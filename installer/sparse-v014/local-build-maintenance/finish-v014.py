from pathlib import Path
import pickle,gzip,shutil,hashlib,json,subprocess,re
p=Path('/mnt/nas/apps/ps4-android/installer/sparse-v014');b=Path('/dev/shm/ps4-v014');entries=pickle.loads((p/'initramfs-entries.private.pickle').read_bytes());out=[]
module=Path('/home/amber/projects/ps4-android/quota2/xt_quota2.ko').read_bytes()
vendor=Path('/mnt/atv-release-audit-system/system/vendor/etc/init/init.android_x86_64.rc').read_text()
vendor=vendor.replace('setprop persist.sys.usb.config adb','setprop persist.sys.usb.config none').replace('setprop persist.service.adb.enable 1','setprop persist.service.adb.enable 0').replace('setprop service.adb.tcp.port 5555','setprop service.adb.tcp.port -1').replace('setprop persist.adb.tcp.port 5555','setprop persist.adb.tcp.port -1')
# Remove forced restarts that bypass the user's Developer Options choice.
vendor=re.sub(r'\non property:service.adb.tcp.port=(?:5555|-1)\n    stop adbd\n    start adbd\n','\n',vendor)
vendor='\n'.join(l for l in vendor.splitlines() if 'setprop ro.serialno ' not in l and 'setprop ril.serialnumber ' not in l)+'\n'
for n,v,d in entries:
 if n=='TRAILER!!!':trailer=(n,v,d);continue
 n=n.replace('6.15.4-androidtv-ps4-aeolia-v1','6.15.4-androidtv-ps4-aeolia')
 if n.endswith('xt_quota2.ko'):d=module
 if n=='usr/sbin/androidtv-ps4-start' or n=='opt/androidtv-ps4/autoboot.sh':
  s=d.decode().replace('PS4ANDROID13-SPARSE-V010','PS4ANDROID13-SPARSE-V014')
  line='cp "$assets/vendor-build.prop" /android/system/vendor/build.prop'
  s=s.replace(line,line+'\ncp "$assets/init.android_x86_64.rc" /android/system/vendor/etc/init/init.android_x86_64.rc')
  s=s.replace('exec >>"$installation/boot.log" 2>&1', '''save_logs() {
 status=$?
 [ "$status" = 0 ] || stage "SETUP FAILED (status $status); data preserved"
 cp /run/androidtv-ps4/one-shot.log "$installation/boot.log" 2>/dev/null || true
 dmesg > "$installation/kernel.log" 2>/dev/null || true
 sync
}
trap save_logs EXIT''')
  d=s.encode()
 # Store human-readable release inputs for the repo without diagnostics/credentials.
 if n=='init' or n.startswith('opt/androidtv-ps4/') and n.endswith(('.sh','.rc','.prop')) or n=='usr/sbin/androidtv-ps4-start':
  q=p/'release-inputs'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(d)
 if n=='init' or n.endswith(('autoboot.sh','android-child.sh')) or n=='usr/sbin/androidtv-ps4-start':subprocess.run(['/bin/busybox','sh','-n'],input=d,check=True)
 out.append((n,v,d))
v=next(v.copy() for n,v,d in out if n=='opt/androidtv-ps4/vendor-build.prop');out.append(('opt/androidtv-ps4/init.android_x86_64.rc',v,vendor.encode()));out.append(trailer)
(p/'release-inputs/opt/androidtv-ps4/init.android_x86_64.rc').write_text(vendor)
buf=bytearray()
for n,v,d in out:
 v=v.copy();v[6]=len(d);v[11]=len(n.encode())+1
 buf.extend(b'070701'+''.join(f'{x:08x}' for x in v).encode()+n.encode()+b'\0');buf.extend(b'\0'*(-len(buf)%4));buf.extend(d);buf.extend(b'\0'*(-len(buf)%4))
assert not any('authorized_keys' in n or 'host_ed25519' in n or 'dropbear' in n for n,v,d in out)
for n,v,d in out:
 if n=='init' or n.endswith(('.sh','.rc','.prop')) or n=='usr/sbin/androidtv-ps4-start':
  assert b'192.168.0.77' not in d,(n,'private IP')
  assert b'ro.adb.secure=0' not in d,(n,'unauthenticated adb')
  assert b'setprop service.adb.tcp.port 5555' not in d,(n,'default TCP adb')
blob=gzip.compress(bytes(buf),compresslevel=6,mtime=0);(b/'assets/initramfs.cpio.gz').write_bytes(blob);(p/'initramfs.cpio.gz').write_bytes(blob)
shutil.copy2('/home/amber/projects/ps4-android/kernel-6.15.4/arch/x86/boot/bzImage',b/'assets/bzImage')
shutil.copy2('/home/amber/projects/ps4-android/kernel-6.15.4/.config',p/'kernel.config')
src=p/'source/install-prebuilt.c';src.write_text(src.read_text().replace('SPARSE-V010','SPARSE-V014').replace('before-sparse-v010','before-sparse-v014'))
r={'version':'v014','kernel':'6.15.4-androidtv-ps4-aeolia','model':'PlayStation 4','fingerprint':'preserved','ssh_server':False,'bundled_ssh_keys':False,'fixed_management_ip':False,'default_network_adb':False,'adb_authentication_required':True,'console_tested':False,'public_release_ready':False,'limitations':['SELinux permissive retained for compatibility','Base Android distribution/root components and redistribution rights require review','Only CUH-1102A hardware tested in previous build','Fresh install, Google login and playback require testing after model/debugging changes'],'assets':{x.name:hashlib.file_digest(x.open('rb'),'sha256').hexdigest() for x in (b/'assets').iterdir()}}
(p/'release-audit.json').write_text(json.dumps(r,indent=2)+'\n')
print('Release-candidate archive and source inputs ready; identity and access checks passed')
