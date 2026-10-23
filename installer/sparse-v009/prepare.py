from pathlib import Path
import shutil,os,gzip,hashlib,json,subprocess
root=Path('/mnt/nas/apps/ps4-android/installer');old=root/'sparse-v008';new=root/'sparse-v009';new.mkdir(exist_ok=True)
b=Path('/dev/shm/ps4-v009');(b/'assets').mkdir(parents=True,exist_ok=True)
shutil.copytree(old/'source',new/'source',dirs_exist_ok=True)
for n in ['build.py','package.py','image-metadata.h']:
 text=(old/n).read_text().replace('v008','v009').replace('V008','V009').replace("'0.08'","'0.09'")
 (new/n).write_text(text)
shutil.copy2(new/'image-metadata.h',b/'image-metadata.h')
p=new/'source/install-prebuilt.c';s=p.read_text().replace('v008','v009').replace('V008','V009');p.write_text(s)
for p in Path('/dev/shm/ps4-v008/assets').iterdir():
 if p.name=='initramfs.cpio.gz':continue
 dest=b/'assets'/p.name
 if not dest.exists():os.link(p,dest)
script=(old/'standalone-start.sh').read_text().replace('V008','V009')
script=script.replace("stage 'Waiting for internal PS4 disk'", "trap 'status=$?; if [ \"$status\" -ne 0 ]; then stage \"SETUP FAILED (status $status); logs retained, data preserved\"; fi' EXIT\nstage 'Waiting for internal PS4 disk'")
script=script.replace(' [ ! -b /dev/sda27 ] || break\n sleep 1',' [ ! -b /dev/sda27 ] || break\n if [ "$((attempt % 5))" = 0 ]; then stage "Still waiting for internal disk ($attempt seconds)"; fi\n sleep 1')
(new/'standalone-start.sh').write_text(script)
subprocess.run(['/bin/busybox','sh','-n'],input=script.encode(),check=True)
raw=gzip.decompress((old/'initramfs-diskwait-fixed.cpio.gz').read_bytes());pos=0;buf=bytearray();entries={}
while pos<len(raw):
 h=raw[pos:pos+110];v=[int(h[6+i*8:14+i*8],16) for i in range(13)];name=raw[pos+110:pos+110+v[11]-1].decode();pos=(pos+110+v[11]+3)&~3;d=raw[pos:pos+v[6]];pos=(pos+v[6]+3)&~3
 if name in ['usr/sbin/cole-android-start','opt/cole-android/autoboot.sh']:d=script.encode()
 if name=='opt/cole-android/graphics-baseline':d=b'standard-v1-internal-sparse-v009\n'
 if name=='opt/cole-android/composer':d=Path('/mnt/nas/apps/ps4-android/downloads/composer-format-recovery').read_bytes()
 entries[name]=d;v[6]=len(d);buf.extend(b'070701'+''.join(f'{x:08x}' for x in v).encode()+name.encode()+b'\0');buf.extend(b'\0'*(-len(buf)%4));buf.extend(d);buf.extend(b'\0'*(-len(buf)%4))
 if name=='TRAILER!!!':break
for n in ['usr/sbin/mke2fs','usr/sbin/e2fsck']:assert entries[n][:4]==b'\x7fELF',n
assert '/usr/sbin/mke2fs -t ext4' in script and '[ -b /dev/sda27 ]' in script
assert script.index("stage 'Waiting for internal PS4 disk'")<script.index('cryptsetup open')
assert 'mount -t nfs' not in script
assert hashlib.sha256(entries['opt/cole-android/gralloc-gbm-yv12-stride.so']).hexdigest()=='d0132e6968085c418492b64053b4b1a7df78aca09fd9bf2c32eb8e79555d22ab'
blob=gzip.compress(bytes(buf),compresslevel=6,mtime=0);(b/'assets/initramfs.cpio.gz').write_bytes(blob);(new/'initramfs.cpio.gz').write_bytes(blob);(new/'initramfs.cpio.gz').chmod(0o600)
(new/'preflight.json').write_text(json.dumps({'version':'0.09','shell_syntax':'passed','disk_wait_before_cryptsetup':True,'formatter_absolute_path':True,'formatter_and_checker_are_elf':True,'graphics_checksum_verified':True,'no_nfs_mounts':True,'initramfs_sha256':hashlib.sha256(blob).hexdigest(),'first_install_console_test':'pending'},indent=2)+'\n')
print('v009 boot image and installer sources ready')
