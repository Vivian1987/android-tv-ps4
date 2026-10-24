#!/usr/bin/env python3
"""Use the Liverpool raster configuration in the pinned Android Mesa binary.

Source equivalent in ac_get_raster_config: the PS4 Liverpool case uses
PA_SC_RASTER_CONFIG=0x2a00161a, not the 0x00000002 Kaveri value.
Reference: Ps3itaTeam/ps4linux-video-drivers, mesa-git/mesa.patch.
This is a bounded binary adaptation, not a rebuilt Mesa source release.
"""
import hashlib

BASE_SHA = '529cc9bca88f16fc53c205770901fcd439be322eda9fda2083ac714b6ed95190'
PATCHED_SHA = 'ca0b4228ede6a6763568e6cafd4efc472f7d31eaae7622b03ad8d3dd3c7e545f'
X86_BASE_SHA = 'eb4db495721ec36dfa4d0cdb6378c845bd756c77748fae9aed14eacaf2389f1e'
X86_PATCHED_SHA = 'fbac4a587e486de0e4f6f6b02dbe3c9495371735ca3c35e5e3cfbcc753d85c2c'

def patch(data, abi='x86_64'):
    if abi == 'x86_64':
        original, corrected, offset, opcode = BASE_SHA, PATCHED_SHA, 0x16f4b38, 'ba'
    elif abi == 'x86':
        original, corrected, offset, opcode = X86_BASE_SHA, X86_PATCHED_SHA, 0x160a6f5, 'bf'
    else:
        raise ValueError('Unsupported ABI')
    assert hashlib.sha256(data).hexdigest() == original, 'Unexpected Mesa binary'
    assert data[offset-1:offset+4] == bytes.fromhex(opcode+'02000000')
    result = data[:offset] + bytes.fromhex('1a16002a') + data[offset+4:]
    assert hashlib.sha256(result).hexdigest() == corrected
    return result

if __name__ == '__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--abi', choices=['x86', 'x86_64'], default='x86_64')
    a=p.parse_args();a.output.write_bytes(patch(a.input.read_bytes(), a.abi))
