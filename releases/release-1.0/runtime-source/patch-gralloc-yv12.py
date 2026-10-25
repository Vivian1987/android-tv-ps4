#!/usr/bin/env python3
"""Pad YV12 rows to 512 bytes in the pinned gralloc.gbm binary.

gralloc.gbm allocates a YV12 buffer as a GR88 surface w/2 pixels wide and
reports the chroma stride as half the luma stride. Mesa's allocator pads that
surface to 256 bytes, so the chroma planes can end up only 128-byte aligned
(1280x720: luma 1280, chroma 640). radeonsi rejects a dma-buf plane whose
pitch isn't 256-byte aligned, so SurfaceFlinger can't import those video
frames, and the picture freezes while audio continues. Widths that happened
to pad to 512 (960x540, 1920x1080) worked.

The patch rounds the GR88 width up to a multiple of 256 pixels, so luma rows
are a multiple of 512 bytes and chroma rows a multiple of 256. The chroma
stride stays half the luma stride, as Android's YV12 layout requires.

  before: mov r12d,eax; shr 31,eax; add r12d,eax; sar 1,eax   (eax = w/2)
          ...;                       mov eax,r12d
  after:  add 0x1ff,r12d; shr 1,r12d; xor r12b,r12b           (r12d = (w+511)/2 & ~255)
          ...;                       nop
"""
import hashlib

BASE_SHA = '6803c4d592e97e6252d0dffd25a6a332db1d5f632cc958f0ec7dd6d89cff9052'
PATCHED_SHA = '2d10e6f61a3d58cd8ccc64e03a94a6a48da82ce15c453cf7844979a0ec35b375'
OFFSET = 0x3726  # gralloc_gbm_bo_create, YV12 branch (vaddr 0x4726)
ORIGINAL = bytes.fromhex('4489e0c1e81f4401e0d1f8' '4489ead1ea4101d5' '4189c4')
CORRECTED = bytes.fromhex('4181c4ff010000' '41d1ec' '4530e4' '4489ead1ea4101d5' '90')

def patch(data):
    assert hashlib.sha256(data).hexdigest() == BASE_SHA, 'Unexpected gralloc binary'
    assert data[OFFSET:OFFSET+len(ORIGINAL)] == ORIGINAL
    result = data[:OFFSET] + CORRECTED + data[OFFSET+len(ORIGINAL):]
    assert hashlib.sha256(result).hexdigest() == PATCHED_SHA
    return result

if __name__ == '__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();a.output.write_bytes(patch(a.input.read_bytes()))
