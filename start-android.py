"""Attach the read-only TV13 image and launch an isolated Android bring-up."""
from pathlib import Path
import subprocess, urllib.request, email.utils, json, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--graphics-probe', action='store_true', help='Keep Android alive for graphics diagnostics after BPF failure')
options = parser.parse_args()

source = Path(__file__).resolve().parent
private = Path('/home/amber/.local/share/cole-ps4-android')
ssh = ['ssh', '-T', '-i', str(private/'id_ed25519'), '-o', 'StrictHostKeyChecking=yes',
       '-o', 'UserKnownHostsFile='+str(private/'known_hosts'), '-o', 'BatchMode=yes',
       '-o', 'ConnectTimeout=5', 'root@192.168.0.77']

def run(script):
    subprocess.run(ssh+['/bin/sh', '-s'], input=script.encode(), check=True, timeout=30)

# PS4's Linux RTC stub starts at 1970; Ember's own clock is known to be wrong.
# Use an HTTPS server's Date header rather than copying Ember's wall clock.
with urllib.request.urlopen('https://www.google.com/generate_204', timeout=10) as response:
    timestamp = int(email.utils.parsedate_to_datetime(response.headers['Date']).timestamp())
run(f'date -u -s @{timestamp}\n')

run('''set -eu
uname -a
grep -q selinuxfs /proc/filesystems
mkdir -p /mnt/android-share /mnt/android-lower /mnt/android-data-share /mnt/android-persistent /android
if ! grep -q ' /mnt/android-share ' /proc/mounts; then
  mount -t nfs -o ro,nolock,vers=3,tcp,mountproto=tcp,mountport=20048 \\
    192.168.0.250:/srv/cole-ps4-android /mnt/android-share
fi
if ! grep -q ' /mnt/android-lower ' /proc/mounts; then
  mount -t ext4 -o ro,loop,noload /mnt/android-share/system.img /mnt/android-lower
fi
mkdir -p /run/android-overlay/upper /run/android-overlay/work
if ! grep -q ' /android ' /proc/mounts; then
  mount -t overlay overlay \\
    -o lowerdir=/mnt/android-lower,upperdir=/run/android-overlay/upper,workdir=/run/android-overlay/work /android
fi
# Persistent ext4 image is mounted by Linux once and bound into Android.
if ! grep -q ' /mnt/android-data-share ' /proc/mounts; then
  mount -t nfs -o rw,nolock,vers=3,tcp,mountproto=tcp,mountport=20048 \\
    192.168.0.250:/srv/cole-ps4-android-data /mnt/android-data-share
fi
if ! grep -q ' /mnt/android-persistent ' /proc/mounts; then
  mount -t ext4 -o loop,noatime /mnt/android-data-share/userdata.img /mnt/android-persistent
fi
if ps -o args | grep -q '^/system/bin/init '; then
  echo 'Android init is already running; refusing a duplicate.'
  exit 1
fi
''')
# Use the pinned Android13 NDK translator in the RAM overlay, retaining base image.
translator = Path('/home/amber/projects/ps4-android/ndk-translation.tar.gz')
if translator.exists():
    subprocess.run(ssh+['cat > /run/cole/ndk-translation.tar.gz'],
                   input=translator.read_bytes(), check=True, timeout=20)
    run('for p in /android/system/lib/arm /android/system/lib64/arm64; do if [ -L "$p" ]; then rm "$p"; fi; mkdir -p "$p"; done\ntar -xzf /run/cole/ndk-translation.tar.gz -C /android/system\n')
    for original, target in [
        (source/'reference/android-system-build.prop', '/android/system/build.prop'),
        (source/'reference/android-vendor-build.prop', '/android/system/vendor/build.prop'),
        (source/'reference/android-product-build.prop', '/android/system/product/etc/build.prop')]:
        props = original.read_text().replace('ro.dalvik.vm.native.bridge=libhoudini.so',
                                             'ro.dalvik.vm.native.bridge=libndk_translation.so')
        subprocess.run(ssh+['cat > '+target], input=props.encode(), check=True, timeout=8)
controllers = subprocess.check_output(ssh+['cat /proc/cgroups'], text=True, timeout=8)
available = {line.split()[0] for line in controllers.splitlines() if line and not line.startswith('#')}
cgroup_config = json.loads(Path('/android-system/system/etc/cgroups.json').read_text())
missing = [item['Controller'] for item in cgroup_config['Cgroups'] if item['Controller'] not in available]
if missing:
    for item in cgroup_config['Cgroups']:
        if item['Controller'] in missing:
            item['Optional'] = True
    subprocess.run(ssh+['cat > /android/system/etc/cgroups.json'],
                   input=(json.dumps(cgroup_config, indent=2)+'\n').encode(), check=True, timeout=8)
    print('Temporary bring-up override: unavailable legacy controllers optional:', missing, flush=True)
subprocess.run(ssh+['cat > /android/system/vendor/brtdtv/resolution.sh'],
               input=(source/'ramboot/resolution.sh').read_bytes(), check=True, timeout=8)
subprocess.run(ssh+['cat > /android/system/etc/init/cole-ps4.rc'],
               input=b'on early-init\n    setprop ro.vndk.version 33\n    setprop sys.use_memfd true\n    export AMD_DEBUG notiling\n',
               check=True, timeout=8)
# Pinned minigbm composer: cache by allocation id, not reusable handle pointer.
composer = source/'downloads/composer-drmfb-allocation-key'
import hashlib
assert hashlib.sha256(composer.read_bytes()).hexdigest() == '4a00209eb9a02f81e959a7d64dd3ad6336b1ee663a59a9a3c7f9f5af0270208a'
subprocess.run(ssh+['cat > /android/system/vendor/bin/hw/composer-cole-new'],
               input=composer.read_bytes(), check=True, timeout=8)
run('chmod 755 /android/system/vendor/bin/hw/composer-cole-new; mv /android/system/vendor/bin/hw/composer-cole-new /android/system/vendor/bin/hw/android.hardware.graphics.composer@2.1-drmfb-service\n')
# Keep allocation on the render node so the HDMI composer owns DRM master.
hal_init = Path('/android-system/system/etc/init.sh').read_text().replace('set_property persist.ffmpeg-codec2.pixel_format YUV_420', 'set_property persist.ffmpeg-codec2.pixel_format RGBX_8888')
hal_init = hal_init.replace('function init_hal_gralloc()\n{',
    'function init_hal_gralloc()\n{\n    set_property gralloc.gbm.device /dev/dri/renderD128')
hal_init = hal_init.replace('function init_hal_audio()\n{',
    'function init_hal_audio()\n{\n    set_property hal.audio.out pcmC0D3p\n    set_property hal.audio.out.hdmi pcmC0D3p\n    set_property hal.audio.primary.hdmi 1')
subprocess.run(ssh+['cat > /android/system/etc/init.sh'],
               input=hal_init.encode(), check=True, timeout=8)
# This image defaults to ashmem, removed from modern Linux; use verified memfd.
main_init = Path('/android-system/system/etc/init/hw/init.rc').read_text()
main_init = main_init.replace('setprop sys.use_memfd false', 'setprop sys.use_memfd true')
subprocess.run(ssh+['cat > /android/system/etc/init/hw/init.rc'],
               input=main_init.encode(), check=True, timeout=8)
# RAM-only bring-up: never expose the PS4 internal USB-SATA disk to vold.
subprocess.run(ssh+['cat > /android/fstab.mustang'],
               input=b'none /cache tmpfs noatime,nosuid,nodev,mode=0770,uid=1000,gid=2001 defaults\n',
               check=True, timeout=8)
original_bpf = Path('/android-system/system/etc/init/bpfloader.rc').read_text()
if options.graphics_probe:
    bpf_rc = '\n'.join(line for line in original_bpf.splitlines()
                       if not line.strip().startswith('reboot_on_failure '))+'\n'
else:
    bpf_rc = original_bpf
subprocess.run(ssh+['cat > /android/system/etc/init/bpfloader.rc'],
               input=bpf_rc.encode(), check=True, timeout=8)
for local, remote in [(source/'downloads/xt_quota2-aeolia-v1.ko', '/run/cole/xt_quota2.ko'),
    (source/'ramboot/android-child.sh', '/run/cole/android-child.sh'),
    (Path('/home/amber/projects/ps4-android/binder-devices'), '/run/cole/binder-devices')]:
    subprocess.run(ssh+['cat > '+remote], input=local.read_bytes(), check=True, timeout=10)
run('''set -eu
chmod 755 /run/cole/android-child.sh /run/cole/binder-devices
if ! grep -q '^xt_quota2 ' /proc/modules; then
    insmod /run/cole/xt_quota2.ko
fi
printf '%s\\n' 'androidboot.hardware=mustang androidboot.selinux=permissive androidboot.fake_battery=1 androidboot.enable_console=1 androidboot.serialno=coleps4 HWC=default HWC_IS_DRMFB=1 GRALLOC=gbm' > /run/cole/android-cmdline
echo on > /proc/sys/kernel/printk_devkmsg
echo 1 > /proc/sys/kernel/printk
trap '' HUP
unshare -m -p -u -i -n -f --propagation private \\
  /bin/sh /run/cole/android-child.sh </dev/null >/run/cole/android.log 2>&1 &
echo $! > /run/cole/android-launcher.pid
sleep 3
cat /run/cole/android.log
dmesg | tail -40
''')
run('''set -eu
launcher=$(cat /run/cole/android-launcher.pid)
child=$(ps -o pid,ppid | awk -v parent="$launcher" '$2 == parent && $1 > 1 {print $1; exit}')
if [ -z "$child" ]; then
    echo 'Android init exited; no network interface will be moved.'
    exit 1
fi
# A separate MAC address gives Android ordinary DHCP while management retains .77.
/usr/sbin/ip link add link eth0 name atv0 type macvlan mode bridge
/usr/sbin/ip link set atv0 netns "$child"
nsenter -t "$child" -n /usr/sbin/ip link set atv0 name eth0
nsenter -t "$child" -n /usr/sbin/ip link set eth0 up
# Move the real Marvell radio into Android; SSH stays on the physical eth0.
if /usr/sbin/iw phy phy0 info >/dev/null 2>&1; then
    radio=$(/usr/sbin/iw dev | awk '$1 == "Interface" {print $2; exit}')
    /usr/sbin/ip link set "$radio" down
    /usr/sbin/iw phy phy0 set netns "$child"
    if [ "$radio" != wlan0 ]; then
        nsenter -t "$child" -n /usr/sbin/ip link set "$radio" name wlan0
    fi
    nsenter -t "$child" -n /usr/sbin/ip link set wlan0 up
fi
echo "Android network attached to namespace owned by PID $child"
''')
if options.graphics_probe:
    run('''set -eu
launcher=$(cat /run/cole/android-launcher.pid)
child=$(ps -o pid,ppid | awk -v parent="$launcher" '$2 == parent && $1 > 1 {print $1; exit}')
test -n "$child"
echo 1 > /proc/sys/kernel/printk
nsenter -t "$child" -m -p -n chroot /android /system/bin/setprop ctl.start surfaceflinger
nsenter -t "$child" -m -p -n chroot /android /system/bin/setprop ctl.start bootanim
echo "Graphics probe requested in Android PID $child; full boot still requires working BPF."
''')
