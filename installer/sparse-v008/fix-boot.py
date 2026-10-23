from pathlib import Path
import gzip,hashlib,json,subprocess
b=Path('/mnt/nas/apps/ps4-android/installer/sparse-v008');p=Path('/dev/shm/ps4-v008/assets/initramfs.cpio.gz');raw=gzip.decompress(p.read_bytes());off=0;buf=bytearray();script=(b/'standalone-start.sh').read_bytes()
while off<len(raw):
 h=raw[off:off+110];v=[int(h[6+i*8:14+i*8],16) for i in range(13)];name=raw[off+110:off+110+v[11]-1].decode();off=(off+110+v[11]+3)&~3;d=raw[off:off+v[6]];off=(off+v[6]+3)&~3
 if name in ['usr/sbin/cole-android-start','opt/cole-android/autoboot.sh']:d=script
 v[6]=len(d);buf.extend(b'070701'+''.join(f'{x:08x}' for x in v).encode()+name.encode()+b'\0');buf.extend(b'\0'*(-len(buf)%4));buf.extend(d);buf.extend(b'\0'*(-len(buf)%4))
 if name=='TRAILER!!!':break
out=b/'initramfs-diskwait-fixed.cpio.gz';out.write_bytes(gzip.compress(bytes(buf),compresslevel=6,mtime=0));out.chmod(0o600)
p=Path('/home/amber/.local/share/cole-ps4-android');ssh=['ssh','-T','-i',str(p/'id_ed25519'),'-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(p/'known_hosts'),'root@192.168.0.77']
t='/mnt/ps4-user/data/linux/boot/initramfs.cpio.gz'
subprocess.run(ssh+['set -C; cat > '+t+'.diskwait-next'],input=out.read_bytes(),check=True)
h=hashlib.sha256(out.read_bytes()).hexdigest();r=subprocess.check_output(ssh+['sha256sum '+t+'.diskwait-next'],text=True);assert r.split()[0]==h
subprocess.run(ssh+['set -e; test ! -e '+t+'.before-diskwait-v008; mv '+t+' '+t+'.before-diskwait-v008; mv '+t+'.diskwait-next '+t+'; sync'],check=True)
(b/'boot-fixes.json').write_text(json.dumps({'sha256':h,'console_boot_image_updated':True,'fixes':['wait for internal disk','use /usr/sbin/mke2fs and /usr/sbin/e2fsck explicitly','allow reuse of mounted internal filesystem'],'package_v008_contains_these_fixes':False,'public_release_blocked_until_rebuild':True},indent=2)+'\n')
print('Fixed boot image persisted and checksum verified:',h)
