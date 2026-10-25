#!/usr/bin/env python3
"""Build the static overlay that names new installations "PlayStation 4"."""
from pathlib import Path
import argparse,subprocess
p=argparse.ArgumentParser();p.add_argument('--android-jar',type=Path,required=True);p.add_argument('--tools',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--key',type=Path,required=True);p.add_argument('--cert',type=Path,required=True);a=p.parse_args()
s=Path(__file__).resolve().parent;b=a.build.resolve();b.mkdir(parents=True,exist_ok=True)
def run(cmd):subprocess.run([str(x) for x in cmd],check=True)
run([a.tools/'aapt2','compile','--dir',s/'res','-o',b/'res.zip'])
run([a.tools/'aapt2','link','-I',a.android_jar,'--manifest',s/'AndroidManifest.xml','-o',b/'unsigned.apk',b/'res.zip'])
run([a.tools/'zipalign','-f','4',b/'unsigned.apk',b/'aligned.apk'])
run([a.tools/'apksigner','sign','--key',a.key,'--cert',a.cert,'--out',b/'AtvDeviceNameOverlay.apk',b/'aligned.apk'])
print(b/'AtvDeviceNameOverlay.apk')
