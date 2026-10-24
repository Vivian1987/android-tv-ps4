#!/usr/bin/env python3
"""Patch the accepted runtime; preserve the kernel, graphics and boot protocol."""
from pathlib import Path
import argparse
import hashlib
import json
import lzma
import os
import re
import runpy
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
BASE_SHA = 'b191d815dbbb322b4cedba7ffee89f10a25a8d3e66d2601fb4151bd9d3d52ecb'
ASSETS = 'opt/androidtv-ps4/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unpack(raw):
    entries, pos = {}, 0
    while pos + 110 <= len(raw):
        header = raw[pos:pos+110]
        assert header[:6] == b'070701'
        fields = [int(header[6+i*8:14+i*8], 16) for i in range(13)]
        name = raw[pos+110:pos+110+fields[11]-1].decode()
        pos = (pos+110+fields[11]+3) & ~3
        data = raw[pos:pos+fields[6]]
        assert len(data) == fields[6]
        pos = (pos+fields[6]+3) & ~3
        if name == 'TRAILER!!!':
            return entries
        assert name not in entries
        entries[name] = (fields, data)
    raise ValueError('Missing cpio trailer')


def pack(entries):
    out = bytearray()
    for name, (fields, data) in list(entries.items()) + [('TRAILER!!!', ([0]*13, b''))]:
        fields = fields.copy()
        fields[6], fields[11] = len(data), len(name.encode())+1
        out.extend(b'070701' + ''.join(f'{v:08x}' for v in fields).encode() + name.encode() + b'\0')
        out.extend(b'\0'*(-len(out) % 4))
        out.extend(data)
        out.extend(b'\0'*(-len(out) % 4))
    return bytes(out)


def prepare(base, output, apps_dir):
    original = (base/'initramfs.cpio.xz').read_bytes()
    assert sha(original) == BASE_SHA, 'Unaccepted base runtime'
    app_manifest = json.loads((ROOT/'bundled-apps.json').read_text())
    bundle = json.loads((ROOT/'bundled-apps-image.json').read_text())
    assert bundle['manifest_sha256'] == sha((ROOT/'bundled-apps.json').read_bytes())
    assert bundle['file'] == 'bundled-apps.sfs'
    image = apps_dir/bundle['file']
    assert image.stat().st_size == bundle['bytes'] and sha(image.read_bytes()) == bundle['sha256']
    app_files = [{'asset':bundle['file'],'bytes':bundle['bytes'],'sha256':bundle['sha256']}]
    mounts = [app['directory'] for app in app_manifest['apps']]
    assert all(re.fullmatch(r'[a-z0-9_-]+',n) for n in mounts)
    total = bundle['bytes']
    header_rows = [' {"bundled-apps.sfs","bundled apps",'+str(total)+'ULL}']
    header = f'#define BUNDLED_APP_COUNT {len(app_files)}\n#define BUNDLED_APP_BYTES {total}ULL\n'
    header += 'struct bundled_app_asset { const char *file; const char *label; uint64_t bytes; };\n'
    header += 'static const struct bundled_app_asset bundled_apps[BUNDLED_APP_COUNT]={\n' + ',\n'.join(header_rows) + '\n};\n'
    (ROOT/'bundled-apps.h').write_text(header)
    entries = unpack(lzma.decompress(original))
    before = {name: sha(data) for name, (_, data) in entries.items()}
    next_inode = max(fields[0] for fields, _ in entries.values())+1

    def put(name, data, mode=0o100644):
        nonlocal next_inode
        fields = entries[name][0].copy() if name in entries else [next_inode, mode, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        next_inode += 1
        fields[6] = len(data)
        entries[name] = (fields, data)

    for name in ['mediaextractor.policy', 'androidtv-logging.rc', 'device-name.sh', 'device-name.rc']:
        put(ASSETS+name, (ROOT/'runtime-source'/name).read_bytes())
    # Rebuild console power cleanup together with any new host-side mounts.
    with tempfile.TemporaryDirectory() as work:
        supervisor = Path(work)/'android-supervisor'
        subprocess.run(['cc','-static','-O2','-Wall','-Wextra','-Werror',
                        str(ROOT/'power/android-supervisor.c'),'-o',str(supervisor)],check=True)
        put('usr/sbin/android-supervisor',supervisor.read_bytes(),0o100755)
    put(ASSETS+'bundled-apps.txt', ('\n'.join(mounts)+'\n').encode())
    child = entries[ASSETS+'android-child.sh'][1].decode()
    needle = 'exec chroot /android /system/bin/init selinux_setup'
    assert child.count(needle) == 1
    child = child.replace(needle, '# Apps select their own home directory; do not inherit the Linux shell root.\nunset HOME\n'+needle)
    subprocess.run(['/bin/busybox','sh','-n'],input=child.encode(),check=True)
    put(ASSETS+'android-child.sh',child.encode(),0o100755)
    for name in ['system-build.prop', 'vendor-build.prop', 'product-build.prop']:
        text = entries[ASSETS+name][1].decode()
        # Model is an app compatibility input, not merely an About-screen label.
        # Restore only the original base model. Keep genuine CPU ABI ordering,
        # existing fingerprint, the PS4 device name and the PS4 kernel identity.
        text = re.sub(r'^(ro\.product(?:\.[a-z_]+)?\.model)=PlayStation 4$',
                      r'\1=Pixel 10 Pro XL', text, flags=re.M)
        text = text.replace('ro.build.display.id=Android TV for PS4 13 - v0.15',
                            'ro.build.display.id=Android TV for PS4 13 - 1.0')
        put(ASSETS+name, text.encode())

    start = entries['usr/sbin/androidtv-ps4-start'][1].decode()
    assert entries[ASSETS+'autoboot.sh'][1] == start.encode()
    mesa_patch = runpy.run_path(str(ROOT/'runtime-source/patch-mesa-raster.py'))
    assert start.count(mesa_patch['BASE_SHA']) == 1
    start = start.replace(mesa_patch['BASE_SHA'],mesa_patch['PATCHED_SHA'])
    mesa32_marker = "echo 'ca0b4228ede6a6763568e6cafd4efc472f7d31eaae7622b03ad8d3dd3c7e545f  /android/system/vendor/lib64/dri/libgallium_dri.so' | sha256sum -c -"
    assert start.count(mesa32_marker) == 1
    start = start.replace(mesa32_marker, mesa32_marker + '\n# The native x86 YouTube/Kodi processes load the 32-bit Mesa driver.\n# Apply the same Liverpool raster correction to the exact pinned base library.\n# OverlayFS copies up this file; the distributed Android system stays untouched.\nmesa32=/android/system/vendor/lib/dri/libgallium_dri.so\nmesa32_sha=$(sha256sum "$mesa32" | cut -d \' \' -f 1)\ncase "$mesa32_sha" in\n eb4db495721ec36dfa4d0cdb6378c845bd756c77748fae9aed14eacaf2389f1e)\n  printf \'\\032\\026\\000\\052\' | dd of="$mesa32" bs=1 seek=23111413 conv=notrunc 2>/dev/null\n  ;;\n fbac4a587e486de0e4f6f6b02dbe3c9495371735ca3c35e5e3cfbcc753d85c2c) ;;\n *) stage \'Unsupported 32-bit graphics library\'; exit 1 ;;\nesac\necho \'fbac4a587e486de0e4f6f6b02dbe3c9495371735ca3c35e5e3cfbcc753d85c2c  /android/system/vendor/lib/dri/libgallium_dri.so\' | sha256sum -c -')
    needle = 'cp "$assets/androidtv-ps4.rc" /android/system/etc/init/androidtv-ps4.rc'
    assert start.count(needle) == 1
    start = start.replace(needle, needle + '''
cp "$assets/androidtv-logging.rc" /android/system/etc/init/androidtv-logging.rc
cp "$assets/device-name.rc" /android/system/etc/init/androidtv-device-name.rc
cp "$assets/device-name.sh" /android/system/bin/androidtv-device-name.sh
chmod 644 /android/system/etc/init/androidtv-device-name.rc /android/system/bin/androidtv-device-name.sh
mkdir -p /android/system/vendor/etc/seccomp_policy
cp "$assets/mediaextractor.policy" /android/system/vendor/etc/seccomp_policy/mediaextractor.policy
chmod 644 /android/system/etc/init/androidtv-logging.rc /android/system/vendor/etc/seccomp_policy/mediaextractor.policy
# Keep native APKs on internal storage, outside the small initramfs.
# Signed APKs, splits and native libraries have their normal Android layout.
# The read-only app filesystem stays on disk, outside the RAM overlay.
mkdir -p /mnt/android-bundled-apps
mount -t squashfs -o ro,loop "$installation/bundled-apps.sfs" /mnt/android-bundled-apps
while read -r app; do
 target="/android/system/app/atv-$app"
 # Replace the base ARM service in its existing privileged product location.
 # Hiding that entire directory prevents duplicate packages and stale libraries.
 [ "$app" != gms ] || target=/android/system/product/priv-app/GooglePlayServices
 mkdir -p "$target"
 mount --bind "/mnt/android-bundled-apps/$app" "$target"
done < "$assets/bundled-apps.txt"''')
    collector = '''nsenter -t "$child" -m -p -n chroot /android /system/bin/logcat -b all -v threadtime 2>/dev/null | head -c 8388608 > "$installation/android-boot.log" &
logger=$!'''
    assert start.count(collector) == 1
    start = start.replace(collector, '# Android init owns the rotating collector in /data/misc/logd; it survives setup.')
    start = start.replace('kill "$logger" 2>/dev/null || true; ', '')
    start = start.replace('  kill "$logger" 2>/dev/null || true\n', '')
    start = start.replace('kill "$logger" 2>/dev/null || true\n', '')
    start = start.replace('check android-boot.log and android-stages.log',
                          'check Android /data/misc/logd and android-stages.log')
    assert '$logger' not in start
    subprocess.run(['/bin/busybox', 'sh', '-n'], input=start.encode(), check=True)
    for name in ['usr/sbin/androidtv-ps4-start', ASSETS+'autoboot.sh']:
        put(name, start.encode(), 0o100755)

    changed = sorted(name for name, (_, data) in entries.items() if before.get(name) != sha(data))
    allowed = sorted([ASSETS+n for n in ['mediaextractor.policy', 'androidtv-logging.rc', 'device-name.sh', 'device-name.rc', 'bundled-apps.txt', 'android-child.sh',
                     'system-build.prop', 'vendor-build.prop', 'product-build.prop', 'autoboot.sh']]
                     + ['usr/sbin/androidtv-ps4-start', 'usr/sbin/android-supervisor'])
    # vendor-build.prop has no top-level model override in some base revisions.
    assert set(changed) <= set(allowed), changed
    assert not (set(before)-set(entries))
    raw = pack(entries)
    assert {n: d for n, (_, d) in unpack(raw).items()} == {n: d for n, (_, d) in entries.items()}
    compressed = lzma.compress(raw, format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC32,
                              filters=[{'id': lzma.FILTER_X86},
                                       {'id': lzma.FILTER_LZMA2, 'dict_size': 8*1024*1024, 'preset': 6}])
    assert len(compressed) < 10*1024*1024, 'Keep accepted boot memory budget'
    output.mkdir(parents=True, exist_ok=True)
    for f in base.iterdir():
        if f.name in ['initramfs.cpio.xz','libgallium-baseline.so']:
            continue
        target = output/f.name
        if target.exists():
            assert sha(target.read_bytes()) == sha(f.read_bytes())
        else:
            os.link(f, target)
    (output/'initramfs.cpio.xz').write_bytes(compressed)
    mesa = output/'libgallium-baseline.so'
    # Never overwrite a hard link into the accepted baseline.
    if mesa.exists():mesa.unlink()
    mesa.write_bytes(mesa_patch['patch']((base/'libgallium-baseline.so').read_bytes()))
    for f in app_files:
        target = output/f['asset']
        if not target.exists():
            os.link(apps_dir/f['asset'], target)
        assert sha(target.read_bytes()) == f['sha256']
    expected = {f.name for f in base.iterdir()} | {f['asset'] for f in app_files}
    assert {f.name for f in output.iterdir()} == expected, 'Unexpected runtime assets'
    manifest = {'base_release': 'retained-start', 'base_initramfs_sha256': BASE_SHA,
                'initramfs_sha256': sha(compressed), 'initramfs_bytes': len(compressed),
                'expanded_sha256': sha(raw), 'expanded_bytes': len(raw),
                'changed_entries': changed, 'kernel_composer_gralloc_bluetooth_unchanged': True,
                'mesa_sha256': mesa_patch['PATCHED_SHA'],
                'bundled_apps_sha256': sha((ROOT/'bundled-apps.json').read_bytes()),
                'bundled_app_bytes': total,
                'bundled_app_count': len(app_manifest['apps']),
                'app_storage': 'Bundled read-only app filesystem, signed APKs and prepared native libraries',
                'userdata_included': False, 'console_boot_tested': False}
    (ROOT/'runtime-inputs.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ['base', 'output', 'apps-dir']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    prepare(args.base, args.output, args.apps_dir)
