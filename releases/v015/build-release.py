#!/usr/bin/env python3
"""Build the 32 GiB v0.15 candidate using explicit, operator-supplied toolchain inputs."""
from pathlib import Path
import argparse,os,subprocess,shutil,hashlib,json
p=argparse.ArgumentParser()
for arg in ['sdk','template','objects','runtime','assets','build','output']:p.add_argument('--'+arg,type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parent;b=a.build.resolve();b.mkdir(parents=True,exist_ok=True);out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);sdk=a.sdk.resolve();tools=sdk/'bin/linux';src=root/'source';cid='IV0000-ATVX13001_00-PS4ANDROIDTV0000'
assert (a.assets/'data-gib.txt').read_text()=='32\n'
for directory in ['sce_sys','sce_module']:shutil.copytree(a.template/directory,b/directory,dirs_exist_ok=True)
shutil.copy2(root/'artwork/icon0.png',b/'sce_sys/icon0.png');shutil.copy2(root/'artwork/pic1.png',b/'sce_sys/pic1.png')
shutil.copy2(root/'image-metadata.h',b/'image-metadata.h')
if (b/'assets').resolve()!=a.assets.resolve():
 shutil.copytree(a.assets,b/'assets',dirs_exist_ok=True)
common=['clang-18','--target=x86_64-pc-freebsd12-elf','-O2','-fPIC','-funwind-tables','-mno-red-zone','-c','-DEDITION_GIB=32','-DRAW_IMAGES','-isysroot',str(sdk),'-isystem',str(sdk/'include'),'-I'+str(b),'-I'+str(src),'-Wall','-Wextra','-Werror','-Wno-unused-function']
objects=[]
for name in ['install-prebuilt.c','image-copy.c','installer-ui.c']:
 dest=b/(name+'.o');subprocess.run(common+[str(src/name),'-o',str(dest)],check=True);objects.append(str(dest))
# Existing privileged helper objects are pinned below. Their source/provenance
# must be reconciled before treating this as a complete public source release.
helper_hashes={}
for name in ['privileged.o','jailbreak.o','kernelrw.o']:
 f=a.objects/name;helper_hashes[name]=hashlib.file_digest(f.open('rb'),'sha256').hexdigest();objects.append(str(f.resolve()))
subprocess.run(['ld.lld-18','-m','elf_x86_64','-pie','--script',str(sdk/'link.x'),'--eh-frame-hdr','-L'+str(sdk/'lib'),*objects,str(sdk/'lib/crt1.o'),'-lc','-lkernel','-lSceSystemService','-lSceSysmodule','-lSceVideoOut','-o',str(b/'launcher.elf')],check=True)
env=dict(os.environ,OO_PS4_TOOLCHAIN=str(sdk),DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1',LD_LIBRARY_PATH=str(a.runtime.resolve()))
def run(args):subprocess.run([str(x) for x in args],cwd=b,env=env,check=True)
run([tools/'create-fself','-in=launcher.elf','-out=launcher.oelf','--eboot','eboot.bin','--paid','0x3800000000000011'])
for key,value in [('APP_VER','0.15'),('VERSION','0.15'),('TITLE','Android TV for PS4')]:run([tools/'PkgTool.Core','sfo_setentry','sce_sys/param.sfo',key,'--type','Utf8','--maxsize','128' if key=='TITLE' else '8','--value',value])
files=['eboot.bin','sce_sys/about/right.sprx','sce_sys/param.sfo','sce_sys/icon0.png','sce_sys/pic1.png','sce_module/libc.prx','sce_module/libSceFios2.prx']+['assets/'+x.name for x in sorted((b/'assets').iterdir())]
run([tools/'create-gp4','-out','pkg.gp4','--content-id='+cid,'--files',' '.join(files)])
run([tools/'PkgTool.Core','pkg_build','pkg.gp4','.'])
f=b/(cid+'.pkg');v=subprocess.run([str(tools/'PkgTool.Core'),'pkg_validate',str(f)],cwd=b,env=env,text=True,capture_output=True,check=True);assert '[FAIL]' not in v.stdout and '[ERROR]' not in v.stdout
(out/'validation.txt').write_text(v.stdout)
name='Android-TV-PS4-13-v0.15-32GiB.pkg';sha=hashlib.file_digest(f.open('rb'),'sha256').hexdigest();dest=out/name;shutil.copyfile(f,dest);assert hashlib.file_digest(dest.open('rb'),'sha256').hexdigest()==sha
manifest={'release':'0.15','edition_gib':32,'logical_data_bytes':34359738368,'file':name,'bytes':dest.stat().st_size,'sha256':sha,'content_id':cid,'package_validation':'passed','console_tested':False,'public_release_ready':False,'helper_object_hashes':helper_hashes,'assets':{x.name:hashlib.file_digest(x.open('rb'),'sha256').hexdigest() for x in (b/'assets').iterdir()}}
(out/'release.json').write_text(json.dumps(manifest,indent=2)+'\n');(out/'SHA256SUMS').write_text(sha+'  '+name+'\n');print(json.dumps(manifest,indent=2),flush=True)
