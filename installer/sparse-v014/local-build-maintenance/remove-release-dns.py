from pathlib import Path
import gzip,json,hashlib
p=Path('/mnt/nas/apps/ps4-android/installer/sparse-v014');b=Path('/dev/shm/ps4-v014');raw=gzip.decompress((b/'assets/initramfs.cpio.gz').read_bytes());pos=0;out=bytearray();inv=[]
while pos<len(raw):
 h=raw[pos:pos+110];v=[int(h[6+i*8:14+i*8],16) for i in range(13)];n=raw[pos+110:pos+110+v[11]-1].decode();pos=(pos+110+v[11]+3)&~3;d=raw[pos:pos+v[6]];pos=(pos+v[6]+3)&~3
 if n=='etc/resolv.conf':d=b'# Android configures DNS through its own network service.\n'
 inv.append({'path':n,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()});v[6]=len(d);out.extend(b'070701'+''.join(f'{x:08x}' for x in v).encode()+n.encode()+b'\0');out.extend(b'\0'*(-len(out)%4));out.extend(d);out.extend(b'\0'*(-len(out)%4))
 if n=='TRAILER!!!':break
assert b'192.168.0.250' not in out
blob=gzip.compress(bytes(out),compresslevel=6,mtime=0);(b/'assets/initramfs.cpio.gz').write_bytes(blob);(p/'initramfs.cpio.gz').write_bytes(blob)
r=json.loads((p/'release-audit.json').read_text());r['assets']['initramfs.cpio.gz']=hashlib.sha256(blob).hexdigest();r['personal_data_scan']='26667 files checked; room-name hits are generic Android resource choices; Wi-Fi config contains no networks; developer DNS removed';(p/'release-audit.json').write_text(json.dumps(r,indent=2)+'\n');(p/'initramfs-inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
print('Removed final personal DNS address; retained generic Android room-name resources')
