#!/usr/bin/env python3
"""Compile the launcher/payload helpers from pinned source and make a clean template."""
from pathlib import Path
import argparse, hashlib, json, shutil, struct, subprocess
ROOT=Path(__file__).resolve().parent
PINS={'libjbc':'4dd18714fa7af7e15813d6a11537b60bb8c6f79c','payload_sdk':'b7326416c23ce14639e9180a24093bdc5eedb579'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser()
    for name in ['sdk','libjbc','payload-sdk','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();sdk=a.sdk.resolve();native=out/'objects';probe=out/'payload';template=out/'template'
    for name in ['libjbc','payload_sdk']:
        dep=getattr(a,name).resolve()
        revision=subprocess.check_output(['git','-C',str(dep),'rev-parse','HEAD'],text=True).strip()
        if revision!=PINS[name]:raise SystemExit(name+' must be checked out at '+PINS[name])
    for path in [native,probe,template/'sce_sys/about',template/'sce_module']:path.mkdir(parents=True,exist_ok=True)
    flags=['clang-18','--target=x86_64-pc-freebsd12-elf','-O0','-fPIC','-funwind-tables','-mno-red-zone','-c','-isysroot',str(sdk),'-isystem',str(sdk/'include'),'-I'+str(a.libjbc.resolve())]
    for name,source in [('privileged',ROOT/'helpers/privileged.c'),('jailbreak',a.libjbc/'jailbreak.c'),('kernelrw',a.libjbc/'kernelrw.c')]:
        subprocess.run(flags+[str(source),'-o',str(native/(name+'.o'))],check=True)
    flat=a.payload_sdk/'libPS4'
    for header in (flat/'include').glob('*.h'):(probe/header.name).write_text(header.read_text().replace('movq ','mov '))
    flags=['gcc','-Os','-std=gnu11','-ffunction-sections','-fdata-sections','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-asynchronous-unwind-tables','-mno-red-zone','-masm=intel','-march=btver2','-mcmodel=small','-fPIE','-fvisibility=hidden','-I'+str(probe),'-I'+str(flat/'include'),'-Wno-incompatible-pointer-types']
    for name in ['kernel.c','module.c','file.c','syscall.s']:
        source=probe/name;source.write_text((flat/'source'/name).read_text().replace('movq ','mov '))
        subprocess.run(flags+['-c',str(source),'-o',str(source.with_suffix('.o'))],check=True)
    for name in ['start.s','memory.c']:
        subprocess.run(flags+['-c',str(ROOT/'helpers'/name),'-o',str(probe/(Path(name).stem+'.o'))],check=True)
    for name in ['sce_sys/about/right.sprx','sce_module/libc.prx','sce_module/libSceFios2.prx']:
        shutil.copyfile(sdk/'samples/hello_world'/name,template/name)
    # Minimal product SFO; the package builder fills the same title/version values.
    values={'APP_TYPE':1,'APP_VER':'1.00','ATTRIBUTE':0,'CATEGORY':'gd','CONTENT_ID':'IV0000-ATVX13001_00-PS4ANDROIDTV0000','DOWNLOAD_DATA_SIZE':0,'SYSTEM_VER':0,'TITLE':'Android TV for PS4','TITLE_ID':'ATVX13001','VERSION':'1.00'}
    sizes={'APP_VER':8,'CATEGORY':4,'CONTENT_ID':48,'TITLE':128,'TITLE_ID':12,'VERSION':8}
    keys=bytearray();data=bytearray();rows=[]
    for key,value in sorted(values.items()):
        ko=len(keys);keys.extend(key.encode()+b'\0');do=len(data)
        if isinstance(value,int):raw=struct.pack('<I',value);fmt=0x404;maximum=4
        else:raw=value.encode()+b'\0';fmt=0x204;maximum=sizes[key]
        rows.append(struct.pack('<HHIII',ko,fmt,len(raw),maximum,do));data.extend(raw+b'\0'*(maximum-len(raw)))
    keyoff=20+16*len(rows);dataoff=(keyoff+len(keys)+3)&~3
    sfo=struct.pack('<5I',0x46535000,0x101,keyoff,dataoff,len(rows))+b''.join(rows)+keys
    sfo+=b'\0'*(dataoff-len(sfo));sfo+=data
    (template/'sce_sys/param.sfo').write_bytes(sfo)
    report={'dependency_commits':PINS,'objects':{str(f.relative_to(out)):digest(f) for directory in [native,probe] for f in sorted(directory.glob('*.o'))},'template':{str(f.relative_to(template)):digest(f) for f in template.rglob('*') if f.is_file()}}
    (out/'helper-build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
