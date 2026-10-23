import os,re,json,gzip
from pathlib import Path
root=Path('/mnt/atv-release-audit-system');p=Path('/mnt/nas/apps/ps4-android/installer/sparse-v014');hits=[];scanned=0;named=[]
needles=[b'/home/amber',b'/opt/cole',b'/run/cole',b'coleps4',b'cole-android',b'codeyoc@gmail',b'fvdegrxy@gmail',b'192.168.0.77',b'192.168.0.250',b'192.168.0.157',b'Bedroom TV']
key=Path('/home/amber/.local/share/cole-ps4-android/id_ed25519.pub').read_bytes().split()[1];needles.append(key)
def scan(path,label):
 global scanned
 try:
  with path.open('rb') as f:
   tail=b'';found=set()
   while True:
    data=f.read(4*1024*1024)
    if not data:break
    data=tail+data
    for i,n in enumerate(needles):
     if n in data:found.add(i)
    tail=data[-2048:]
   scanned+=1
   if found:hits.append({'file':label,'matches':[('personal SSH public key' if i==len(needles)-1 else needles[i].decode()) for i in sorted(found)]})
 except OSError as e:hits.append({'file':label,'scan_error':str(e)})
for base,ds,fs in os.walk(root):
 for n in fs:
  f=Path(base)/n
  if f.is_symlink():continue
  rel=str(f.relative_to(root))
  if n in ['authorized_keys','adb_keys','accounts.db','accounts_ce.db','accounts_de.db','WifiConfigStore.xml','wpa_supplicant.conf'] or n.startswith(('id_rsa','id_ed25519','ssh_host_')):named.append(rel)
  scan(f,rel)
for f in Path('/dev/shm/ps4-v014/assets').iterdir():
 if f.name in ['system.sfs','initramfs.cpio.gz']:continue
 scan(f,'package/assets/'+f.name)
raw=gzip.decompress(Path('/dev/shm/ps4-v014/assets/initramfs.cpio.gz').read_bytes());found=[('personal SSH public key' if i==len(needles)-1 else n.decode()) for i,n in enumerate(needles) if n in raw]
r={'files_scanned':scanned,'personal_marker_hits':hits,'sensitive_filename_review':named,'initramfs_personal_marker_hits':found,'scope':'Mounted system filesystem, decompressed initramfs and other package assets; no userdata image bundled'}
(p/'personal-data-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
