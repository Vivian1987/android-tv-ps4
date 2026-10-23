"""Temporary direct-LAN recovery endpoint, restricted to the PS4 and Ember."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import hashlib

library = Path('/lib/x86_64-linux-gnu/libc.so.6').read_bytes()
digest = hashlib.sha256(library).hexdigest()
script = f'''#!/bin/sh
set -e
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
wget -q -O /tmp/libc.cole-new http://192.168.0.250:18778/libc
echo '{digest}  /tmp/libc.cole-new' | sha256sum -c -
chmod 755 /tmp/libc.cole-new
mv /tmp/libc.cole-new /lib/x86_64-linux-gnu/libc.so.6
/usr/sbin/dropbear -s -j -k -p 192.168.0.77:22 -r /etc/dropbear/host_ed25519
echo 'Cole: SSH restored.'
'''.encode()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.client_address[0] not in ['192.168.0.77', '192.168.0.250']:
            self.send_error(403)
            return
        if self.path == '/':
            data, content_type = script, 'text/plain'
        elif self.path == '/libc':
            data, content_type = library, 'application/octet-stream'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def log_message(self, *args):
        pass

print('PS4-only recovery endpoint ready on 192.168.0.250:18778', flush=True)
HTTPServer(('192.168.0.250', 18778), Handler).serve_forever()
