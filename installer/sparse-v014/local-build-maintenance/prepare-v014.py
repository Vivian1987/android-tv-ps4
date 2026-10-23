from pathlib import Path
import shutil,os,gzip,hashlib,re,json,subprocess
root=Path('/mnt/nas/apps/ps4-android/installer');old=root/'sparse-v013';new=root/'sparse-v014';b=Path('/dev/shm/ps4-v014');(b/'assets').mkdir(parents=True,exist_ok=True)
p=Path('/dev/shm/ps4-v011/IV0000-ATVX13001_00-PS4ANDROIDTV0000.pkg');a=root/'sparse-v011'/p.name
if p.exists():
 assert hashlib.file_digest(p.open('rb'),'sha256').digest()==hashlib.file_digest(a.open('rb'),'sha256').digest();p.unlink()
shutil.copytree(old/'source',new/'source',dirs_exist_ok=True)
for n in ['build.py','package.py','upload.py','image-metadata.h']:(new/n).write_text((old/n).read_text().replace('v013','v014').replace('0.13','0.14'))
shutil.copy2(new/'image-metadata.h',b/'image-metadata.h')
for p in Path('/dev/shm/ps4-v013/assets').iterdir():
 if p.name not in ['initramfs.cpio.gz','bzImage'] and not (b/'assets'/p.name).exists():os.link(p,b/'assets'/p.name)
raw=gzip.decompress(Path('/dev/shm/ps4-v013/assets/initramfs.cpio.gz').read_bytes());pos=0;entries=[];removed=[]
while pos<len(raw):
 h=raw[pos:pos+110];v=[int(h[6+i*8:14+i*8],16) for i in range(13)];n=raw[pos+110:pos+110+v[11]-1].decode();pos=(pos+110+v[11]+3)&~3;d=raw[pos:pos+v[6]];pos=(pos+v[6]+3)&~3
 if n.startswith(('etc/dropbear','root/.ssh')) or n=='usr/sbin/dropbear':removed.append(n);continue
 n=n.replace('cole-android','androidtv-ps4').replace('cole-ps4.rc','androidtv-ps4.rc')
 if n=='init':
  s=d.decode();a=s.index('network_ready=0');z=s.index('mkdir -p /run/cole',a);s=s[:a]+s[z:]
  a=s.index('/usr/sbin/dropbear');z=s.index("echo 'Reports",a);s=s[:a]+s[z:]
  s=s.replace('hostname cole-ps4','hostname androidtv-ps4').replace('internal first-install test','standalone installer').replace('[Cole boot]','[Android TV]')
  s=s.replace('    setsid cttyhack /bin/sh','    echo "Android startup unavailable. Restart the console to return to PS4."')
  d=s.encode()
 if n=='init' or n.endswith(('.sh','.rc','.prop')) or n=='usr/sbin/androidtv-ps4-start':
  s=d.decode();s=s.replace('/opt/cole-android','/opt/androidtv-ps4').replace('/usr/sbin/cole-android-start','/usr/sbin/androidtv-ps4-start').replace('/run/cole','/run/androidtv-ps4').replace('cole-ps4.rc','androidtv-ps4.rc')
  if n.endswith('.prop'):
   s=re.sub(r'(?m)^(ro\.product(?:\.[a-z]+)?\.model)=.*$',r'\1=PlayStation 4',s)
   s=re.sub(r'(?m)^ro.build.display.id=.*$','ro.build.display.id=Android TV for PS4 13 - v014',s)
   for key,value in {'ro.secure':'1','ro.debuggable':'0','ro.adb.secure':'1','persist.sys.debuggable':'0','persist.service.adb.enable':'0','persist.service.debuggable':'0','persist.sys.usb.config':'none','persist.adb.tcp.port':'-1','service.adb.tcp.port':'-1','ro.soc.manufacturer':'AMD','ro.soc.model':'Jaguar'}.items():
    s=re.sub(r'(?m)^'+re.escape(key)+r'=.*$',key+'='+value,s)
   if n.endswith('system-build.prop'):s+='\npersist.sys.usb.config=none\npersist.adb.tcp.port=-1\nservice.adb.tcp.port=-1\n'
  if 'androidboot.serialno=coleps4' in s:
   target="printf '%s\\n' 'androidboot.hardware="
   at=s.index(target)
   s=s[:at]+'''# Per-install identifier; no developer identity or fabricated hardware serial.
if [ ! -s "$installation/device-id" ]; then
 od -An -N8 -tx1 /dev/urandom | tr -d ' \\n' > "$installation/device-id"
 sync
fi
serial=$(cat "$installation/device-id")
'''+s[at:]
   s=s.replace("'androidboot.hardware=",'"androidboot.hardware=').replace("GRALLOC=gbm' >",'GRALLOC=gbm" >').replace('androidboot.serialno=coleps4','androidboot.serialno=ps4${serial}')
   s=s.replace('# A separate MAC address gives Android ordinary DHCP while management retains .77.','# Android owns its DHCP configuration; the host has no management address.\n/usr/sbin/ip link set eth0 up')
   s=s.replace('# Move the real Marvell radio into Android; SSH stays on the physical eth0.','# Move the real Marvell radio into Android.')
   s=s.replace('Android boot timeout; SSH and logs remain available','Android boot timeout; logs remain on the console')
   s=s.replace('installation=/mnt/ps4-user/app/ps4-android','installation=/mnt/ps4-user/app/ps4-android\n# Persist startup output locally for diagnosis without remote access.\nexec >>"$installation/boot.log" 2>&1')
  d=s.encode()
 if n.startswith('lib/modules/'):
  n=n.replace('6.15.4-cole-android-aeolia-v1','6.15.4-androidtv-ps4-aeolia')
 entries.append((n,v,d))
 if n=='TRAILER!!!':break
# Kernel and quota module must be built before assembling the final archive.
(new/'initramfs-entries.json').write_text(json.dumps({'removed':removed,'files':len(entries)},indent=2)+'\n')
import pickle
(new/'initramfs-entries.private.pickle').write_bytes(pickle.dumps(entries))
for n,v,d in entries:
 if n=='init' or n.endswith(('.sh',)) or n=='usr/sbin/androidtv-ps4-start':
  subprocess.run(['/bin/busybox','sh','-n'],input=d,check=True)
print('v014 sources prepared; boot script syntax passes; SSH credentials and server removed')
