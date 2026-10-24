#!/usr/bin/env python3
"""Embed the pinned upstream PIC Linux payload, not an arbitrary ELF loader.
Upstream distributes this payload as both ELF and flat BIN (objcopy of
.text/.rodata/.data/.bss). Preserve section spacing and explicitly zero BSS.
"""
import hashlib, struct, sys, subprocess
from pathlib import Path
EXPECTED='623c3b68592437b612ede22a4fc1a6f1eef6b17c4b16a1270100ece04cb3c98f'
def flatten(blob):
    if hashlib.sha256(blob).hexdigest()!=EXPECTED:
        raise ValueError('Unreviewed Linux payload: source/hash/PIC layout must be reviewed first')
    e=struct.unpack_from('<16sHHIQQQIHHHHHH',blob)
    assert e[0][:7]==b'\x7fELF\x02\x01\x01' and e[1:4]==(2,62,1)
    entry=e[4]; sections=[]
    assert e[11]==64
    sh=[struct.unpack_from('<IIQQQQIIQQ',blob,e[6]+i*64) for i in range(e[12])]
    names=blob[sh[e[13]][4]:sh[e[13]][4]+sh[e[13]][5]]
    for h in sh:
        name=names[h[0]:].split(b'\0',1)[0]
        if name in (b'.text',b'.rodata',b'.data',b'.bss'):
            assert h[3]>=entry and h[3]+h[5]-entry < 1024*1024
            assert h[1]==8 or h[4]+h[5]<=len(blob)
            sections.append(h)
    assert len(sections)==4 and min(h[3] for h in sections)==entry
    image=bytearray(max(h[3]+h[5] for h in sections)-entry)
    for h in sections:
        if h[1]!=8:image[h[3]-entry:h[3]-entry+h[5]]=blob[h[4]:h[4]+h[5]]
    return bytes(image)
if __name__=='__main__':
    data=flatten(Path(sys.argv[1]).read_bytes())
    rows=[','.join('0x%02x'%b for b in data[i:i+16]) for i in range(0,len(data),16)]
    Path(sys.argv[2]).write_text('/* Generated from pinned PS4 Linux loader; includes zero BSS. */\nstatic const unsigned char local_payload_image[]={\n'+',\n'.join(rows)+'\n};\n')
    required=['get_firmware','normalize_fw_ver','find_offsets_by_fw','get_kexec_blob','get_sb_id','kernel_main','kexec','kexec_load','pack_kexec_args','g_fw','g_kexec_s','g_kexec_e','errno','evf_open','evf_cancel','evf_close','kill']
    symbols={}
    for line in subprocess.check_output(['nm',sys.argv[1]],text=True).splitlines():
        words=line.split()
        if len(words)==3 and words[2] in required:symbols[words[2]]=int(words[0],16)
    assert set(symbols)==set(required)
    with Path(sys.argv[2]).open('a') as out:
        for name,addr in sorted(symbols.items()):
            offset=addr-0x401000
            assert 0<=offset<len(data)
            out.write('#define PAYLOAD_'+name+' '+hex(offset)+'ULL\n')
    print('Embedded pinned local payload:' ,len(data),'bytes; SHA256',hashlib.sha256(data).hexdigest())
