# Baikal kernel

Baikal consoles (later Slims and Pros) boot `bzImage-baikal`; every other console keeps the tested kernel. Build it from the same base as the main kernel (see [BUILD](../../../../docs/BUILD.md)) with `kernel/config` and:

1. `0001-baikal-southbridge-support.patch`: crashniels' 6.15 Baikal support (commits 74acef7, 8cbe437, 97a8f03, b3b6b1e from [crashniels/linux](https://github.com/crashniels/linux/tree/ps4-linux-6.15.y-baikal)), adapted to this base, plus the Baikal SATA PHY start-up from [linux-psx](https://github.com/meerzulee/linux-psx) (rmuxnet) for the drive.

`psx_mts_net.c` and `mts_net_core.h` are linux-psx's Baikal Ethernet driver (GPL-2.0), built as a module against this kernel. For 6.15 the `device_match_driver_override()` check reads `pci_dev->driver_override` instead.

None of this has been tested on a Baikal console yet.
