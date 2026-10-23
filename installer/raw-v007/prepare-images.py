from pathlib import Path
import gzip,zipfile,hashlib,json,os,time
b=Path('/mnt/nas/apps/ps4-android/installer/raw-v007')
records=[]
def extract(src,name,expected,expected_hash=None):
 target=b/'assets'/name;stage=target.with_suffix('.preparing')
 assert not target.exists() and not stage.exists(), 'Existing image preserved'
 h=hashlib.sha256();size=0;start=time.monotonic()
 with stage.open('xb') as out:
  while data:=src.read(4*1024*1024):
   h.update(data);size+=len(data)
   if data.count(0)==len(data):out.seek(len(data),1)
   else:out.write(data)
  out.truncate(size);out.flush();os.fsync(out.fileno())
 assert size==expected
 if expected_hash:assert h.hexdigest()==expected_hash
 stage.rename(target)
 r={'name':name,'bytes':size,'sha256':h.hexdigest(),'seconds':time.monotonic()-start,'host_sparse_storage':True}
 records.append(r);print(json.dumps(r),flush=True)
with gzip.open('/dev/shm/ps4-v004/assets/system.img.gz','rb') as src:
 extract(src,'system.img',5269999616,'057c243d8e0a102376b7454ffdeae2a591aee8c53141795933342bc538046f59')
with zipfile.ZipFile('/home/amber/Downloads/Telegram Desktop/DATA-32GB.zip') as archive:
 with archive.open('data.img') as src:extract(src,'data.img',33554432000)
(b/'raw-images.json').write_text(json.dumps(records,indent=2))
(b/'images-verified').write_text('Host decompression complete; system SHA256 and supplied ZIP CRC verified.\n')
