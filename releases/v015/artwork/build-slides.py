from pathlib import Path
import base64,subprocess
from PIL import Image
root=Path(__file__).resolve().parents[1];a=root/'artwork';branding=a
def url(path):return 'data:image/png;base64,'+base64.b64encode(Path(path).read_bytes()).decode()
logo=url(branding/'android-tv-official.png');ps4=url(branding/'ps4-official.png');welcome=url(a/'android-first-run.png')
base=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1280" height="720" viewBox="0 0 1280 720">
<defs><linearGradient id="bg" x2="1" y2=".5"><stop stop-color="#071327"/><stop offset="1" stop-color="#123c73"/></linearGradient><linearGradient id="glass" x2=".9" y2="1"><stop stop-color="#273f60"/><stop offset="1" stop-color="#101b2c"/></linearGradient><radialGradient id="light"><stop stop-color="#337dd1" stop-opacity=".35"/><stop offset="1" stop-color="#337dd1" stop-opacity="0"/></radialGradient></defs>
<rect width="1280" height="720" fill="url(#bg)"/><ellipse cx="920" cy="310" rx="480" ry="310" fill="url(#light)"/>
<image x="64" y="48" width="270" height="46" xlink:href="{logo}"/><image x="1038" y="57" width="178" height="36" xlink:href="{ps4}"/>
<path d="M64 123H1216" stroke="#ffffff" stroke-opacity=".12"/>
<rect y="538" width="1280" height="182" fill="#080f1d"/><path d="M0 538H1280" stroke="#3a5274" stroke-opacity=".7"/>
'''
def text(y,content,size=22,color='#c7d6e9',weight=400):return f'<text x="64" y="{y}" font-family="Roboto" font-size="{size}" font-weight="{weight}" fill="{color}">{content}</text>'
slides=[]
slides.append(base+text(196,'ANDROID TV 13',16,'#7ebeff')+text(254,'Your apps.',42,'#ffffff',500)+text(306,'On your PS4.',42,'#ffffff',500)+text(364,'Set up Android TV and install')+text(398,'the apps you want to use.')+f'''<rect x="510" y="163" width="706" height="341" rx="8" fill="#02050a" stroke="#668ab7" stroke-opacity=".6"/>
<image x="518" y="171" width="690" height="325" preserveAspectRatio="xMidYMid meet" xlink:href="{welcome}"/>
</svg>''')
controller=f'''<image x="538" y="139" width="650" height="350" preserveAspectRatio="xMidYMid meet" xlink:href="{url(a/'dualshock4-jet-black-transparent.png')}"/>'''
slides.append(base+text(196,'CONTROLLER NAVIGATION',16,'#7ebeff')+text(254,'Your controller.',42,'#ffffff',500)+text(306,'Your remote.',42,'#ffffff',500)+text(364,'Navigate with the D-pad.')+text(398,'Press the PS button to go Home.')+controller+'</svg>')
console='''<g transform="translate(590 185)"><path d="M55 52L470 12L574 117L158 159Z" fill="#334c69" stroke="#88a4bf"/><path d="M55 52L158 159V275L55 168Z" fill="#101d31"/><path d="M158 159L574 117V234L158 275Z" fill="#1c2d44" stroke="#4f6884"/><path d="M55 111L158 218L574 176" stroke="#080f1d" stroke-width="12"/><path d="M158 215L574 173" stroke="#5cbaff" stroke-width="3"/><path d="M183 248L265 240" stroke="#0a101a" stroke-width="6"/>
<text x="330" y="326" text-anchor="middle" font-family="Roboto" font-size="24" fill="#c7d6e9">Internal storage</text></g>'''
slides.append(base+text(196,'STANDALONE INSTALLATION',16,'#7ebeff')+text(254,'Installed here.',42,'#ffffff',500)+text(306,'Ready next time.',42,'#ffffff',500)+text(364,'Load GoldHEN, then launch Android TV')+text(398,'from your PS4 home screen.')+console+'</svg>')
with (root/'source/installer-artwork.h').open('w') as f:
 f.write('/* Native installer slides; generated from SVG artwork. */\nstatic const uint32_t installer_slides[3][1280*720] = {\n')
 for i,svg in enumerate(slides):
  (a/f'slide-{i}.svg').write_text(svg);subprocess.run(['inkscape',str(a/f'slide-{i}.svg'),'--export-filename='+str(a/f'slide-{i}.png')],check=True,stdout=subprocess.DEVNULL)
  im=Image.open(a/f'slide-{i}.png').convert('RGB');f.write('{\n')
  for y in range(720):f.write(','.join('0xff%02x%02x%02x'%im.getpixel((x,y)) for x in range(1280))+',\n')
  f.write('},\n')
 f.write('};\n')
# README preview excludes the bottom area reserved for live installer progress.
preview=slides[1].replace('height="720" viewBox="0 0 1280 720"', 'height="538" viewBox="0 0 1280 538"', 1)
(a/'controller-preview.svg').write_text(preview)
subprocess.run(['inkscape',str(a/'controller-preview.svg'),'--export-filename='+str(a/'controller-preview.png')],check=True,stdout=subprocess.DEVNULL)
print('Installer slides and cropped README preview rendered')
