from pathlib import Path
import gzip,hashlib,json,time,tarfile,stat,subprocess,shutil,re
base=Path('/mnt/nas/apps/ps4-android'); work=Path('/home/amber/projects/ps4-android'); build=Path('/dev/shm/ps4-v008'); out=base/'installer/sparse-v008'
raw=gzip.decompress((work/'standard-boot/initramfs.cpio.gz').read_bytes()); entries={}; p=0
while p<len(raw):
 h=raw[p:p+110]; assert h[:6]==b'070701'; v=[int(h[6+i*8:14+i*8],16) for i in range(13)]
 n=raw[p+110:p+110+v[11]-1].decode(); p=(p+110+v[11]+3)&~3; d=raw[p:p+v[6]]; p=(p+v[6]+3)&~3
 if n=='TRAILER!!!':break
 entries[n]=(v,d)
def put(n,d,mode=0o100644):
 parent=Path(n).parent
 if str(parent)!='.' and str(parent) not in entries: put(str(parent),b'',0o40755)
 entries[n]=([len(entries)+1,mode,0,0,1,0,len(d),0,0,0,0,len(n.encode())+1,0],d)
with tarfile.open(work/'internal-tools-runtime.tar') as t:
 for m in t:
  if m.isfile():put(m.name,t.extractfile(m).read(),0o100000|m.mode)
files={'/usr/sbin/mke2fs','/usr/sbin/e2fsck','/usr/sbin/resize2fs','/etc/mke2fs.conf'}
for f in list(files):
 if f.startswith('/usr/sbin'):files.update(re.findall(r'(/[^\s()]+)',subprocess.check_output(['ldd',f],text=True)))
for f in files:put(f.lstrip('/'),Path(f).read_bytes(),0o100000|stat.S_IMODE(Path(f).stat().st_mode))
old=entries['usr/sbin/cole-android-start'][1].decode(); tail=old[old.index("stage 'System and userdata mounted;"):]
setup='''#!/bin/sh
set -eu
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
assets=/opt/cole-android
stage() { echo "[Android setup $(cut -d' ' -f1 /proc/uptime)s] $*"; }
stage 'Waiting for internal PS4 disk'
for attempt in $(seq 1 60); do
 [ ! -b /dev/sda27 ] || break
 sleep 1
done
[ -b /dev/sda27 ] || { stage 'Internal disk did not appear within 60 seconds'; exit 1; }
stage 'Opening internal PS4 storage'
[ -r /key/eap_hdd_key.bin ]
dmesg | grep -qi aeolia
mkdir -p /mnt/ps4-user /mnt/android-share /mnt/android-sfs /mnt/android-lower /mnt/android-persistent /android
if ! grep -q ' /mnt/ps4-user ' /proc/mounts; then
cryptsetup open --type plain --cipher aes-xts-plain64 --key-size 256 --offset 0 --key-file /key/eap_hdd_key.bin /dev/sda27 ps4-android-user
mount -t ufs -o ufstype=ufs2,noatime /dev/mapper/ps4-android-user /mnt/ps4-user
fi
installation=/mnt/ps4-user/app/ps4-android
[ -f "$installation/ready" ] || { stage 'Package setup incomplete'; exit 1; }
grep -q '^PS4ANDROID13-SPARSE-V008$' "$installation/ready"
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
 printf '%s\\n' 'PS4ANDROID-DATA-V1' > "$installation/data-ready.next"
 sync
 mv "$installation/data-ready.next" "$installation/data-ready"
 sync
 stage 'Fresh Android storage created'
fi
mount --bind "$installation" /mnt/android-share
mount -t squashfs -o ro,loop "$installation/system.sfs" /mnt/android-sfs
mount -t ext4 -o ro,loop,noload /mnt/android-sfs/system.img /mnt/android-lower
mkdir -p /run/android-overlay/upper /run/android-overlay/work
mount -t overlay overlay -o lowerdir=/mnt/android-lower,upperdir=/run/android-overlay/upper,workdir=/run/android-overlay/work /android
mount -t ext4 -o loop,noatime "$installation/data.img" /mnt/android-persistent
'''
script=setup+tail
# Management-only network for this private test build. No NFS mounts anywhere.
assert 'mount -t nfs' not in script
subprocess.run(['/bin/busybox','sh','-n'],input=script.encode(),check=True)
(out/'standalone-start.sh').write_text(script)
put('usr/sbin/cole-android-start',script.encode(),0o100755);put('opt/cole-android/autoboot.sh',script.encode(),0o100755)
put('opt/cole-android/graphics-baseline',b'standard-v1-internal-sparse-v008\n')
# Show setup stage output on the TV as well as preserving the log.
init=entries['init'][1].decode().replace("echo 'Cole PS4 Android project: RAM diagnostic boot'","echo 'PS4 Android TV: internal first-install test'").replace("echo 'Internal disks are not mounted. No installer is running.'","echo 'Android storage will be prepared on the internal drive.'")
put('init',init.encode(),0o100755)
buf=bytearray()
for n,(v,d) in list(entries.items())+[('TRAILER!!!',([0]*13,b''))]:
 v=v.copy();v[6]=len(d);v[11]=len(n.encode())+1
 buf.extend(b'070701'+''.join(f'{x:08x}' for x in v).encode()+n.encode()+b'\0');buf.extend(b'\0'*(-len(buf)%4));buf.extend(d);buf.extend(b'\0'*(-len(buf)%4))
(build/'assets/initramfs.cpio.gz').write_bytes(gzip.compress(bytes(buf),compresslevel=6,mtime=0))
for name in ['bzImage','bootargs.txt','vram.txt']:shutil.copy2(work/'standard-boot'/name,build/'assets'/name)
shutil.copy2(base/'downloads/linux-1024mb.elf',build/'assets/linux.elf')
shutil.copy2(work/'exports/libgallium-baseline.so',build/'assets/libgallium-baseline.so')
shutil.copy2(base/'downloads/android-tv13-system.sfs',build/'assets/system.sfs')
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()} for p in (build/'assets').iterdir()}
(out/'assets.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Assets prepared; no userdata image and no NFS boot dependency',flush=True)
print(json.dumps({n:x['bytes'] for n,x in manifest.items()},indent=2))
