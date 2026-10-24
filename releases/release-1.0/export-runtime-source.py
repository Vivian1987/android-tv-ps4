#!/usr/bin/env python3
"""Export auditable text from the hash-pinned packaged initramfs.

This does not rebuild the archive or copy console-generated state. Binary
helpers remain externally supplied inputs, identified in runtime/manifest.json.
"""
from pathlib import Path
import argparse, hashlib, json, lzma, runpy
ROOT = Path(__file__).resolve().parent
NAMES = ['init', 'usr/sbin/androidtv-ps4-start']
NAMES += ['opt/androidtv-ps4/'+n for n in [
    'android-child.sh', 'autoboot.sh', 'androidtv-ps4.rc', 'bpfloader.rc',
    'init.rc', 'init.sh', 'init.android_x86_64.rc', 'controller-home.sh',
    'resolution.sh', 'system-build.prop', 'vendor-build.prop', 'product-build.prop',
    'hwcomposer.rc', 'bluetooth.rc', 'bluetooth-scheduling.rc',
    'mediaextractor.policy', 'androidtv-logging.rc', 'device-name.sh', 'device-name.rc', 'bundled-apps.txt']]
def main():
    p=argparse.ArgumentParser();p.add_argument('--initramfs',type=Path,required=True)
    p.add_argument('--output',type=Path,default=ROOT/'runtime');a=p.parse_args()
    raw=a.initramfs.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    expected=json.loads((ROOT/'runtime-inputs.json').read_text())['initramfs_sha256']
    if sha!=expected:raise SystemExit('Initramfs does not match runtime-inputs.json')
    entries=runpy.run_path(str(ROOT/'prepare-runtime.py'))['unpack'](lzma.decompress(raw))
    report={'initramfs_sha256':sha,'text_files':{},'binary_helpers':{}}
    for name in NAMES:
        fields,data=entries[name];data.decode('utf-8')
        if b'\0' in data:raise ValueError('Binary in text export: '+name)
        dest=a.output/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        report['text_files'][name]=hashlib.sha256(data).hexdigest()
    for name in ['usr/sbin/android-supervisor','usr/sbin/androidtv-display-ready',
                 'opt/androidtv-ps4/composer','opt/androidtv-ps4/gralloc-gbm-yv12-stride.so',
                 'opt/androidtv-ps4/binder-devices','opt/androidtv-ps4/AtvConnectivity.apk']:
        report['binary_helpers'][name]=hashlib.sha256(entries[name][1]).hexdigest()
    (a.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Exported',len(NAMES),'hash-verified runtime text files')
if __name__=='__main__':main()
