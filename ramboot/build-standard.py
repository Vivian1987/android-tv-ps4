"""Build the default prototype image with mandatory, verified graphics fixes."""
from pathlib import Path
import gzip, hashlib, json, time, subprocess
project = Path(__file__).resolve().parents[1]
work = Path('/home/amber/projects/ps4-android')
base = work/'installer-recovery/restore-prototype'
assets = work/'autoboot-assets'
outdir = work/'standard-boot'
outdir.mkdir(exist_ok=True)
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha((base/'initramfs.cpio.gz').read_bytes()) == '1227c5b013bd45bf37558ee70df78c2c45700c84e0b98c6f5019c575e2a10317'
assert sha((base/'bzImage').read_bytes()) == '0e214b0b823e05d6736d667c0f536e71efaad66e5921f201b903eebcd4fc6845'
graphics = 'd0132e6968085c418492b64053b4b1a7df78aca09fd9bf2c32eb8e79555d22ab'
assert sha((assets/'gralloc-gbm-yv12-stride.so').read_bytes()) == graphics

def unpack(blob):
    b=gzip.decompress(blob); p=0; entries={}
    while p<len(b):
        h=b[p:p+110]; assert h[:6]==b'070701'
        v=[int(h[6+i*8:14+i*8],16) for i in range(13)]
        name=b[p+110:p+110+v[11]-1].decode(); p=(p+110+v[11]+3)&~3
        data=b[p:p+v[6]]; p=(p+v[6]+3)&~3
        if name=='TRAILER!!!': break
        entries[name]=(v,data)
    return entries
entries=unpack((base/'initramfs.cpio.gz').read_bytes())
def put(name,data,mode=0o100644):
    entries[name]=([len(entries)+1,mode,0,0,1,0,len(data),0,0,0,0,len(name.encode())+1,0],data)
for file in assets.iterdir():
    if file.is_file(): put('opt/cole-android/'+file.name,file.read_bytes(),0o100755 if file.suffix=='.sh' else 0o100644)
put('opt/cole-android/boot-time',str(int(time.time())).encode()+b'\n')
start=(assets/'autoboot.sh').read_text()
assert 'waiting for wired image server' in start
assert 'gralloc-gbm-yv12-stride.so' in start and 'libgallium-baseline.so' in start
check=f"echo '{graphics}  /android/system/vendor/lib64/hw/gralloc.gbm.so' | sha256sum -c -\n"
start=start.replace("stage 'Launching Android init with baseline Mesa and RGB video buffers'",check+"stage 'Launching Android init with verified graphics baseline (standard-v1)'" )
put('opt/cole-android/autoboot.sh',start.encode(),0o100755)
put('usr/sbin/cole-android-start',start.encode(),0o100755)
put('opt/cole-android/graphics-baseline',b'standard-v1\n')
subprocess.run(['/bin/busybox','sh','-n'],input=start.encode(),check=True)
assert b'cole-android-start' in entries['init'][1]
archive=bytearray()
for name,(v,data) in list(entries.items())+[('TRAILER!!!',([0]*13,b''))]:
    v=v.copy(); v[6]=len(data); v[11]=len(name.encode())+1
    archive.extend(b'070701'+''.join(f'{x:08x}' for x in v).encode()+name.encode()+b'\0')
    archive.extend(b'\0'*(-len(archive)%4)); archive.extend(data); archive.extend(b'\0'*(-len(archive)%4))
blob=gzip.compress(bytes(archive),compresslevel=6,mtime=0)
verified=unpack(blob)
assert sha(verified['opt/cole-android/gralloc-gbm-yv12-stride.so'][1])==graphics
assert check.encode() in verified['usr/sbin/cole-android-start'][1]
(outdir/'initramfs.cpio.gz').write_bytes(blob); (outdir/'initramfs.cpio.gz').chmod(0o600)
for name in ['bzImage','bootargs.txt','vram.txt']: (outdir/name).write_bytes((base/name).read_bytes())
manifest={'version':'standard-v1','purpose':'Default prototype boot with complete graphics fixes, network wait and persistent userdata','files':{n:{'path':str(outdir/n),'sha256':sha((outdir/n).read_bytes())} for n in ['bzImage','initramfs.cpio.gz','bootargs.txt','vram.txt']},'gralloc_sha256':graphics,'validated_archive_contents':True,'boot_verified':False}
(project/'evidence/standard-boot.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
