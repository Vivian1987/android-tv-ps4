import ftplib,io,json
from pathlib import Path
f=ftplib.FTP();f.connect('192.168.0.77',2121,timeout=10);f.login();root='/user/app/ps4-android';o=io.BytesIO();f.retrbinary('RETR '+root+'/ready',o.write);assert o.getvalue()==b'PS4ANDROID13-SPARSE-V010\nedition=32\n'
lines=[];f.retrlines('LIST '+root,lines.append);files={l.split(maxsplit=8)[8] for l in lines if l.startswith('-')};assert files=={'data-gib.txt','data-ready','data.img','libgallium-baseline.so','ready','system.sfs'},files
for n in files:f.delete(root+'/'+n)
f.rmd(root);f.quit();Path('/mnt/nas/apps/ps4-android/installer/sparse-v014/reset.json').write_text(json.dumps({'deleted_test_directory':root,'files':sorted(files),'checkpoint_preserved':True},indent=2)+'\n');print('Previous Android test installation deleted; recovery checkpoint untouched')
