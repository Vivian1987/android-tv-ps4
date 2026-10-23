# Storage accounting — v0.15, 32 GiB edition

These figures describe the recorded package with SHA-256
`d9524c23141adc7c7d6f49955d607d5ec325524fcf006b1dd693f73bfe9226b4`.
Its eight build assets were checked against the release manifest before adding
up their sizes. Actual installed PS4 allocation has not been measured here.

| Item | Bytes | GiB |
| --- | ---: | ---: |
| Android data image, fully allocated | 34,359,738,368 | 32.000 |
| Copied system, graphics library and boot files | 2,332,663,987 | 2.172 |
| Installed launcher/package estimate | 2,348,810,240 | 2.188 |
| Combined estimate at full data-image allocation | 39,041,212,595 | 36.360 |
| Combined estimate plus 2 GiB free margin | 41,188,696,243 | 38.360 |
| Also retaining a separate downloaded PKG | 43,537,506,483 | 40.547 |

GiB means 1,073,741,824 bytes. Decimal GB means 1,000,000,000 bytes.
Allowing about 42 GiB (45 GB) provides rounding room above the last estimate;
it is planning guidance, not an installer-enforced reservation or a measured
maximum including arbitrary old downloads/backups.

## Why the system is counted twice

`build-release.py` includes `system.sfs` and the other assets in the launcher
package. `source/install-prebuilt.c` copies the system and graphics library to
`/user/app/ps4-android`, and boot files to `/data/linux/boot`. It does not delete
the originals in the installed package. Subsequent launches still open the
package assets, including the Linux loader and boot files.

The installed package is distinct from a downloaded copy staged under
`/data/pkg` or elsewhere. That download occupies additional space if retained
on the internal drive. A download on external storage does not add that copy
to internal-drive usage.

The package file's size is used as an estimate of the installed launcher
footprint. PS4 allocation overhead is not measured by the package file size.
The copied-files total includes `system.sfs`, `libgallium-baseline.so`,
`bzImage`, `initramfs.cpio.gz`, `bootargs.txt`, `vram.txt` and `data-gib.txt`.
Markers, logs, filesystem overhead and retained boot backups add further space.

## What the free-space checks actually do

For a new installation, the native app checks for `SYSTEM_BYTES + 2 GiB` free:
4,406,571,008 bytes (4.104 GiB). This runs after the launcher PKG is installed.
An existing or partial system copy reduces the amount requested by that check.
The check does not explicitly add the remaining boot/graphics file sizes.

Linux first boot checks for more than 2 GiB free, then creates a sparse
`data.img` with `truncate` and formats that file as ext4. It does not preallocate
the full 32 GiB or continuously enforce a 2 GiB reserve during Android use.

Inside the image, `data/` supplies Android's `/data`, and `metadata/` supplies
`/metadata`. The compressed system stays read-only; its writable overlay is in
RAM. Apps, settings and downloaded files consume space inside the data image.

Interrupted system copies use `.part` and are renamed after completion, rather
than retaining a second complete copy on successful installation. Existing boot
files may be kept as `.before-sparse-v015` backups. Old packages, logs, failed
installations and backups must be counted separately when estimating a drive
that already has development history.
