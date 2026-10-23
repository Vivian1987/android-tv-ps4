from pathlib import Path
import os,json,hashlib,shutil,subprocess,xml.etree.ElementTree as E
root=Path('/mnt/nas/apps/ps4-android/installer');old=root/'sparse-v010';new=root/'sparse-v011';new.mkdir(exist_ok=True);b=Path('/dev/shm/ps4-v011');(b/'assets').mkdir(parents=True,exist_ok=True)
# Retire a verified RAM build artifact only; NAS copy remains authoritative.
oldram=Path('/dev/shm/ps4-v008/IV0000-ATVX13001_00-PS4ANDROIDTV0000.pkg');archive=root/'sparse-v008'/oldram.name
if oldram.exists():
 assert archive.exists() and hashlib.file_digest(oldram.open('rb'),'sha256').hexdigest()==hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
 oldram.unlink()
shutil.copytree(old/'source',new/'source',dirs_exist_ok=True)
for n in ['build.py','package.py','image-metadata.h','upload.py']:
 (new/n).write_text((old/n).read_text().replace('v010','v011').replace("'0.10'","'0.11'"))
shutil.copy2(new/'image-metadata.h',b/'image-metadata.h')
for p in Path('/dev/shm/ps4-v010/assets').iterdir():
 dest=b/'assets'/p.name
 if not dest.exists():os.link(p,dest)
# Preserve proven installer/boot logic and state marker; this revision changes presentation only.
brand=Path('/mnt/nas/apps/ps4-android/branding'); ns='{http://www.w3.org/2000/svg}'
x=E.parse(brand/'banner-official-assets-v5.svg').getroot()
images=x.findall(ns+'image');texts=x.findall(ns+'text')
for el,coords in zip(images,[(380,55,520,87.1),(550,205,180,36.75)]):
 for k,v in zip(['x','y','width','height'],coords):el.set(k,str(v))
texts[0].set('x','640');texts[0].set('y','180');texts[0].set('font-size','23')
E.ElementTree(x).write(new/'installer-background.svg',encoding='unicode',xml_declaration=True)
subprocess.run(['inkscape',str(new/'installer-background.svg'),'--export-filename='+str(new/'installer-background.png')],check=True)
from PIL import Image
im=Image.open(new/'installer-background.png').convert('RGB');assert im.size==(1280,720)
# Lossless pixel encoding for the native framebuffer, not a redraw of the logos.
with (new/'source/installer-artwork.h').open('w') as f:
 f.write('/* Generated from installer-background.svg using original logo assets. */\nstatic const uint32_t installer_artwork[1280*720] = {\n')
 for y in range(720):
  f.write(','.join('0xff%02x%02x%02x'%im.getpixel((xx,y)) for xx in range(1280))+',\n')
 f.write('};\n')
p=new/'source/installer-ui.c';s=p.read_text().replace('#include <string.h>','#include <string.h>\n#include "installer-artwork.h"')
a=s.index(' rectangle(0,0,WIDTH,HEIGHT,0xff10202c);');z=s.index(' /* Wrap status',a)
s=s[:a]+' memcpy(buffers[buffer_index],installer_artwork,FRAME_BYTES);\n text(80,270,3,"Setup progress",0xfff4f8fa);\n'+s[z:]
s=s.replace('int y=300','int y=320').replace('y<390','y<410').replace('80,420','80,450').replace('80,480','80,510').replace('0xff50ddb0','0xff6ba5d7');p.write_text(s)
p=new/'package.py';s=p.read_text();a=s.index('img=Image.new');z=s.index('def run(args)',a)
s=s[:a]+'''branding=Path('/mnt/nas/apps/ps4-android/branding')
Image.open(branding/'icon-official-assets-v5.png').convert('RGB').save(b/'sce_sys/icon0.png')
subprocess.run(['inkscape',str(branding/'banner-official-assets-v5.svg'),'--export-width=1920','--export-height=1080','--export-filename='+str(b/'sce_sys/pic1.png')],check=True)
Image.open(b/'sce_sys/pic1.png').convert('RGB').save(b/'sce_sys/pic1.png')
'''+s[z:]
s=s.replace("'sce_sys/icon0.png','sce_module", "'sce_sys/icon0.png','sce_sys/pic1.png','sce_module").replace('PS4 Android TV - Internal Test','Android TV for PS4')
p.write_text(s)
(new/'branding.json').write_text(json.dumps({'selected':'v5','icon':'sce_sys/icon0.png','package_background':'sce_sys/pic1.png','installer_background':'installer-background.png','real_logo_sources':str(brand/'official-asset-sources.json'),'base_logic':'v010 unchanged, including all three startup fixes','public_release':False},indent=2)+'\n')
print('Branded v011 sources prepared')
