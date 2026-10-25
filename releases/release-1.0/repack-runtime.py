#!/usr/bin/env python3
"""Rebuild runtime text and the power supervisor using verified package assets.

The Android system and hardware binaries remain pinned external inputs. This
path lets contributors edit the published runtime snapshot without an older,
unpublished base archive. Outputs go to a new directory; source assets survive.
"""
from pathlib import Path
import argparse,gzip,hashlib,io,json,lzma,os,runpy,subprocess,tarfile,tempfile
ROOT=Path(__file__).resolve().parent

def digest(data):return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--assets',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--runtime-tree',type=Path,default=ROOT/'runtime')
    p.add_argument('--additions',type=Path,help='directory mirroring runtime-additions.json paths');a=p.parse_args()
    manifest=json.loads((ROOT/'runtime-inputs.json').read_text())
    original=(a.assets/'initramfs.cpio.xz').read_bytes();parent_sha=digest(original)
    if parent_sha!=manifest['initramfs_sha256']:raise SystemExit('Input runtime does not match runtime-inputs.json')
    snapshot=json.loads((a.runtime_tree/'manifest.json').read_text())
    if snapshot['initramfs_sha256']!=parent_sha:raise SystemExit('Runtime snapshot belongs to a different archive')
    if a.output.exists() and any(a.output.iterdir()):raise SystemExit('Output directory must be empty')
    a.output.mkdir(parents=True,exist_ok=True)
    api=runpy.run_path(str(ROOT/'prepare-runtime.py'));entries=api['unpack'](lzma.decompress(original))
    before={n:digest(data) for n,(_,data) in entries.items()}
    for name in snapshot['text_files']:
        if name.startswith('/') or '..' in Path(name).parts or name not in entries:raise ValueError('Invalid snapshot path')
        data=(a.runtime_tree/name).read_bytes();data.decode('utf-8')
        if b'\0' in data:raise ValueError('Binary in text snapshot')
        if data.startswith(b'#!/bin/sh'):subprocess.run(['busybox','sh','-n'],input=data,check=True)
        entries[name]=(entries[name][0],data)
    source=ROOT/'power/android-supervisor.c'
    with tempfile.TemporaryDirectory() as tmp:
        binary=Path(tmp)/'android-supervisor'
        subprocess.run(['cc','-static','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],check=True)
        power=binary.read_bytes()
    name='usr/sbin/android-supervisor';entries[name]=(entries[name][0],power)
    gralloc=runpy.run_path(str(ROOT/'runtime-source/patch-gralloc-yv12.py'))
    name='opt/androidtv-ps4/gralloc-gbm-yv12-stride.so'
    if digest(entries[name][1])!=gralloc['PATCHED_SHA']:entries[name]=(entries[name][0],gralloc['patch'](entries[name][1]))
    # Hardware-support files (Slim/Pro Wi-Fi and Bluetooth) that the base
    # runtime lacks. Each must match runtime-additions.json exactly.
    additions=json.loads((ROOT/'runtime-additions.json').read_text())['files']
    if additions and not a.additions:raise SystemExit('--additions is required for runtime-additions.json')
    inode=max(f[0] for f,_ in entries.values())+1
    dir_fields=entries['lib/firmware'][0];file_fields=entries['lib/firmware/regulatory.db'][0]
    drive=io.BytesIO()
    with tarfile.open(fileobj=drive,mode='w',format=tarfile.USTAR_FORMAT) as tar:
        for name,item in sorted(additions.items()):
            if item.get('location')!='drive':continue
            data=(a.additions/name).read_bytes()
            if digest(data)!=item['sha256']:raise SystemExit('Addition does not match runtime-additions.json: '+name)
            # Drive files never ship in the initramfs, including from an older parent.
            entries.pop(name,None)
            info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0
            tar.addfile(info,io.BytesIO(data))
    wifi=gzip.compress(drive.getvalue(),mtime=0)
    for name,item in sorted(additions.items()):
        if item.get('location')=='drive':continue
        data=(a.additions/name).read_bytes()
        if digest(data)!=item['sha256']:raise SystemExit('Addition does not match runtime-additions.json: '+name)
        parts=name.split('/')
        for depth in range(1,len(parts)):
            parent='/'.join(parts[:depth])
            if parent not in entries:
                fields=dir_fields.copy();fields[0]=inode;inode+=1;entries[parent]=(fields,b'')
        fields=file_fields.copy();fields[0]=inode;inode+=1;fields[1]=0o100000|int(item.get('mode','0644'),8)
        entries[name]=(fields,data)
    raw=api['pack'](entries)
    compressed=lzma.compress(raw,format=lzma.FORMAT_XZ,check=lzma.CHECK_CRC32,filters=[{'id':lzma.FILTER_X86},{'id':lzma.FILTER_LZMA2,'dict_size':8*1024*1024,'preset':6}])
    if len(compressed)>16*1024*1024:raise ValueError('Unexpected initramfs growth; review boot memory budget')
    for asset in a.assets.iterdir():
        if not asset.is_file():raise ValueError('Unexpected asset directory')
        if asset.name not in ('initramfs.cpio.xz','mt7668-wifi.tar.gz'):os.link(asset,a.output/asset.name)
    (a.output/'initramfs.cpio.xz').write_bytes(compressed)
    (a.output/'mt7668-wifi.tar.gz').write_bytes(wifi)
    manifest.update(parent_initramfs_sha256=parent_sha,initramfs_sha256=digest(compressed),initramfs_bytes=len(compressed),expanded_sha256=digest(raw),expanded_bytes=len(raw),changed_entries=[n for n,(_,data) in entries.items() if before.get(n)!=digest(data)],power_supervisor_sha256=digest(power),power_supervisor_source_sha256=digest(source.read_bytes()),mt7668_wifi_sha256=digest(wifi),mt7668_wifi_bytes=len(wifi),console_boot_tested=False)
    (ROOT/'runtime-inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
