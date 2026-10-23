"""Download a pinned reference release without executing upstream code."""
import json,urllib.request,hashlib,concurrent.futures
from pathlib import Path
root=Path(__file__).resolve().parent;release=json.loads((root/'evidence/loader-release.json').read_text())
wanted={'bzImage-belize-7.1.7','bzImage-baikal-7.0.8','initramfs.cpio.gz','kernel-7.1.7-Strawberry-General.config','linux-1024mb.elf','linux-2048mb.elf','SHA256SUMS'}
def fetch(a):
 dest=root/'downloads'/a['name'];tmp=dest.with_suffix('.part')
 with urllib.request.urlopen(a['browser_download_url'],timeout=60) as r,tmp.open('wb') as out:
  while chunk:=r.read(1024*1024):out.write(chunk)
 assert tmp.stat().st_size==a['size']
 digest=hashlib.sha256(tmp.read_bytes()).hexdigest();expected=a.get('digest')
 if expected and expected.startswith('sha256:'):assert digest==expected.split(':',1)[1]
 tmp.replace(dest);return {'name':a['name'],'bytes':dest.stat().st_size,'sha256':digest,'github_digest_matches':bool(expected)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,[a for a in release['assets'] if a['name'] in wanted]))
(root/'evidence/download-manifest.json').write_text(json.dumps({'release':release['tag_name'],'source':release['html_url'],'files':results},indent=2))
for r in results:print(r['name'],r['bytes'],'downloaded')
