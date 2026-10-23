from pathlib import Path
import base64,json,subprocess,shutil
b=Path(__file__).resolve().parent
uri=lambda name:'data:image/png;base64,'+base64.b64encode((b/name).read_bytes()).decode()
a=uri('android-tv-official.png');p=uri('ps4-official.png')
def image(u,x,y,w,h):return f'<image xlink:href="{u}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"/>'
def svg(w,h,content):return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#1c2b40"/><stop offset="1" stop-color="#0b1424"/></linearGradient><radialGradient id="glow"><stop stop-color="#245079" stop-opacity=".38"/><stop offset="1" stop-color="#18334b" stop-opacity="0"/></radialGradient><linearGradient id="edge" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#7899b6" stop-opacity=".32"/><stop offset="1" stop-color="#7899b6" stop-opacity=".06"/></linearGradient></defs>{content}</svg>'''
def panel(x,y,w,h,r):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#panel)"/><rect x="{x+.75}" y="{y+.75}" width="{w-1.5}" height="{h-1.5}" rx="{r}" fill="none" stroke="url(#edge)" stroke-width="1.5"/><ellipse cx="{x+w/2}" cy="{y+h*.37}" rx="{w*.46}" ry="{h*.34}" fill="url(#glow)"/>'
def text(x,y,size):return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="DejaVu Sans,sans-serif" font-size="{size}" fill="#b9c7d6">for</text>'
# Centre each complete logo stack in its own panel; preserve logo aspect ratios.
board='<rect width="1800" height="900" fill="#0b1019"/>'+panel(70,250,400,400,48)+panel(540,200,1190,500,16)
board+=image(a,110,356,320,53.6)+text(270,461,25)+image(p,150,495,240,49)
board+=image(a,695,277,880,147.4)+text(1135,485,30)+image(p,895,525,480,98)
icon=panel(0,0,512,512,40)+image(a,48,123,416,69.7)+text(256,259,28)+image(p,96,305,320,65.333)
banner=panel(0,0,1280,720,18)+image(a,170,200,940,157.5)+text(640,421,32)+image(p,380,465,520,106.167)
for name,w,h,body in [('identity-official-assets-v6',1800,900,board),('icon-official-assets-v6',512,512,icon),('banner-official-assets-v6',1280,720,banner)]:
 path=b/(name+'.svg');path.write_text(svg(w,h,body))
 subprocess.run(['inkscape',str(path),'--export-filename='+str(b/(name+'.png'))],check=True)
(pth:=b/'selected.json').write_text(json.dumps({'version':'v6','based_on':'v3','artwork':'identity-official-assets-v6.png','artwork_source':'identity-official-assets-v6.svg','icon':'icon-official-assets-v6.png','banner':'banner-official-assets-v6.png','note':'Centered original logo assets, restrained blue depth; no logo redraws.'},indent=2)+'\n')
shutil.copy2(b/'identity-official-assets-v6.png','/home/amber/Pictures/PS4-Android-TV/identity-official-assets-v6.png')
