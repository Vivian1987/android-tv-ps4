from pathlib import Path
import time,json,hashlib,ftplib
b=Path('/mnt/nas/apps/ps4-android/installer/raw-v007')
end=time.monotonic()+7200
pkg=b/'IV0000-ATVX13001_00-PS4ANDROIDTV0000.pkg'
def validation_started():
 for proc in Path('/proc').glob('[0-9]*/cmdline'):
  try:cmd=proc.read_bytes().split(b'\0')
  except (OSError,PermissionError):continue
  if b'pkg_validate' in cmd and str(pkg).encode() in cmd:return True
 return False
while not (b/'manifest.json').exists() and not validation_started():
 if time.monotonic()>end:raise SystemExit('No finished package reached validation; nothing uploaded')
 time.sleep(2)
r={'path':str(pkg),'bytes':pkg.stat().st_size}
name='ps4-android13-32GB-raw-ATVX13001-v007.pkg';stage=name+'.uploading'
with ftplib.FTP() as f:
 f.connect('192.168.0.77',2121,timeout=60);f.login();f.cwd('/data/pkg')
 assert name not in f.nlst() and stage not in f.nlst(),'Existing upload preserved'
 print('Uploading finished package while validation runs; keeping .uploading suffix',flush=True)
 done=0;reported=0;start=time.monotonic();sent_hash=hashlib.sha256()
 def progress(data):
  global done,reported
  done+=len(data);sent_hash.update(data)
  if done-reported>=2*1024**3:
   print(f'Uploaded {done/1e9:.1f}/{r["bytes"]/1e9:.1f} GB at {done/(time.monotonic()-start)/1e6:.1f} MB/s',flush=True);reported=done
 with Path(r['path']).open('rb') as src:f.storbinary('STOR '+stage,src,blocksize=1024*1024,callback=progress)
 print('Transfer finished; waiting for successful validation manifest',flush=True)
 while not (b/'manifest.json').exists():
  if time.monotonic()>end:raise SystemExit('Validation not confirmed; .uploading file preserved')
  time.sleep(2)
 r=json.loads((b/'manifest.json').read_text())
 assert sent_hash.hexdigest()==r['sha256'],'Source transfer hash differs from validated package'
 print('Verifying full package readback from PS4',flush=True)
 h=hashlib.sha256();f.retrbinary('RETR '+stage,h.update,blocksize=1024*1024)
 assert h.hexdigest()==r['sha256'],'Readback mismatch; .uploading file preserved'
 f.rename(stage,name)
 old='ps4-android13-32GB-data-ATVX13001-v006.pkg'
 if old in f.nlst() and old+'.superseded' not in f.nlst():f.rename(old,old+'.superseded')
 result={'path':'/data/pkg/'+name,'bytes':r['bytes'],'sha256':h.hexdigest(),'installed':False}
 (b/'staged.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
