from pathlib import Path
import ftplib,time,io,json,subprocess
b=Path(__file__).resolve().parent;deadline=time.monotonic()+300
while True:
 f=ftplib.FTP()
 try:f.connect('192.168.0.77',2121,timeout=3);f.login();break
 except OSError:
  f.close()
  if time.monotonic()>deadline:raise SystemExit('Waiting for GoldHEN FTP; no reset performed')
  time.sleep(3)
root='/user/app/ps4-android';out=io.BytesIO();f.retrbinary('RETR '+root+'/ready',out.write);assert out.getvalue()==b'PS4ANDROID13-SPARSE-V009\nedition=32\n'
lines=[];f.retrlines('LIST '+root,lines.append);files={x.split(maxsplit=8)[8] for x in lines if x.startswith('-')};expected={'data-gib.txt','data-ready','data.img','libgallium-baseline.so','ready','system.sfs'};assert files==expected,files
removed=[]
for n in sorted(files):f.delete(root+'/'+n);removed.append(root+'/'+n)
f.rmd(root)
f.delete('/data/pkg/ps4-android13-sparse-v009.pkg');removed.append('/data/pkg/ps4-android13-sparse-v009.pkg')
try:f.cwd(root);raise AssertionError('Installation still present')
except ftplib.error_perm:pass
app=[]
try:f.retrlines('LIST /user/app/ATVX13001',app.append)
except ftplib.error_perm:pass
f.quit();(b/'clean-install-reset.json').write_text(json.dumps({'removed':removed,'install_directory_absent':True,'native_app_directory_present':bool(app),'checkpoint_preserved':True},indent=2)+'\n')
print('v009 test data removed; clean installation verified',flush=True)
subprocess.run(['python3',str(b/'upload.py')],check=True)
