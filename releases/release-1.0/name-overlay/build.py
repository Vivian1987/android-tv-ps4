#!/usr/bin/env python3
"""Build a static overlay. By default, the one that names new installations "PlayStation 4";
--source screensaver-overlay --name AtvScreensaverOverlay.apk builds the screensaver defaults."""
from pathlib import Path
import argparse,subprocess
p=argparse.ArgumentParser();p.add_argument('--android-jar',type=Path,required=True);p.add_argument('--tools',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--key',type=Path,required=True);p.add_argument('--cert',type=Path,required=True)
p.add_argument('--source',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--name',default='AtvDeviceNameOverlay.apk');a=p.parse_args()
s=a.source.resolve();b=a.build.resolve();b.mkdir(parents=True,exist_ok=True)
def run(cmd):subprocess.run([str(x) for x in cmd],check=True)
run([a.tools/'aapt2','compile','--dir',s/'res','-o',b/'res.zip'])
run([a.tools/'aapt2','link','-I',a.android_jar,'--manifest',s/'AndroidManifest.xml','-o',b/'unsigned.apk',b/'res.zip'])
run([a.tools/'zipalign','-f','4',b/'unsigned.apk',b/'aligned.apk'])
run([a.tools/'apksigner','sign','--key',a.key,'--cert',a.cert,'--out',b/a.name,b/'aligned.apk'])
print(b/a.name)
