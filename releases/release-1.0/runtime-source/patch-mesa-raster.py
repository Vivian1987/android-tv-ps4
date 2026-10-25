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

# PS4 Pro (Gladius) has twice the shader engines and also needs
# PA_SC_RASTER_CONFIG_1=0x4e (kernel gfx_v7_0_raster_config, CHIP_GLADIUS).
# Mesa identifies both PS4 GPUs as Kaveri, whose case leaves raster_config_1
# at 0. The Gladius build points the Kaveri jump-table entry at the Hawaii
# block (never used on a PS4) and gives that block both Gladius values. The
# boot script applies these bytes only when the GPU is 1002:9924.
GLADIUS = {
    'x86_64': (PATCHED_SHA, '7130ea84514d6113426ffb33c48b1e8dab68f75de33b4e1e25798ffcf53e836a',
               [(5873684, '61bb1501'), (24071009, '2a'), (24071012, '4e')]),
    'x86': (X86_PATCHED_SHA, '2fa26f9bc50f33ae07dfc13b0488770d5fe20a19b9a821ac956d2c0905d7c42a',
            [(5383584, '8b2372ff'), (23111439, '2a'), (23111441, '4e')]),
}

def patch_gladius(data, abi='x86_64'):
    original, corrected, edits = GLADIUS[abi]
    assert hashlib.sha256(data).hexdigest() == original, 'Expected the Liverpool-corrected Mesa binary'
    result = bytearray(data)
    for offset, value in edits:
        value = bytes.fromhex(value)
        result[offset:offset+len(value)] = value
    assert hashlib.sha256(result).hexdigest() == corrected
    return bytes(result)

if __name__ == '__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--abi', choices=['x86', 'x86_64'], default='x86_64')
    p.add_argument('--gladius', action='store_true', help='apply the PS4 Pro edits to a corrected binary')
    a=p.parse_args();data=a.input.read_bytes()
    a.output.write_bytes(patch_gladius(data, a.abi) if a.gladius else patch(data, a.abi))
