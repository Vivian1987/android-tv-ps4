from pathlib import Path
import os,subprocess,shutil,hashlib,json,time
from PIL import Image,ImageDraw,ImageFont
b=Path('/mnt/nas/apps/ps4-android/installer/raw-v007');w=Path('/home/amber/projects/ps4-android');sdk=w/'toolchains/OpenOrbis/PS4Toolchain';tools=sdk/'bin/linux';cid='IV0000-ATVX13001_00-PS4ANDROIDTV0000'
env=dict(os.environ,OO_PS4_TOOLCHAIN=str(sdk),DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1',LD_LIBRARY_PATH=str(w/'toolchains/pkgtool-runtime/usr/lib/x86_64-linux-gnu'))
for _ in range(120):
 if (b/'images-verified').exists():break
 time.sleep(2)
else:raise SystemExit('Image validation has not completed')
shutil.copytree(w/'installer-recovery/v003/sce_sys',b/'sce_sys',dirs_exist_ok=True)
shutil.copytree(w/'installer-recovery/v003/sce_module',b/'sce_module',dirs_exist_ok=True)
img=Image.new('RGB',(512,512),'#10202c');d=ImageDraw.Draw(img);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',32)
for y,t,color in [(80,'PS4 Android TV','white'),(170,'Android 13','#50ddb0'),(250,'32 GB raw images','white'),(340,'Setup / Boot','white')]:d.text((32,y),t,font=font,fill=color)
img.save(b/'sce_sys/icon0.png')
def run(args):subprocess.run([str(x) for x in args],cwd=b,env=env,check=True)
for key,value in [('APP_VER','0.07'),('VERSION','0.07'),('TITLE','PS4 Android TV - 32 GB raw')]:
 run([tools/'PkgTool.Core','sfo_setentry','sce_sys/param.sfo',key,'--type','Utf8','--maxsize','128' if key=='TITLE' else '8','--value',value])
files=['eboot.bin','sce_sys/about/right.sprx','sce_sys/param.sfo','sce_sys/icon0.png','sce_module/libc.prx','sce_module/libSceFios2.prx']+['assets/'+p.name for p in sorted((b/'assets').iterdir())]
run([tools/'create-gp4','-out','pkg.gp4','--content-id='+cid,'--files',' '.join(files)])
run([tools/'PkgTool.Core','pkg_build','pkg.gp4','.'])
pkg=b/(cid+'.pkg');v=subprocess.run([str(tools/'PkgTool.Core'),'pkg_validate',str(pkg)],cwd=b,env=env,text=True,capture_output=True,check=True)
assert '[FAIL]' not in v.stdout and '[ERROR]' not in v.stdout
(b/'validation.txt').write_text(v.stdout)
r={'version':'0.07','path':str(pkg),'bytes':pkg.stat().st_size,'sha256':hashlib.file_digest(pkg.open('rb'),'sha256').hexdigest(),'content_id':cid,'data_bytes':33554432000,'system_bytes':5269999616,'data_source':'DATA-32GB.zip','layout':'raw system.img and data.img; PS4 copies without decompression','console_tested':False,'validation':v.stdout}
(b/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='validation'},indent=2),flush=True)
