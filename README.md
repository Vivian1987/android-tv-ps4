# Android TV 13 for PS4

![Android TV for PS4](branding/repository-banner.svg)

A PS4 port of **BRTDTV's Android TV x86 builds**, installed and launched through
a PS4 app. It runs from the internal drive, with no PC needed after installation.
Android's files sit inside the existing PS4 filesystem. No repartitioning.

[Release and compatibility](#release-and-compatibility) · [Requirements](#requirements) · [Preview](#preview) · [Installation](#installation) · [Storage](#storage) · [Source](#source) · [Credits](#credits)

## Release and compatibility

**v0.15 — Android TV 13, 32 GiB edition**

Package: `Android-TV-PS4-13-v0.15-32GiB.pkg` · 2.35 GB

The PKG has not been uploaded to [GitHub Releases](https://github.com/odiecay/android-tv-ps4/releases) yet.

| Version | Verification |
| --- | --- |
| v0.14 | Installed and booted on CUH-1102A (Aeolia), firmware 13.52, with Ethernet working. |
| v0.15 | Package checks passed; console testing is incomplete. |

Other PS4 models and firmware versions have not been tested. Booting Android
and working Ethernet do not establish compatibility with individual streaming
apps or their playback requirements.

## Requirements

- GoldHEN with BinLoader enabled on port **9090**.
- About **42 GiB (45 GB) of available internal-drive space** to accommodate
  a full data image, installed app, system files, a retained PKG download and
  free-space margin. Initial use is smaller; see [Storage](#storage).
- Internet access for online setup and apps.

## Installation

1. Load GoldHEN and enable BinLoader on port **9090**.
2. Install the PKG with the PS4 package installer.
3. Open **Android TV for PS4** from the home screen.
4. Leave it running while it copies the system and prepares the boot files.
   It then boots Linux, creates Android's data storage and starts Android TV.
5. Complete Android TV setup.

For later boots, load GoldHEN, enable BinLoader and open the app again.
It keeps your Android data and skips the installation. Restarting the console
returns to the PS4 operating system.

## Storage

The installer stores Android as files on the internal drive. It does not
create partitions or format the drive.

`system.sfs` is the compressed, read-only system. Linux mounts it, then mounts
the `system.img` inside it. Apps, settings and downloads go into `data.img`,
an ext4 filesystem that Linux mounts as a virtual disk.

This release creates a **32 GiB sparse data image** on first boot. It takes up
physical drive space as data is written, rather than reserving all 32 GiB at
once. Android and your PS4 games share the drive's free space. Formatting
means Android reports slightly less than 32 GiB usable.

32 GiB is the capacity chosen for this release. The image does not automatically
grow beyond it, and the installer does not resize an existing image.

At full data-image allocation, the data, copied system files and installed
launcher total approximately **36.4 GiB (39 GB)**. Keeping the downloaded PKG
on the internal drive adds about **2.19 GiB**. The 42 GiB planning figure above
also leaves room for overhead and free space; it is an estimate, not measured
console allocation.

The installer's **2 GiB spare-space check is not the total space requirement**
and does not reserve room for future writes. The [storage documentation](docs/STORAGE.md)
explains the calculation and how the image capacity is configured.

PS4-specific system changes are applied at boot in a RAM overlay. Apps and
settings persist in the data image. Uninstalling the launcher PKG does not
delete that image.

## Preview

![Android TV setup screen](releases/v015/artwork/android-first-run.png)

![Controller navigation preview](releases/v015/artwork/controller-preview.png)

*Installer artwork in the current source. These revisions postdate the recorded PKG build.*

## Source

The current installer is in [`releases/v015`](releases/v015/).
[Build instructions and source map](docs/BUILD.md) identify its entry points,
required tools and external inputs. Older versions are in
[`installer/`](installer/README.md).

You can ask a coding agent to read the source and explain the parts you want
to understand. For example:

- [How does installation work?](releases/v015/source/install-prebuilt.c)
- [What happens if a copy is interrupted?](releases/v015/source/image-copy.c)
- [How does Android's restart request reach the console?](releases/v015/power/android-supervisor.c)

Have it point to the code it used. Check that it is reading the right version;
code alone does not prove a feature has been tested on hardware.

Not every bundled component can be rebuilt from this checkout alone. A build
produces a manifest of its input hashes; changes on `main` do not update an
already-built PKG.

## Credits

Thanks to **BRTDTV** for their work bringing Android TV to x86 PCs. This PS4
port builds on that foundation.

- [BRTDTV Telegram group](https://t.me/+7cbIufx3Eh5hZmYx)
- [New Telegram group](https://t.me/+t15cB5esYJUxZjdh)
- [TD Android TV no PC — YouTube](https://www.youtube.com/@TDAndroidTVnoPC)

[Artwork sources and font licence](docs/ASSETS.md).
