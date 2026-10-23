from pathlib import Path
import gzip,json,hashlib,subprocess
p=Path('/mnt/nas/apps/ps4-android/installer/sparse-v014');b=Path('/dev/shm/ps4-v014');raw=gzip.decompress((b/'assets/initramfs.cpio.gz').read_bytes());pos=0;out=bytearray();inventory=[]
while pos<len(raw):
 h=raw[pos:pos+110];v=[int(h[6+i*8:14+i*8],16) for i in range(13)];n=raw[pos+110:pos+110+v[11]-1].decode();pos=(pos+110+v[11]+3)&~3;d=raw[pos:pos+v[6]];pos=(pos+v[6]+3)&~3
 if n.endswith('system-build.prop'):
  d=d.replace(b'persist.service.adb.enable=0',b'persist.service.adb.enable=1').replace(b'adb.tcp.port=-1',b'adb.tcp.port=5555')
 if n.endswith('init.android_x86_64.rc'):
  d=d.replace(b'setprop persist.service.adb.enable 0',b'setprop persist.service.adb.enable 1').replace(b'adb.tcp.port -1',b'adb.tcp.port 5555')
  d+=b'\n# Developer access is enabled; each host must be authorized on this device.\non property:sys.boot_completed=1\n    setprop service.adb.tcp.port 5555\n    start adbd\n'
 if n.startswith('opt/androidtv-ps4/') and n.endswith(('.sh','.rc','.prop')):(p/'release-inputs'/n).write_bytes(d)
 assert not any(x in n for x in ['authorized_keys','host_ed25519','adb_keys'])
 inventory.append({'path':n,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()})
 v[6]=len(d);out.extend(b'070701'+''.join(f'{x:08x}' for x in v).encode()+n.encode()+b'\0');out.extend(b'\0'*(-len(out)%4));out.extend(d);out.extend(b'\0'*(-len(out)%4))
 if n=='TRAILER!!!':break
blob=gzip.compress(bytes(out),compresslevel=6,mtime=0)
(b/'assets/initramfs.cpio.gz').write_bytes(blob);(p/'initramfs.cpio.gz').write_bytes(blob)
r=json.loads((p/'release-audit.json').read_text());r['default_network_adb']=True;r['adb_port']=5555;r['assets']['initramfs.cpio.gz']=hashlib.sha256(blob).hexdigest();r['user_direction']='Keep development primitives; ADB on at boot, no bundled personal trust or credentials';(p/'release-audit.json').write_text(json.dumps(r,indent=2)+'\n');(p/'initramfs-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
print('ADB enabled at boot; authorization flag retained; no bundled trusted keys')
