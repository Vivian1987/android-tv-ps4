from pathlib import Path
import shutil,os,gzip,hashlib,json,subprocess
root=Path('/mnt/nas/apps/ps4-android/installer');old=root/'sparse-v009';new=root/'sparse-v010';new.mkdir(exist_ok=True);b=Path('/dev/shm/ps4-v010');(b/'assets').mkdir(parents=True,exist_ok=True)
shutil.copytree(old/'source',new/'source',dirs_exist_ok=True)
for n in ['build.py','package.py','image-metadata.h','upload.py']:
 (new/n).write_text((old/n).read_text().replace('v009','v010').replace('V009','V010').replace("'0.09'","'0.10'"))
p=new/'source/install-prebuilt.c';p.write_text(p.read_text().replace('v009','v010').replace('V009','V010'))
shutil.copy2(new/'image-metadata.h',b/'image-metadata.h')
for p in Path('/dev/shm/ps4-v009/assets').iterdir():
 if p.name!='initramfs.cpio.gz':os.link(p,b/'assets'/p.name)
script=(old/'standalone-start.sh').read_text().replace('V009','V010')
(new/'standalone-start.sh').write_text(script);subprocess.run(['/bin/busybox','sh','-n'],input=script.encode(),check=True)
raw=gzip.decompress((old/'initramfs-format-recovery.cpio.gz').read_bytes());pos=0;buf=bytearray();entries={}
while pos<len(raw):
 h=raw[pos:pos+110];v=[int(h[6+i*8:14+i*8],16) for i in range(13)];n=raw[pos+110:pos+110+v[11]-1].decode();pos=(pos+110+v[11]+3)&~3;d=raw[pos:pos+v[6]];pos=(pos+v[6]+3)&~3
 if n in ['usr/sbin/cole-android-start','opt/cole-android/autoboot.sh']:d=script.encode()
 if n=='opt/cole-android/graphics-baseline':d=b'standard-v1-internal-sparse-v010\n'
 entries[n]=d;v[6]=len(d);buf.extend(b'070701'+''.join(f'{x:08x}' for x in v).encode()+n.encode()+b'\0');buf.extend(b'\0'*(-len(buf)%4));buf.extend(d);buf.extend(b'\0'*(-len(buf)%4))
 if n=='TRAILER!!!':break
assert hashlib.sha256(entries['opt/cole-android/composer']).hexdigest()=='3039510ce6a16777904155f62c21b110d3d02bde0a448af6dec96a814e3a28a2'
assert hashlib.sha256(entries['opt/cole-android/gralloc-gbm-yv12-stride.so']).hexdigest()=='d0132e6968085c418492b64053b4b1a7df78aca09fd9bf2c32eb8e79555d22ab'
assert '/usr/sbin/mke2fs -t ext4' in script and script.index('Waiting for internal PS4 disk')<script.index('cryptsetup open')
assert 'mount -t nfs' not in script
for n in ['usr/sbin/mke2fs','usr/sbin/e2fsck']:assert entries[n][:4]==b'\x7fELF'
blob=gzip.compress(bytes(buf),compresslevel=6,mtime=0);(b/'assets/initramfs.cpio.gz').write_bytes(blob);(new/'initramfs.cpio.gz').write_bytes(blob);(new/'initramfs.cpio.gz').chmod(0o600)
(new/'preflight.json').write_text(json.dumps({'version':'0.10','shell_syntax':'passed','disk_wait':True,'absolute_formatter_paths':True,'formatter_elf_verified':True,'patched_composer_verified':True,'patched_gralloc_verified':True,'no_nfs_mounts':True,'initramfs_sha256':hashlib.sha256(blob).hexdigest(),'console_test':'pending'},indent=2)+'\n')
print('v010 preflight passed')
