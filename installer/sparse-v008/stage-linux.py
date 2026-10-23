from pathlib import Path
import subprocess,json,hashlib,time
b=Path('/mnt/nas/apps/ps4-android/installer/sparse-v008');m=json.loads((b/'manifest.json').read_text());p=Path('/home/amber/.local/share/cole-ps4-android')
ssh=['ssh','-T','-i',str(p/'id_ed25519'),'-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(p/'known_hosts'),'root@192.168.0.77']
prep='''set -e
umount /mnt/ps4-release-stage
rt=/run/storage-probe
crypt() { "$rt/lib64/ld-linux-x86-64.so.2" --library-path "$rt/lib/x86_64-linux-gnu" "$rt/usr/sbin/cryptsetup" "$@"; }
crypt close ps4-release-stage
crypt open --type plain --cipher aes-xts-plain64 --key-size 256 --offset 0 --key-file /key/eap_hdd_key.bin /dev/sda27 ps4-release-stage
mount -t ufs -o rw,ufstype=ufs2,noatime /dev/mapper/ps4-release-stage /mnt/ps4-release-stage
[ ! -e /mnt/ps4-release-stage/app/ps4-android ]
[ ! -e /mnt/ps4-release-stage/data/pkg/ps4-android13-sparse-v008.pkg ]
[ ! -e /mnt/ps4-release-stage/data/pkg/ps4-android13-sparse-v008.pkg.staging ]
'''
subprocess.run(ssh+['/bin/sh','-s'],input=prep.encode(),check=True)
target='/mnt/ps4-release-stage/data/pkg/ps4-android13-sparse-v008.pkg'
proc=subprocess.Popen(ssh+['set -C; cat > '+target+'.staging'],stdin=subprocess.PIPE)
h=hashlib.sha256();start=time.monotonic();done=0
with Path(m['path']).open('rb') as f:
 while chunk:=f.read(4*1024*1024):
  proc.stdin.write(chunk);h.update(chunk);done+=len(chunk)
  if done%(256*1024*1024)==0:print(f'{done/1e9:.2f} GB transferred',flush=True)
proc.stdin.close();assert proc.wait()==0
assert h.hexdigest()==m['sha256']
check=subprocess.check_output(ssh+['sync; sha256sum '+target+'.staging'],text=True)
assert check.split()[0]==m['sha256'],check
subprocess.run(ssh+['mv '+target+'.staging '+target+'; chmod 644 '+target+'; sync'],check=True)
result={'console_pkg':'/data/pkg/ps4-android13-sparse-v008.pkg','bytes':done,'sha256':m['sha256'],'write_readback_seconds':time.monotonic()-start,'fresh_install_directory_absent':True,'installed':False}
(b/'staged.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
