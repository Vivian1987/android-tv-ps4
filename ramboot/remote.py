"""Send stdin to the running PS4's shell using the pinned project host key."""
from pathlib import Path
import subprocess, sys
p = Path('/home/amber/.local/share/cole-ps4-android')
result = subprocess.run(['ssh', '-T', '-i', str(p/'id_ed25519'),
    '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile='+str(p/'known_hosts'),
    '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5', 'root@192.168.0.77',
    '/bin/sh', '-s'], input=sys.stdin.buffer.read())
raise SystemExit(result.returncode)
