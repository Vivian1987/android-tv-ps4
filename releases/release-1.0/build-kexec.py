#!/usr/bin/env python3
"""Compile the pinned v25.1 source with bounded allocation/ownership handling."""
from pathlib import Path
import subprocess, sys, hashlib, json
root=Path(__file__).resolve().parent
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
source=root/'loader-source/linux/ps4-kexec-common'
subprocess.run(['make','-C',str(source),'FW_DEFINE=PS4_13_52',
    'BUILD_DIR='+str(out/'kexec'),'clean'],check=True)
subprocess.run(['make','-C',str(source),'FW_DEFINE=PS4_13_52',
    'BUILD_DIR='+str(out/'kexec'),
    'EXTRA_CFLAGS=-fcf-protection=none -mno-sse -mno-sse2 -mno-mmx -msoft-float'],check=True)
blob=(out/'kexec/kexec.bin').read_bytes()
assert 0<len(blob)<128*1024
elf=out/'kexec/kexec.elf'
relocations=subprocess.check_output(['readelf','-r',str(elf)],text=True)
assert 'There are no relocations' in relocations,relocations
symbols=subprocess.check_output(['nm','-n',str(elf)],text=True).splitlines()
entry=[int(x.split()[0],16) for x in symbols if x.split()[-1]=='kexec_init']
assert entry==[0],entry
rows=[','.join('0x%02x'%b for b in blob[i:i+16]) for i in range(0,len(blob),16)]
(out/'kexec-1352-image.h').write_text('static const unsigned char kexec_1352_image[]={\n'+',\n'.join(rows)+'\n};\n')
manifest={'upstream':(root/'loader-source/UPSTREAM').read_text().splitlines(),
 'blob_sha256':hashlib.sha256(blob).hexdigest(),'blob_bytes':len(blob),
 'source_sha256':{str(p.relative_to(root/'loader-source')):hashlib.sha256(p.read_bytes()).hexdigest()
  for p in sorted((root/'loader-source').rglob('*')) if p.is_file()}}
(out/'kexec-build.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Source-built loader:',len(blob),'bytes;',manifest['blob_sha256'])
