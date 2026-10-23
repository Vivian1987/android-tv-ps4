# Storage — v0.15, 32 GiB edition

These figures describe the recorded package with SHA-256
`d9524c23141adc7c7d6f49955d607d5ec325524fcf006b1dd693f73bfe9226b4`.
The eight build assets match the hashes in the release manifest. The totals
below use their file sizes; actual installed disk usage has not been measured.

| Item | Bytes | GiB |
| --- | ---: | ---: |
| Android data image, fully allocated | 34,359,738,368 | 32.000 |
| Copied system, graphics library and boot files | 2,332,663,987 | 2.172 |
| Installed launcher/package estimate | 2,348,810,240 | 2.188 |
| Combined estimate at full data-image allocation | 39,041,212,595 | 36.360 |
| Combined estimate plus 2 GiB free margin | 41,188,696,243 | 38.360 |
| Also retaining a separate downloaded PKG | 43,537,506,483 | 40.547 |

GiB means 1,073,741,824 bytes. Decimal GB means 1,000,000,000 bytes.
Allow about 42 GiB (45 GB) for this installation, including some free space.
The installer does not reserve that space. Any old downloads or backups on
the drive need to be counted separately.

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

The installed launcher estimate uses the PKG file size. It does not include
extra space the PS4 filesystem may use to store it.
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

## How the 32 GiB capacity is selected

This release starts at 32 GiB. The capacity is set in the build configuration.
The [package builder](../releases/v015/build-release.py)
requires `data-gib.txt` to contain `32`, compiles the installer with
`EDITION_GIB=32`, and records the edition and logical byte count in its manifest.
The [installer](../releases/v015/source/install-prebuilt.c) copies that capacity
file alongside the Android files and checks the installed edition on later runs.

The supplied first-boot script reads `data-gib.txt`, creates `data.img.part`
with `truncate -s` using the capacity multiplied by 1,073,741,824, and formats
that file with `mke2fs` as ext4. After checking it, it renames the file to
`data.img`. Formatting applies to this image file, not the PS4 drive.
That script is bundled in the external initramfs input; it is not currently
included as standalone source in the public checkout.

The first-boot script accepts 32, 64 or 128 GiB, but this package builder is
configured for 32 GiB. Building a larger edition requires updating the capacity
asset, compiler definition, package naming and manifest values together. This
is not an end-user capacity setting, and 64/128 GiB editions are not provided
by this release.

Existing images are checked against the selected capacity. Changing the number
does not expand an existing filesystem: the current installer rejects an
edition mismatch and has no resize operation. The first-boot code creates a
new image at the configured size; it cannot expand an image that already
contains your data.
