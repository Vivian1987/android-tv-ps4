#!/bin/sh
set -eu
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
mount -t proc proc /android/proc
mount -t sysfs sysfs /android/sys
mkdir -p /android/sys/fs/selinux
mount -t selinuxfs selinuxfs /android/sys/fs/selinux
mount -t tmpfs -o mode=0755 tmpfs /android/dev
mkdir -p /android/dev/pts /android/dev/socket /android/dev/binderfs
mount -t devpts -o newinstance,ptmxmode=0666 devpts /android/dev/pts
for entry in 'null 1 3' 'zero 1 5' 'random 1 8' 'urandom 1 9' 'tty 5 0' 'console 5 1' 'kmsg 1 11'; do
    set -- $entry
    mknod -m 666 /android/dev/$1 c $2 $3
done
ln -s pts/ptmx /android/dev/ptmx
mount -t binder binder /android/dev/binderfs
/run/cole/binder-devices /android/dev/binderfs/binder-control
for name in binder hwbinder vndbinder; do
    ln -s binderfs/$name /android/dev/$name
    chmod 666 /android/dev/binderfs/$name
done
if [ -f /mnt/android-persistent/data/system/packages.xml ]; then
    mount --bind /mnt/android-persistent/data /android/data
elif [ -f /run/android-data-preserved/system/packages.xml ]; then
    mount --bind /run/android-data-preserved /android/data
else
    mount -t tmpfs -o size=1536m,mode=0771,uid=1000,gid=1000 tmpfs /android/data
fi
mount -t tmpfs tmpfs /android/apex
mkdir -p /android/linkerconfig /android/metadata /android/mnt /android/debug_ramdisk
mount -t tmpfs tmpfs /android/linkerconfig
# Android remounts its root read-only; these runtime trees must remain writable.
if [ -d /mnt/android-persistent/metadata/vold ]; then
    mount --bind /mnt/android-persistent/metadata /android/metadata
elif [ -d /run/android-metadata-preserved/vold ]; then
    mount --bind /run/android-metadata-preserved /android/metadata
else
    mount -t tmpfs -o mode=0755 tmpfs /android/metadata
fi
for runtime in mnt debug_ramdisk cache; do
    mount -t tmpfs -o mode=0755 tmpfs /android/$runtime
done
mount --bind /run/cole/android-cmdline /android/proc/cmdline
ip link set lo up
/usr/sbin/ip link add dummy0 type dummy
/usr/sbin/ip link set dummy0 up
export ANDROID_ROOT=/system ANDROID_DATA=/data
echo 'Starting Android init in its own PID, mount, IPC, UTS and network namespaces'
exec chroot /android /system/bin/init selinux_setup
