#!/bin/sh
set -eu
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
assets=/opt/androidtv-ps4
stage() {
 message="[Android setup $(cut -d' ' -f1 /proc/uptime)s] $*"
 printf '%s\n' "$message" >> /run/androidtv-ps4/progress.log
 # A new Android framebuffer ends all console writes from this script.
 if [ ! -f /run/androidtv-ps4/display-ready ]; then printf '%s\n' "$message"; fi
}
trap 'status=$?; if [ "$status" -ne 0 ]; then stage "SETUP FAILED (status $status); logs retained, data preserved"; fi' EXIT
touch /run/androidtv-ps4/bootstrap-active
stage 'Waiting for internal PS4 disk'
for attempt in $(seq 1 60); do
 [ ! -b /dev/sda27 ] || break
 if [ "$((attempt % 5))" = 0 ]; then stage "Still waiting for internal disk ($attempt seconds)"; fi
 sleep 1
done
[ -b /dev/sda27 ] || { stage 'Internal disk did not appear within 60 seconds'; exit 1; }
stage 'Opening internal PS4 storage (disk encryption and filesystem)'
[ -r /key/eap_hdd_key.bin ]
# Record the southbridge for reports; Belize and Baikal consoles are allowed to try.
southbridge=$(dmesg | grep -ioE 'aeolia|belize|baikal' | head -1 || true)
stage "Southbridge: ${southbridge:-unknown}"
mkdir -p /mnt/ps4-user /mnt/android-share /mnt/android-sfs /mnt/android-lower /mnt/android-persistent /android
if ! grep -q ' /mnt/ps4-user ' /proc/mounts; then
cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 --offset 0 --key-file /key/eap_hdd_key.bin /dev/sda27 ps4-android-user
mount -t ufs -o ufstype=ufs2,noatime /dev/mapper/ps4-android-user /mnt/ps4-user
fi
installation=/mnt/ps4-user/app/ps4-android
# Rotate only the previous local boot reports.
for report in boot.log kernel.log android-boot.log android-stages.log; do
 [ ! -f "$installation/$report" ] || mv "$installation/$report" "$installation/$report.previous"
done
# Persist startup output locally for diagnosis without remote access.
save_logs() {
 status=$?
 [ "$status" = 0 ] || stage "SETUP FAILED (status $status); data preserved"
 cp /run/androidtv-ps4/one-shot.log "$installation/boot.log" 2>/dev/null || true
 dmesg > "$installation/kernel.log" 2>/dev/null || true
 cp /run/androidtv-ps4/progress.log "$installation/boot-progress.log" 2>/dev/null || true
 cp /run/androidtv-ps4/display-ready "$installation/display-ready.log" 2>/dev/null || true
 cp /run/androidtv-ps4/display-watch.log "$installation/display-watch.log" 2>/dev/null || true
 sync
 rm -f /run/androidtv-ps4/bootstrap-active
}
trap save_logs EXIT
[ -f "$installation/ready" ] || { stage 'Package setup incomplete'; exit 1; }
grep -q '^PS4ANDROID13-SPARSE-V015$' "$installation/ready"
capacity=$(cat "$installation/data-gib.txt")
case "$capacity" in 32|64|128) ;; *) stage 'Invalid data capacity'; exit 1;; esac
# Keep spare physical disk space for both operating systems.
available=$(df -Pk "$installation" | tail -1 | awk '{print $4}')
[ "$available" -gt 2097152 ] || { stage 'Less than 2 GiB physical storage remains'; exit 1; }
if [ ! -f "$installation/data-ready" ]; then
 [ ! -e "$installation/data.img" ] || { stage 'Uncommitted data image preserved; recovery needed'; exit 1; }
 [ ! -e "$installation/data.img.part" ] || { stage 'Interrupted creation preserved; recovery needed'; exit 1; }
 stage "Creating fresh $capacity GiB Android storage"
 truncate -s "$((capacity * 1073741824))" "$installation/data.img.part"
 /usr/sbin/mke2fs -t ext4 -F -m 0 -E nodiscard,lazy_itable_init=1,lazy_journal_init=1 "$installation/data.img.part"
 /usr/sbin/e2fsck -fn "$installation/data.img.part"
 sync
 mv "$installation/data.img.part" "$installation/data.img"
 printf '%s\n' 'PS4ANDROID-DATA-V1' > "$installation/data-ready.next"
 sync
 mv "$installation/data-ready.next" "$installation/data-ready"
 sync
 stage 'Fresh Android storage created'
fi
mount --bind "$installation" /mnt/android-share
stage 'Mounting compressed Android system from internal storage'
mount -t squashfs -o ro,loop "$installation/system.sfs" /mnt/android-sfs
mount -t ext4 -o ro,loop,noload /mnt/android-sfs/system.img /mnt/android-lower
mkdir -p /run/android-overlay/upper /run/android-overlay/work
mount -t overlay overlay -o lowerdir=/mnt/android-lower,upperdir=/run/android-overlay/upper,workdir=/run/android-overlay/work /android
[ "$(stat -c %s "$installation/data.img")" = "$((capacity * 1073741824))" ] || { stage 'Data image size does not match selected edition; data preserved'; exit 1; }
stage 'Mounting Android app storage'
mount -t ext4 -o loop,noatime "$installation/data.img" /mnt/android-persistent
stage 'System and userdata mounted; preparing graphics and media'
for p in /android/system/lib/arm /android/system/lib64/arm64; do
 [ ! -L "$p" ] || rm "$p"
 mkdir -p "$p"
done
stage 'Preparing app compatibility libraries'
tar -xzf "$installation/ndk-translation.tar.gz" -C /android/system
cp "$assets/system-build.prop" /android/system/build.prop
cp "$assets/vendor-build.prop" /android/system/vendor/build.prop
cp "$assets/init.android_x86_64.rc" /android/system/vendor/etc/init/init.android_x86_64.rc
cp "$assets/product-build.prop" /android/system/product/etc/build.prop
cp "$assets/init.sh" /android/system/etc/init.sh
cp "$assets/init.rc" /android/system/etc/init/hw/init.rc
cp "$assets/androidtv-ps4.rc" /android/system/etc/init/androidtv-ps4.rc
cp "$assets/androidtv-logging.rc" /android/system/etc/init/androidtv-logging.rc
cp "$assets/device-name.rc" /android/system/etc/init/androidtv-device-name.rc
cp "$assets/device-name.sh" /android/system/bin/androidtv-device-name.sh
chmod 644 /android/system/etc/init/androidtv-device-name.rc /android/system/bin/androidtv-device-name.sh
mkdir -p /android/system/vendor/etc/seccomp_policy
cp "$assets/mediaextractor.policy" /android/system/vendor/etc/seccomp_policy/mediaextractor.policy
chmod 644 /android/system/etc/init/androidtv-logging.rc /android/system/vendor/etc/seccomp_policy/mediaextractor.policy
# Keep native APKs on internal storage, outside the small initramfs.
# Signed APKs, splits and native libraries have their normal Android layout.
# The read-only app filesystem stays on disk, outside the RAM overlay.
mkdir -p /mnt/android-bundled-apps
mount -t squashfs -o ro,loop "$installation/bundled-apps.sfs" /mnt/android-bundled-apps
while read -r app; do
 target="/android/system/app/atv-$app"
 # Replace the base ARM service in its existing privileged product location.
 # Hiding that entire directory prevents duplicate packages and stale libraries.
 [ "$app" != gms ] || target=/android/system/product/priv-app/GooglePlayServices
 mkdir -p "$target"
 mount --bind "/mnt/android-bundled-apps/$app" "$target"
done < "$assets/bundled-apps.txt"
cp "$assets/bootanimation.zip" /android/system/product/media/bootanimation.zip
chmod 644 /android/system/product/media/bootanimation.zip
mkdir -p /android/system/app/AtvConnectivity
cp "$assets/AtvConnectivity.apk" /android/system/app/AtvConnectivity/AtvConnectivity.apk
chmod 755 /android/system/app/AtvConnectivity
chmod 644 /android/system/app/AtvConnectivity/AtvConnectivity.apk
cp "$assets/bpfloader.rc" /android/system/etc/init/bpfloader.rc
cp "$assets/resolution.sh" /android/system/vendor/brtdtv/resolution.sh
cp "$assets/gralloc-gbm-yv12-stride.so" /android/system/vendor/lib64/hw/gralloc.gbm.so
cp "$assets/composer" /android/system/vendor/bin/hw/android.hardware.graphics.composer@2.1-drmfb-service
chmod 755 /android/system/vendor/bin/hw/android.hardware.graphics.composer@2.1-drmfb-service
cp "$assets/libatv-display-modes.so" /android/system/vendor/lib64/libatv-display-modes.so
chmod 644 /android/system/vendor/lib64/libatv-display-modes.so
cp "$assets/hwcomposer.rc" /android/system/vendor/etc/init/android.hardware.graphics.composer@2.1-drmfb-service.rc
# Bluetooth owns HCI through its HAL; Wi-Fi and Ethernet remain in Android.
cp "$assets/bluetooth.rc" /android/system/vendor/etc/init/android.hardware.bluetooth@1.1-service.vbt.rc
cp "$assets/bluetooth-scheduling.rc" /android/system/etc/init/androidtv-bluetooth.rc
chmod 644 /android/system/vendor/etc/init/android.hardware.bluetooth@1.1-service.vbt.rc /android/system/etc/init/androidtv-bluetooth.rc
# Scope the old event-mask workaround to the verified Marvell SD8797 device.
if grep -q '^SDIO_ID=02DF:912A$' /sys/class/bluetooth/hci0/device/uevent 2>/dev/null; then
 cp "$assets/libatv-bluetooth-sd8797.so" /android/system/vendor/lib64/libatv-bluetooth-sd8797.so
 chmod 644 /android/system/vendor/lib64/libatv-bluetooth-sd8797.so
 printf '%s\n' '    setenv LD_PRELOAD /vendor/lib64/libatv-bluetooth-sd8797.so' >> /android/system/vendor/etc/init/android.hardware.bluetooth@1.1-service.vbt.rc
fi
chmod 644 /android/system/vendor/etc/init/android.hardware.graphics.composer@2.1-drmfb-service.rc
printf '%s\n' 'none /cache tmpfs noatime,nosuid,nodev,mode=0770,uid=1000,gid=2001 defaults' > /android/fstab.mustang
cp "$assets/android-child.sh" /run/androidtv-ps4/android-child.sh
cp "$assets/binder-devices" /run/androidtv-ps4/binder-devices
cp "$assets/xt_quota2.ko" /run/androidtv-ps4/xt_quota2.ko
cp /mnt/android-share/libgallium-baseline.so /android/system/vendor/lib64/dri/libgallium_dri.so
echo 'ca0b4228ede6a6763568e6cafd4efc472f7d31eaae7622b03ad8d3dd3c7e545f  /android/system/vendor/lib64/dri/libgallium_dri.so' | sha256sum -c -
# The native x86 YouTube/Kodi processes load the 32-bit Mesa driver.
# Apply the same Liverpool raster correction to the exact pinned base library.
# OverlayFS copies up this file; the distributed Android system stays untouched.
mesa32=/android/system/vendor/lib/dri/libgallium_dri.so
mesa32_sha=$(sha256sum "$mesa32" | cut -d ' ' -f 1)
case "$mesa32_sha" in
 eb4db495721ec36dfa4d0cdb6378c845bd756c77748fae9aed14eacaf2389f1e)
  printf '\032\026\000\052' | dd of="$mesa32" bs=1 seek=23111413 conv=notrunc 2>/dev/null
  ;;
 fbac4a587e486de0e4f6f6b02dbe3c9495371735ca3c35e5e3cfbcc753d85c2c) ;;
 *) stage 'Unsupported 32-bit graphics library'; exit 1 ;;
esac
echo 'fbac4a587e486de0e4f6f6b02dbe3c9495371735ca3c35e5e3cfbcc753d85c2c  /android/system/vendor/lib/dri/libgallium_dri.so' | sha256sum -c -
sh "$assets/controller-home.sh"
echo '6803c4d592e97e6252d0dffd25a6a332db1d5f632cc958f0ec7dd6d89cff9052  /android/system/vendor/lib64/hw/gralloc.gbm.so' | sha256sum -c -
stage 'Launching Android init with verified graphics baseline (standard-v1)'
set -eu
chmod 755 /run/androidtv-ps4/android-child.sh /run/androidtv-ps4/binder-devices
if ! grep -q '^xt_quota2 ' /proc/modules; then
    insmod /run/androidtv-ps4/xt_quota2.ko
fi
# Per-install identifier; no developer identity or fabricated hardware serial.
if [ ! -s "$installation/device-id" ]; then
 od -An -N8 -tx1 /dev/urandom | tr -d ' \n' > "$installation/device-id"
 sync
fi
serial=$(cat "$installation/device-id")
printf '%s\n' "androidboot.hardware=mustang androidboot.selinux=permissive androidboot.fake_battery=1 androidboot.enable_console=0 androidboot.serialno=ps4${serial} HWC=default HWC_IS_DRMFB=1 GRALLOC=gbm" > /run/androidtv-ps4/android-cmdline
echo on > /proc/sys/kernel/printk_devkmsg
echo 7 > /proc/sys/kernel/printk
trap '' HUP
stage 'Starting Android graphics at up to 60 Hz; waiting for its first display frame'
if [ ! -f /mnt/android-persistent/data/system/packages.xml ]; then
 stage 'First start: Android must prepare its bundled apps before setup opens'
fi
/usr/sbin/androidtv-display-ready </dev/null >/run/androidtv-ps4/display-watch.log 2>&1 &
watcher=$!
while [ ! -f /run/androidtv-ps4/display-watch-ready ]; do
 kill -0 "$watcher" 2>/dev/null || { stage 'Display observer unavailable; startup logs remain enabled'; break; }
 sleep 0.05
done
touch /run/androidtv-ps4/allow-console-power
# Retain only the host network namespace for the HCI HAL.
# No host address, remote server, credentials, or external boot dependency.
touch /run/androidtv-ps4/host-netns
mount --bind /proc/self/ns/net /run/androidtv-ps4/host-netns
/usr/sbin/android-supervisor -- /bin/sh /run/androidtv-ps4/android-child.sh </dev/null >/run/androidtv-ps4/android.log 2>&1 &
echo $! > /run/androidtv-ps4/android-supervisor.pid
for attempt in $(seq 1 50); do
 [ ! -s /run/androidtv-ps4/android-init.pid ] || break
 sleep 0.1
done
child=$(cat /run/androidtv-ps4/android-init.pid 2>/dev/null || true)
if [ -z "$child" ]; then
    echo 'Android init exited; no network interface will be moved.'
    exit 1
fi
# Android owns its DHCP configuration; the host has no management address.
# A console without a recognised Ethernet port still boots, just without it.
if [ -e /sys/class/net/eth0/address ]; then
 /usr/sbin/ip link set eth0 up
 hwmac=$(cat /sys/class/net/eth0/address)
 /usr/sbin/ip link add link eth0 name atv0 address "02${hwmac#??}" type macvlan mode bridge
 /usr/sbin/ip link set atv0 netns "$child"
 nsenter -t "$child" -n /usr/sbin/ip link set atv0 name eth0
 nsenter -t "$child" -n /usr/sbin/ip link set eth0 up
else
 stage 'No Ethernet interface found; continuing without Ethernet'
fi
# Move the real Marvell radio into Android.
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

stage 'Android init launched; diagnostics continue in android-stages.log'
# These logs are created on this console, never included in the release package.
# Android init owns the rotating collector in /data/misc/logd; it survives setup.
for attempt in $(seq 1 120); do
 if [ -f /run/androidtv-ps4/power-request ]; then exit 0; fi
 now=$(cut -d' ' -f1 /proc/uptime)
 props=$(timeout 3 nsenter -t "$child" -m -p -n chroot /android /system/bin/getprop 2>/dev/null || true)
 property() { printf '%s\n' "$props" | sed -n "s/^\[$1\]: \[\(.*\)\]$/\1/p"; }
 if [ "$(property init.svc.bootanim)" = running ] && [ ! -f /run/androidtv-ps4/animation-captured ]; then
  touch /run/androidtv-ps4/animation-captured
  ( timeout 5 nsenter -t "$child" -m -p -n chroot /android /system/bin/dumpsys SurfaceFlinger > "$installation/animation-display.log" 2>&1 || true ) &
 fi
 if [ ! -f /run/androidtv-ps4/display-ready ]; then
  stage "Android startup: graphics=$(property init.svc.surfaceflinger) animation=$(property init.svc.bootanim) apps=$(property init.svc.zygote); waiting for a display frame"
 fi
 { echo "[$now seconds]"; printf '%s\n' "$props" | grep -E '^\[(sys.boot_completed|init.svc.(zygote|zygote_secondary|surfaceflinger|bootanim|adbd)|service.bootanim.exit|sys.user.0.ce_available)\]' || true; } >> "$installation/android-stages.log"
 if printf '%s\n' "$props" | grep -q '^\[sys.boot_completed\]: \[1\]'; then
  echo "[$now seconds] Android boot complete" >> "$installation/android-stages.log"
  echo "$child" > /run/androidtv-ps4/android.pid
  exit 0
 fi
 sleep 2
done
stage 'Android startup has not completed. Logs are saved; restarting returns to PS4.'
echo 'Android boot timeout; check Android /data/misc/logd and android-stages.log' >> "$installation/android-stages.log"
exit 1
