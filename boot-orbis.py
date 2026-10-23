"""Stage verified Android-capable RAM Linux over GoldHEN FTP, then boot it."""
from pathlib import Path
import argparse, ftplib, hashlib, io, json, socket, subprocess, time, uuid

project = Path(__file__).resolve().parent
private = Path('/home/amber/.local/share/cole-ps4-android')
backups = private/'orbis-backups'
backups.mkdir(exist_ok=True, mode=0o700)
parser = argparse.ArgumentParser()
parser.add_argument('--known-good', action='store_true', help='Alias for the current graphics-verified standard; never restores obsolete images')
parser.add_argument('--proven-ram', action='store_true', help='Alias for the current graphics-verified standard')
options = parser.parse_args()
standard = json.loads((project/'evidence/standard-boot.json').read_text())
assert standard['validated_archive_contents'] and standard['version'] == 'standard-v1'
files = []
for name in ['bzImage', 'initramfs.cpio.gz', 'bootargs.txt', 'vram.txt']:
    spec = standard['files'][name]
    data = Path(spec['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == spec['sha256'], 'Standard boot checksum mismatch: '+name
    files.append((name, data))
build = {'sha256': standard['files']['bzImage']['sha256']}
ram_hash = standard['files']['initramfs.cpio.gz']['sha256']
expected_uname = '6.15.4-cole-android-aeolia-v1'
f = ftplib.FTP()
f.connect('192.168.0.77', 2121, timeout=8)
f.login()
f.voidcmd('TYPE I')
for name in ['bzImage', 'initramfs.cpio.gz', 'bootargs.txt', 'vram.txt']:
    for usb in ['usb0', 'usb1']:
        try:
            size = f.size('/mnt/'+usb+'/'+name)
        except ftplib.error_perm:
            continue
        assert size is None, 'USB boot override exists; inspect before booting.'
manifest = []
for name, data in files:
    target = '/data/linux/boot/'+name
    expected = hashlib.sha256(data).hexdigest()
    old = bytearray()
    try:
        f.retrbinary('RETR '+target, old.extend, blocksize=262144)
    except ftplib.error_perm:
        pass
    previous = hashlib.sha256(old).hexdigest() if old else None
    if previous == expected:
        print('Already verified:', target, flush=True)
        manifest.append({'path': target, 'sha256': expected, 'unchanged': True})
        continue
    stage = target+'.cole-next'
    f.storbinary('STOR '+stage, io.BytesIO(data), blocksize=262144)
    remote_hash = hashlib.sha256()
    f.retrbinary('RETR '+stage, remote_hash.update, blocksize=262144)
    assert remote_hash.hexdigest() == expected, 'FTP checksum mismatch: '+name
    backup = None
    if old:
        local = backups/(name+'.'+previous)
        local.write_bytes(old)
        local.chmod(0o600)
        backup = target+'.backup-'+previous[:12]+'-'+uuid.uuid4().hex[:6]
        f.rename(target, backup)
    f.rename(stage, target)
    manifest.append({'path': target, 'bytes': len(data), 'sha256': expected,
                     'previous_sha256': previous, 'remote_backup': backup})
    print('Staged and verified:', target, len(data), 'bytes', flush=True)
f.quit()
(project/'evidence/android-orbis-staged.json').write_text(json.dumps(manifest, indent=2)+'\n')
loader = (project/'downloads/linux-1024mb.elf').read_bytes()
assert hashlib.sha256(loader).hexdigest() == '623c3b68592437b612ede22a4fc1a6f1eef6b17c4b16a1270100ece04cb3c98f'
with socket.create_connection(('192.168.0.77', 9090), timeout=5) as sock:
    sock.sendall(loader)
    sock.shutdown(socket.SHUT_WR)
print('GoldHEN Linux loader sent.', flush=True)
ssh = ['ssh', '-T', '-i', str(private/'id_ed25519'), '-o', 'StrictHostKeyChecking=yes',
       '-o', 'UserKnownHostsFile='+str(private/'known_hosts'), '-o', 'BatchMode=yes',
       '-o', 'ConnectTimeout=2', 'root@192.168.0.77', 'uname -r']
deadline = time.monotonic()+100
while time.monotonic() < deadline:
    try:
        result = subprocess.run(ssh, capture_output=True, text=True, timeout=4)
        if result.returncode == 0 and result.stdout.strip() == expected_uname:
            print('New kernel running:', result.stdout.strip(), flush=True)
            (project/'evidence/android-kernel-running.json').write_text(json.dumps({
                'uname': result.stdout.strip(), 'kernel_sha256': build['sha256'],
                'boot_path': 'GoldHEN ELF loader', 'ssh_host_key_verified': True}, indent=2)+'\n')
            break
    except subprocess.TimeoutExpired:
        pass
    time.sleep(2)
else:
    raise SystemExit('No new-kernel SSH within 100 seconds; inspect TV before retrying.')
