#!/usr/bin/env python3
"""Prepare signed APKs and their native libraries as a read-only app filesystem.

Android does not extract native libraries for immutable system applications.
Prepare the normal /system/app/<name>/lib/<isa> layout before packaging.
No app data, accounts, save files or device state are input to this process.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,zipfile

ROOT=Path(__file__).resolve().parent
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def prepare(inputs,build,output):
    manifest=json.loads((ROOT/'bundled-apps.json').read_text())
    tree=build/'apps';tree.mkdir(parents=True,exist_ok=True)
    expected={};layouts=[]
    for app in manifest['apps']:
        name=app['directory'];assert re.fullmatch('[a-z0-9_-]+',name)
        abi=next((a for a in ['x86_64','x86','arm64-v8a','armeabi-v7a'] if a in app['abis']),None)
        isa={'x86_64':'x86_64','x86':'x86','arm64-v8a':'arm64','armeabi-v7a':'arm'}.get(abi)
        assert not app['requires_translation'] or name=='crossyroad'
        native=[]
        for f in app['files']:
            source=inputs/f['asset'];assert source.stat().st_size==f['bytes'] and digest(source)==f['sha256']
            assert re.fullmatch('[A-Za-z0-9_.-]+\\.apk',f['filename'])
            dest=tree/name/f['filename'];dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists():os.link(source,dest)
            assert digest(dest)==f['sha256'];expected[dest.relative_to(tree).as_posix()]=f['sha256']
            with zipfile.ZipFile(source) as z:
                for info in z.infolist():
                    if not abi or not info.filename.startswith('lib/'+abi+'/') or not info.filename.endswith('.so'):continue
                    lib=Path(info.filename).name
                    assert re.fullmatch('[A-Za-z0-9_.+-]+\\.so',lib),lib
                    data=z.read(info);assert data[:4]==b'\x7fELF'
                    target=tree/name/'lib'/isa/lib;target.parent.mkdir(parents=True,exist_ok=True)
                    sha=hashlib.sha256(data).hexdigest()
                    if target.exists():assert digest(target)==sha
                    else:target.write_bytes(data);target.chmod(0o644)
                    expected[target.relative_to(tree).as_posix()]=sha;native.append(lib)
        assert not abi or native,app['id']
        layouts.append({'directory':name,'package':app['package'],'abi':abi,'native_libraries':sorted(set(native))})
    actual={p.relative_to(tree).as_posix():digest(p) for p in tree.rglob('*') if p.is_file()}
    assert actual==expected,'Unexpected or stale app filesystem files'
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['mksquashfs',str(tree),str(output),'-noappend','-all-root','-comp','zstd','-Xcompression-level','8','-b','1048576','-processors','4','-no-progress','-mkfs-time','0','-all-time','0','-root-mode','0755'],check=True)
    report={'file':'bundled-apps.sfs','bytes':output.stat().st_size,'sha256':digest(output),
            'manifest_sha256':digest(ROOT/'bundled-apps.json'),'account_data_included':False,
            'layout':layouts,'files':expected,'console_boot_tested':False}
    (ROOT/'bundled-apps-image.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['files','layout']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['inputs','build','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();prepare(a.inputs,a.build,a.output)
