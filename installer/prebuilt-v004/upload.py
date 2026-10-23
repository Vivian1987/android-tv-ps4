from pathlib import Path
import time,json,hashlib,ftplib
b=Path('/dev/shm/ps4-v004')
for _ in range(120):
 if (b/'manifest.json').exists():break
 time.sleep(2)
else:raise SystemExit('No validated package')
r=json.loads((b/'manifest.json').read_text());name='ps4-android13-32GB-data-ATVX13001-v004.pkg';stage=name+'.uploading'
with ftplib.FTP() as f:
 f.connect('192.168.0.77',2121,timeout=20);f.login();f.cwd('/data/pkg')
 assert name not in f.nlst() and stage not in f.nlst(),'Existing upload preserved'
 print('Uploading validated prebuilt-image installer',flush=True)
 with Path(r['path']).open('rb') as src:f.storbinary('STOR '+stage,src,blocksize=1024*1024)
 print('Verifying complete readback from PS4',flush=True)
 h=hashlib.sha256();f.retrbinary('RETR '+stage,h.update,blocksize=1024*1024)
 assert h.hexdigest()==r['sha256'],'Readback mismatch; preserve .uploading file'
 f.rename(stage,name)
 old='ps4-android13-32gib-ATVX13001-v003.pkg'
 if old in f.nlst() and old+'.superseded' not in f.nlst():f.rename(old,old+'.superseded')
 result={'path':'/data/pkg/'+name,'bytes':r['bytes'],'sha256':h.hexdigest(),'installed':False}
 (b/'staged.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
