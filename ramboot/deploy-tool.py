"""Copy a host tool and dependencies to RAM Linux without clobbering live files."""
from pathlib import Path
import hashlib, re, subprocess, sys, uuid

private = Path('/home/amber/.local/share/cole-ps4-android')
ssh = ['ssh', '-T', '-i', str(private/'id_ed25519'), '-o', 'StrictHostKeyChecking=yes',
       '-o', 'UserKnownHostsFile='+str(private/'known_hosts'), '-o', 'BatchMode=yes',
       '-o', 'ConnectTimeout=5', 'root@192.168.0.77']

def deploy(path):
    assert re.fullmatch(r'/[A-Za-z0-9_./+-]+', path) and '..' not in Path(path).parts
    assert path.startswith(('/usr/sbin/', '/usr/bin/', '/lib/', '/lib64/'))
    data = Path(path).read_bytes()
    mode = f'{Path(path).stat().st_mode & 0o777:o}'
    expected = hashlib.sha256(data).hexdigest()
    existing = subprocess.run(ssh+['sha256sum '+path], capture_output=True, text=True, timeout=8)
    if existing.returncode == 0 and existing.stdout.split()[0] == expected:
        subprocess.run(ssh+['chmod '+mode+' '+path], check=True, timeout=8)
        print('Already matches:', path, flush=True)
        return
    temporary = path+'.cole-stage-'+uuid.uuid4().hex
    subprocess.run(ssh+['mkdir -p '+str(Path(path).parent)], check=True, timeout=8)
    subprocess.run(ssh+['cat > '+temporary], input=data, check=True, timeout=15)
    actual = subprocess.check_output(ssh+['sha256sum '+temporary], text=True, timeout=8).split()[0]
    assert actual == expected, 'Upload checksum mismatch: '+path
    subprocess.run(ssh+['chmod '+mode+' '+temporary+'\nmv '+temporary+' '+path], check=True, timeout=8)
    print('Atomically deployed:', path, flush=True)

if __name__ == '__main__':
    binary = sys.argv[1]
    deps = subprocess.check_output(['ldd', binary], text=True)
    for dependency in dict.fromkeys(re.findall(r'(/[^\s()]+)', deps)):
        deploy(dependency)
    deploy(binary)
