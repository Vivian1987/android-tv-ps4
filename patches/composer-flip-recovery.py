from pathlib import Path
import hashlib,struct,json
p=Path('/home/amber/projects/ps4-android/autoboot-assets/composer');data=bytearray(p.read_bytes());old=hashlib.sha256(data).hexdigest()
assert old=='d4bd4f23938a8b96b6aa882ff5e4c1a013745321691b30f1c234b741ae310196'
# Pinned ELF: executable segment's file offset is virtual address - 0x1000.
start=0x16f00;cave=0x171c3;end=0x16fe5
assert data[start-0x1000:start-0x1000+9]==bytes.fromhex('c6435e00e9dc000000')
assert data[cave-0x1000:cave-0x1000+13]==b'\xcc'*13
# After a failed flip, clear both mModeSet (0x5d) and mFlipPending (0x5e).
# The next present then uses drmModeSetCrtc, which can change pixel format.
code=bytes.fromhex('66c7435d0000')+b'\xe9'+struct.pack('<i',end-(cave+11))
data[cave-0x1000:cave-0x1000+len(code)]=code
data[start-0x1000:start-0x1000+9]=b'\xe9'+struct.pack('<i',cave-(start+5))+b'\x90'*4
out=Path('/mnt/nas/apps/ps4-android/downloads/composer-format-recovery');out.write_bytes(data)
Path('/mnt/nas/apps/ps4-android/evidence/composer-format-recovery.json').write_text(json.dumps({'original_sha256':old,'sha256':hashlib.sha256(data).hexdigest(),'failure_branch_va':hex(start),'code_cave_va':hex(cave),'source_equivalent':'After drmModePageFlip failure: mFlipPending=false; mModeSet=false; next present retries using drmModeSetCrtc.','live_verified':False},indent=2)+'\n')
print(out)
