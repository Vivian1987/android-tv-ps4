# Baikal kernel

Baikal consoles (later Slims and Pros) boot `bzImage-baikal`; every other console keeps the tested kernel. Build it from the same base as the main kernel (see [BUILD](../../../../docs/BUILD.md)) with `kernel/config` plus the Baikal settings below, and apply, in order:

1. `0001-baikal-southbridge-support.patch`: crashniels' 6.15 Baikal support (commits 74acef7, 8cbe437, 97a8f03, b3b6b1e from [crashniels/linux](https://github.com/crashniels/linux/tree/ps4-linux-6.15.y-baikal)), adapted to this base, plus the Baikal SATA PHY start-up from [linux-psx](https://github.com/meerzulee/linux-psx) (rmuxnet) for the drive.
2. `0002-linux-ps4-v60-baikal-display.patch`: the fixes from meerzulee's [linux-ps4](https://github.com/meerzulee/linux-ps4) tag `v60-hdmi-working`, the first 6.15.4 build that put a picture on a Baikal Slim's screen. Each change is documented in that repository's `patches/6.x-baikal/series` and `checkpoint/docs/research/`.

`psx_mts_net.c` and `mts_net_core.h` are linux-psx's Baikal Ethernet driver (GPL-2.0), built as a module against this kernel. For 6.15 the `device_match_driver_override()` check reads `pci_dev->driver_override` instead.

## Why 1.1's first Baikal kernel showed no picture

The Baikal southbridge driver sets up its serial port, then the ICC channel the GPU uses to program the HDMI chip. On 6.x kernels the serial port is rejected, and 1.1's driver treated that as fatal, so the whole southbridge driver gave up. The GPU driver waits for the southbridge before it starts, so it waited forever and the HDMI output stayed off. meerzulee found this with a serial cable on a Baikal Slim; the log shows `Failed to register serial port 0`, then `probe with driver baikal_pcie failed with error -5`.

## What patch 0002 changes

| Area | Change | Upstream patch |
| --- | --- | --- |
| Southbridge | A serial port failure is a warning, not fatal | 0200/0004 |
| Interrupts | The southbridge becomes a 6.x MSI parent and programs its own MSI registers; shared-vector and per-function masking fixes | 0200/0005, 0007–0010 |
| ICC | If the ICC interrupt never arrives, poll its status register, so HDMI commands still complete | 0200/0011–0014 |
| ACPI | Give IRQ 9 a descriptor and install the ACPI interrupt with `request_irq`, so the GPU's ATOM BIOS tables work | 0100/0002, 0150/0001 |
| GPU | Require MSI; skip DisplayPort link training (the HDMI chip trains the link itself); start the HDMI bridge at attach in 1080p60 | 0300/0005–0010 |
| GPU | Keep the bridge running through mode changes, give the link time to settle, floor the DisplayPort clock to 4 lanes at 2.7 Gbps, use the real PLL | 0300/0014, 0015, 0022, 0023, 0026 |
| GPU | Leave the DisplayPort transmitter that the PS4 firmware already trained untouched: skip the transmitter disable and enable steps. This was the change that brought up the picture | 0300/0031, 0032 |
| USB | Baikal xHCI shutdown, settle time, interrupts through the southbridge, interrupt moderation and retry | 0800/0002, 0005–0007 |
| IOMMU | Southbridge devices use the identity domain, so the drive controller's DMA allocations work | 1000/0003 |

Several 0300 patches also add display diagnostics to the kernel log (ATOM table trace, bridge command timing, DisplayPort lane status). They're kept: on a console with no picture, the log is the only way to see how far the display got.

## Built-in boot arguments

The Baikal kernel has `CONFIG_CMDLINE="pci=nocrs intremap=off video=HDMI-A-1:1920x1080@60D"`, added in front of `bootargs.txt`, so other consoles never see them. Every Baikal setup reported working uses `intremap=off` and `pci=nocrs`: the loader turns the IOMMU off on Baikal, and interrupt remapping without it loses interrupts. The `D` forces the HDMI output on.

## Status

Built, not yet run on a Baikal console. The upstream results are on Baikal Slims; Baikal Pros haven't been confirmed working on any 6.x kernel. Starting with the build that includes this kernel, Linux also copies its log to a USB stick every few seconds (see `AndroidTV-PS4-blackbox` in [INSTALL](../../../../docs/INSTALL.md#logs-and-reporting-problems)), so a Baikal start with no picture still reports how far it got.
