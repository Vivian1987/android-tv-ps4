from pathlib import Path
import ftplib,json,hashlib,time
b=Path(__file__).resolve().parent;m=json.loads((b/'manifest.json').read_text());src=Path(m['path']);name='ps4-android13-sparse-v014.pkg';stage=name+'.uploading'
f=ftplib.FTP();f.connect('192.168.0.77',2121,timeout=30);f.login();f.cwd('/data/pkg');assert name not in f.nlst() and stage not in f.nlst()
h=hashlib.sha256();done=0;last=0;start=time.monotonic()
def progress(data):
 global done,last
 h.update(data);done+=len(data)
 if done-last>=256*1024*1024:print(f'Uploaded {done/1e9:.2f}/{m["bytes"]/1e9:.2f} GB',flush=True);last=done
with src.open('rb') as source:f.storbinary('STOR '+stage,source,blocksize=1024*1024,callback=progress)
assert h.hexdigest()==m['sha256'];print('Verifying console readback',flush=True)
r=hashlib.sha256();f.retrbinary('RETR '+stage,r.update,blocksize=1024*1024);assert r.hexdigest()==m['sha256']
f.rename(stage,name);f.quit()
result={'console_path':'/data/pkg/'+name,'sha256':r.hexdigest(),'bytes':done,'seconds':time.monotonic()-start,'readback_verified':True,'installed':False};(b/'staged.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
