#!/usr/bin/env python3
from pathlib import Path
import argparse,subprocess,zipfile
p=argparse.ArgumentParser();p.add_argument('--android-jar',type=Path,required=True);p.add_argument('--tools',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--keystore',type=Path,required=True);p.add_argument('--password-file',type=Path,required=True);a=p.parse_args()
s=Path(__file__).resolve().parent;b=a.build.resolve();(b/'classes').mkdir(parents=True,exist_ok=True);(b/'dex').mkdir(exist_ok=True)
def run(cmd):subprocess.run([str(x) for x in cmd],check=True)
run(['javac','--release','8','-cp',a.android_jar,'-d',b/'classes',*sorted((s/'src').rglob('*.java'))])
run([a.tools/'d8','--min-api','33','--lib',a.android_jar,'--output',b/'dex',*sorted((b/'classes').rglob('*.class'))])
run([a.tools/'aapt2','link','-I',a.android_jar,'--manifest',s/'AndroidManifest.xml','-o',b/'unsigned.apk'])
with zipfile.ZipFile(b/'unsigned.apk','a',zipfile.ZIP_DEFLATED) as z:z.write(b/'dex/classes.dex','classes.dex')
run([a.tools/'zipalign','-f','4',b/'unsigned.apk',b/'aligned.apk'])
run([a.tools/'apksigner','sign','--ks',a.keystore,'--ks-pass','file:'+str(a.password_file),'--out',b/'AtvConnectivity.apk',b/'aligned.apk'])
run([a.tools/'apksigner','verify','--verbose',b/'AtvConnectivity.apk'])
print(b/'AtvConnectivity.apk')
