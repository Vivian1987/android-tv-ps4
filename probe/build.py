import pathlib,subprocess,re,json,hashlib
root=pathlib.Path(__file__).resolve().parent;sdk=root.parents[1]/'spaghettikart-ps4/flat-sdk-source/libPS4';build=pathlib.Path('/home/amber/projects/ps4-android/probe-build')
for h in (sdk/'include').glob('*.h'):
 s=h.read_text().replace('movq ','mov ');(build/h.name).write_text(s)
flags=['-Os','-std=gnu11','-ffunction-sections','-fdata-sections','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-asynchronous-unwind-tables','-mno-red-zone','-masm=intel','-march=btver2','-mcmodel=small','-fPIE','-fvisibility=hidden','-I'+str(build),'-I'+str(sdk/'include'),'-Wno-incompatible-pointer-types']
objects=[]
for name in ['kernel.c','module.c','file.c','syscall.s']:
 src=build/name;src.write_text((sdk/'source'/name).read_text().replace('movq ','mov '));obj=src.with_suffix('.o');subprocess.run(['gcc',*flags,'-c',str(src),'-o',str(obj)],check=True,capture_output=True);objects.append(obj)
for src in [root/'hardware.c',root.parents[1]/'spaghettikart-ps4/control/start.s',root.parents[1]/'spaghettikart-ps4/control/memory.c']:
 obj=build/(src.stem+'.o');subprocess.run(['gcc',*flags,'-c',str(src),'-o',str(obj)],check=True,capture_output=True);objects.append(obj)
elf=build/'hardware.elf';subprocess.run(['ld','-T',str(root.parents[1]/'spaghettikart-ps4/control/linker.x'),'--gc-sections','--build-id=none','-o',str(elf),*[str(x) for x in objects]],check=True)
readout=subprocess.check_output(['readelf','-h','-r',str(elf)],text=True);assert '0x0' in readout and 'There are no relocations' in readout
out=build/'hardware.bin';subprocess.run(['objcopy','-O','binary',str(elf),str(out)],check=True);print(json.dumps({'path':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'relocations':False}))
