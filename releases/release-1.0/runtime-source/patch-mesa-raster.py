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

def patch(data):
    assert hashlib.sha256(data).hexdigest() == BASE_SHA, 'Unexpected Mesa binary'
    assert data[0x16f4b37:0x16f4b3c] == bytes.fromhex('ba02000000')
    result = data[:0x16f4b38] + bytes.fromhex('1a16002a') + data[0x16f4b3c:]
    assert hashlib.sha256(result).hexdigest() == PATCHED_SHA
    return result

if __name__ == '__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();a.output.write_bytes(patch(a.input.read_bytes()))
