from pathlib import Path
import hashlib,shutil,os,json,subprocess,xml.etree.ElementTree as E
from PIL import Image
root=Path('/mnt/nas/apps/ps4-android/installer');old=root/'sparse-v011';new=root/'sparse-v012';b=Path('/dev/shm/ps4-v012');(b/'assets').mkdir(parents=True,exist_ok=True)
ram=Path('/dev/shm/ps4-v009/IV0000-ATVX13001_00-PS4ANDROIDTV0000.pkg');archive=root/'sparse-v009'/ram.name
if ram.exists():
 assert hashlib.file_digest(ram.open('rb'),'sha256').hexdigest()==hashlib.file_digest(archive.open('rb'),'sha256').hexdigest();ram.unlink()
shutil.copytree(old/'source',new/'source',dirs_exist_ok=True)
for n in ['build.py','image-metadata.h','upload.py']:(new/n).write_text((old/n).read_text().replace('v011','v012'))
shutil.copy2(new/'image-metadata.h',b/'image-metadata.h')
for p in Path('/dev/shm/ps4-v011/assets').iterdir():
 dest=b/'assets'/p.name
 if not dest.exists():os.link(p,dest)
# Native VideoOut is rectangular: use a genuinely opaque, edge-to-edge background.
x=E.parse(old/'installer-background.svg').getroot();ns='{http://www.w3.org/2000/svg}'
for el in list(x):
 if el.tag==ns+'rect':x.remove(el)
base=E.Element(ns+'rect',{'x':'0','y':'0','width':'1280','height':'720','fill':'url(#panel)'})
x.insert(1,base)
E.ElementTree(x).write(new/'installer-background.svg',encoding='unicode',xml_declaration=True)
subprocess.run(['inkscape',str(new/'installer-background.svg'),'--export-filename='+str(new/'installer-background.png')],check=True)
im=Image.open(new/'installer-background.png').convert('RGBA');assert im.getextrema()[3]==(255,255)
with (new/'source/installer-artwork.h').open('w') as f:
 f.write('/* Original logo assets, opaque full-frame installer background. */\nstatic const uint32_t installer_artwork[1280*720] = {\n')
 for y in range(720):f.write(','.join('0xff%02x%02x%02x'%im.getpixel((xx,y))[:3] for xx in range(1280))+',\n')
 f.write('};\n')
(new/'branding.json').write_text(json.dumps({'version':'v6','icon':'RGBA; no shadow overhang; fully transparent outer corners','installer_background':'opaque edge-to-edge, no corner border or transparency','package_background':'explicit dark matte rather than implicit white alpha discard','boot_assets':'unchanged from v010/v011','public_release':False},indent=2)+'\n')
print('v012 sources prepared; full-frame installer alpha verified opaque')
