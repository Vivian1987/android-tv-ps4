"""Switch the PS4's RAM-only Linux to the verified Android-capable build."""
from pathlib import Path
import hashlib, json, subprocess, time

project = Path(__file__).resolve().parent
private = Path('/home/amber/.local/share/cole-ps4-android')
ssh = ['ssh', '-T', '-i', str(private/'id_ed25519'), '-o', 'StrictHostKeyChecking=yes',
       '-o', 'UserKnownHostsFile='+str(private/'known_hosts'), '-o', 'BatchMode=yes',
       '-o', 'ConnectTimeout=3', 'root@192.168.0.77']
evidence = json.loads((project/'evidence/android-kernel-build.json').read_text())
image = Path(evidence['runtime'])/'arch/x86/boot/bzImage'
assert hashlib.sha256(image.read_bytes()).hexdigest() == evidence['sha256']
result = subprocess.run(ssh+['cat /sys/bus/pci/devices/0000:00:01.0/device'],
                        capture_output=True, text=True, check=True, timeout=6)
assert result.stdout.strip() == '0x9920', 'Unexpected console GPU'
for local, remote in [(image, '/run/cole/kernel-android'),
    (Path('/home/amber/projects/ps4-android/ramboot/initramfs.cpio.gz'), '/run/cole/ramboot-next.cpio.gz')]:
    data = local.read_bytes()
    subprocess.run(ssh+['cat > '+remote], input=data, check=True, timeout=20)
    digest = subprocess.check_output(ssh+['sha256sum '+remote], text=True, timeout=6).split()[0]
    assert digest == hashlib.sha256(data).hexdigest(), 'Transfer checksum mismatch'
    print('Verified '+remote, flush=True)
args = ('panic=0 clocksource=tsc consoleblank=0 net.ifnames=0 radeon.dpm=0 '
        'amdgpu.dpm=0 drm.debug=0 console=tty0 video=HDMI-A-1:1920x1080@60 '
        'rdinit=/init enforcing=0 androidboot.selinux=permissive')
subprocess.run(ssh+['/usr/sbin/kexec -s -l /run/cole/kernel-android '
    '--initrd=/run/cole/ramboot-next.cpio.gz --append="'+args+'"'], check=True, timeout=20)
print('New kernel loaded; executing the transition.', flush=True)
try:
    result = subprocess.run(ssh+['sync\n/usr/sbin/kexec -e'], capture_output=True, text=True, timeout=10)
    print('Transition SSH exit:', result.returncode, flush=True)
except subprocess.TimeoutExpired:
    print('Transition closed or stalled the old SSH session; checking the new boot.', flush=True)
deadline = time.monotonic()+120
while time.monotonic() < deadline:
    try:
        result = subprocess.run(ssh+['uname -r'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and '-cole-android-aeolia' in result.stdout:
            print('New kernel confirmed:', result.stdout.strip(), flush=True)
            (project/'evidence/android-kernel-running.json').write_text(json.dumps({
                'uname': result.stdout.strip(), 'kernel_sha256': evidence['sha256'],
                'transition': 'kexec_file_load then kexec', 'ssh_host_key_verified': True}, indent=2)+'\n')
            break
    except subprocess.TimeoutExpired:
        pass
    time.sleep(2)
else:
    raise SystemExit('No confirmed new-kernel SSH after 120 seconds; inspect console before retrying.')
