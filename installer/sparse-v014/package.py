from pathlib import Path
import os,subprocess,shutil,hashlib,json,time
from PIL import Image,ImageDraw,ImageFont
b=Path('/dev/shm/ps4-v014');w=Path('/home/amber/projects/ps4-android');sdk=w/'toolchains/OpenOrbis/PS4Toolchain';tools=sdk/'bin/linux';cid='IV0000-ATVX13001_00-PS4ANDROIDTV0000'
env=dict(os.environ,OO_PS4_TOOLCHAIN=str(sdk),DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1',LD_LIBRARY_PATH=str(w/'toolchains/pkgtool-runtime/usr/lib/x86_64-linux-gnu'))
shutil.copytree(w/'installer-recovery/v003/sce_sys',b/'sce_sys',dirs_exist_ok=True)
shutil.copytree(w/'installer-recovery/v003/sce_module',b/'sce_module',dirs_exist_ok=True)
branding=Path('/mnt/nas/apps/ps4-android/branding')
Image.open(branding/'icon-official-assets-v6.png').convert('RGBA').save(b/'sce_sys/icon0.png')
subprocess.run(['inkscape',str(branding/'banner-official-assets-v6.svg'),'--export-width=1920','--export-height=1080','--export-filename='+str(b/'sce_sys/pic1.png')],check=True)
picture=Image.open(b/'sce_sys/pic1.png').convert('RGBA')
matte=Image.new('RGBA',picture.size,'#0b1424')
matte.alpha_composite(picture)
matte.convert('RGB').save(b/'sce_sys/pic1.png')
def run(args):subprocess.run([str(x) for x in args],cwd=b,env=env,check=True)
for key,value in [('APP_VER','0.14'),('VERSION','0.14'),('TITLE','Android TV for PS4')]:
 run([tools/'PkgTool.Core','sfo_setentry','sce_sys/param.sfo',key,'--type','Utf8','--maxsize','128' if key=='TITLE' else '8','--value',value])
files=['eboot.bin','sce_sys/about/right.sprx','sce_sys/param.sfo','sce_sys/icon0.png','sce_sys/pic1.png','sce_module/libc.prx','sce_module/libSceFios2.prx']+['assets/'+p.name for p in sorted((b/'assets').iterdir())]
run([tools/'create-gp4','-out','pkg.gp4','--content-id='+cid,'--files',' '.join(files)])
run([tools/'PkgTool.Core','pkg_build','pkg.gp4','.'])
pkg=b/(cid+'.pkg');v=subprocess.run([str(tools/'PkgTool.Core'),'pkg_validate',str(pkg)],cwd=b,env=env,text=True,capture_output=True,check=True)
assert '[FAIL]' not in v.stdout and '[ERROR]' not in v.stdout
(b/'validation.txt').write_text(v.stdout)
r={'version':'0.14','path':str(pkg),'bytes':pkg.stat().st_size,'sha256':hashlib.file_digest(pkg.open('rb'),'sha256').hexdigest(),'content_id':cid,'data_bytes':34359738368,'system_bytes':(b/'assets/system.sfs').stat().st_size,'data_source':'created on console; no bundled data image','layout':'compressed system.sfs; sparse ext4 userdata created on first Linux boot','console_tested':False,'validation':v.stdout}
(b/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='validation'},indent=2),flush=True)

shutil.copy2(b/'manifest.json','/mnt/nas/apps/ps4-android/installer/sparse-v014/manifest.json')
shutil.copy2(b/'validation.txt','/mnt/nas/apps/ps4-android/installer/sparse-v014/validation.txt')
