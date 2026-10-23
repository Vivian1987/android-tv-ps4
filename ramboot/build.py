"""Build a RAM-only PS4 diagnostic image from installed Ubuntu packages."""
from pathlib import Path
import gzip, hashlib, json, os, re, shutil, stat, subprocess, tarfile

source = Path(__file__).resolve().parent
build = Path('/home/amber/projects/ps4-android/ramboot')
root = build / 'root'
private = Path('/home/amber/.local/share/cole-ps4-android')
build.mkdir(parents=True, exist_ok=True)
if root.exists():
    shutil.rmtree(root)
for name in ['bin', 'sbin', 'usr/bin', 'usr/sbin', 'dev', 'proc', 'sys',
             'run', 'tmp', 'etc/dropbear', 'root/.ssh', 'lib64',
             'lib/x86_64-linux-gnu']:
    (root / name).mkdir(parents=True, exist_ok=True)

def copy(src, dest):
    path = root / dest.lstrip('/')
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, path)
    path.chmod(0o755)

copy('/usr/bin/busybox', '/bin/busybox')
(root / 'bin/sh').symlink_to('busybox')
copy('/usr/sbin/dropbear', '/usr/sbin/dropbear')
copy('/usr/sbin/kexec', '/usr/sbin/kexec')
copy('/usr/sbin/ip', '/usr/sbin/ip')
copy('/usr/sbin/iw', '/usr/sbin/iw')
for binary in ['/usr/sbin/dropbear', '/usr/sbin/kexec', '/usr/sbin/ip', '/usr/sbin/iw']:
    ldd = subprocess.check_output(['ldd', binary], text=True)
    for lib in re.findall(r'(/[^\s()]+)', ldd):
        copy(lib, lib)
firmware = build.parent/'console-firmware.tar'
if firmware.exists():
    with tarfile.open(firmware) as archive:
        for member in archive:
            name = Path(member.name)
            assert not name.is_absolute() and '..' not in name.parts
            assert name.parts[:2] == ('lib', 'firmware')
            dest = root/name
            if member.isdir():
                dest.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(archive.extractfile(member).read())
                dest.chmod(0o644)
            else:
                raise RuntimeError('Unexpected console firmware entry: '+member.name)
wireless = build.parent/'wireless-firmware'
if wireless.exists():
    for file in wireless.rglob('*'):
        if file.is_file():
            copy(file, str(file.relative_to(wireless)))
            (root/file.relative_to(wireless)).chmod(0o644)
quota_module = build.parent/'quota2/xt_quota2.ko'
if quota_module.exists():
    copy(quota_module, '/lib/modules/6.15.4-cole-android-aeolia-v1/extra/xt_quota2.ko')
copy(source / 'init', '/init')
copy(private / 'host_ed25519', '/etc/dropbear/host_ed25519')
copy(private / 'id_ed25519.pub', '/root/.ssh/authorized_keys')
for name in ['root', 'root/.ssh']:
    (root / name).chmod(0o700)
for name in ['etc/dropbear/host_ed25519', 'root/.ssh/authorized_keys']:
    (root / name).chmod(0o600)
(root / 'etc/passwd').write_text('root:x:0:0:root:/root:/bin/sh\n')
(root / 'etc/shadow').write_text('root:!:0:0:99999:7:::\n')
(root / 'etc/shadow').chmod(0o600)
(root / 'etc/group').write_text('root:x:0:\n')
(root / 'etc/profile').write_text('export PATH=/bin:/sbin:/usr/bin:/usr/sbin\n')
(root / 'etc/resolv.conf').write_text('nameserver 192.168.0.250\n')
(root / 'etc/nsswitch.conf').write_text('passwd: files\ngroup: files\nhosts: files dns\n')
subprocess.run(['/bin/busybox', 'sh', '-n', str(root / 'init')], check=True)

# Write newc directly: every archive owner is root, regardless of build user.
archive = bytearray()
def entry(name, mode, data=b'', ino=1):
    namebytes = name.encode() + b'\0'
    values = [ino, mode, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(namebytes), 0]
    archive.extend(b'070701' + ''.join(f'{v:08x}' for v in values).encode())
    archive.extend(namebytes)
    archive.extend(b'\0' * (-len(archive) % 4))
    archive.extend(data)
    archive.extend(b'\0' * (-len(archive) % 4))

for ino, path in enumerate(sorted(root.rglob('*')), 1):
    mode = path.lstat().st_mode
    data = os.readlink(path).encode() if stat.S_ISLNK(mode) else (path.read_bytes() if path.is_file() else b'')
    entry(str(path.relative_to(root)), mode, data, ino)
entry('TRAILER!!!', 0)
out = build / 'initramfs.cpio.gz'
out.write_bytes(gzip.compress(bytes(archive), compresslevel=6, mtime=0))
manifest = {'image': str(out), 'bytes': out.stat().st_size,
            'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
            'purpose': 'RAM-only hardware/network diagnostic; no disk mounts or installer',
            'management_ip': '192.168.0.77', 'ssh': 'project key only',
            'components': subprocess.check_output(['dpkg-query', '-W', 'busybox-static', 'dropbear-bin', 'libc6'], text=True).splitlines()}
(source.parent / 'evidence/ramboot-build.json').write_text(json.dumps(manifest, indent=2) + '\n')
out.chmod(0o600) # Contains a dedicated host key, never publish this artifact.
print(json.dumps(manifest, indent=2))
