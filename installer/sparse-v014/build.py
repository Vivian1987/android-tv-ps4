from pathlib import Path
import subprocess,shutil,os
b=Path('/dev/shm/ps4-v014');w=Path('/home/amber/projects/ps4-android');sdk=w/'toolchains/OpenOrbis/PS4Toolchain';src=Path('/mnt/nas/apps/ps4-android/installer/sparse-v014/source');z=b/'vendor/zlib-1.3.1'
common=['clang-18','--target=x86_64-pc-freebsd12-elf','-O2','-fPIC','-funwind-tables','-mno-red-zone','-c','-DEDITION_GIB=32','-DRAW_IMAGES','-isysroot',str(sdk),'-isystem',str(sdk/'include'),'-I'+str(b),'-I'+str(z),'-I'+str(src)]
objects=[]
for f in ['install-prebuilt.c','image-copy.c','installer-ui.c']:
 obj=b/(f+'.o');subprocess.run(common+['-Wall','-Wextra','-Werror','-Wno-unused-function',str(src/f),'-o',str(obj)],check=True);objects.append(str(obj))
for f in ['privileged.o','jailbreak.o','kernelrw.o']:objects.append(str(w/'installer-pkg-build/32'/f))
subprocess.run(['ld.lld-18','-m','elf_x86_64','-pie','--script',str(sdk/'link.x'),'--eh-frame-hdr','-L'+str(sdk/'lib'),*objects,str(sdk/'lib/crt1.o'),'-lc','-lkernel','-lSceSystemService','-lSceSysmodule','-lSceVideoOut','-o',str(b/'launcher.elf')],check=True)
env=dict(os.environ,OO_PS4_TOOLCHAIN=str(sdk))
subprocess.run([str(sdk/'bin/linux/create-fself'),'-in=launcher.elf','-out=launcher.oelf','--eboot','eboot.bin','--paid','0x3800000000000011'],cwd=b,env=env,check=True)
print('Prebuilt-image installer and native GUI compiled and linked')