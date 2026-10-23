# Android TV 13 for PS4

![Android TV for PS4](branding/repository-banner.svg)

I took **BRTDTV's Android TV 13 for PCs** and adapted it to run on the PS4.
You install and launch it through a PS4 app. Android lives in files on the
existing internal drive, so there's no repartitioning.

[Release and compatibility](#release-and-compatibility) · [Requirements](#requirements) · [Preview](#preview) · [Installation](#installation) · [Storage](#storage) · [Source](#source) · [Credits](#credits)

## Release and compatibility

**v0.15 — Android TV 13, 32 GiB edition**

Package: `Android-TV-PS4-13-v0.15-32GiB.pkg` · 2.35 GB

The PKG has not been uploaded to [GitHub Releases](https://github.com/odiecay/android-tv-ps4/releases) yet.

| Version | Verification |
| --- | --- |
| v0.14 | Installed and booted on CUH-1102A (Aeolia), firmware 13.52, with Ethernet working. |
| v0.15 | Package checks passed; console testing is incomplete. |

Testing so far covers CUH-1102A on firmware 13.52. Other models, firmware
versions and individual streaming apps need their own testing.

## Requirements

- GoldHEN with BinLoader enabled on port **9090**.
- About **42 GiB (45 GB) of available internal-drive space** for
  a full data image, the installed app, system files, a copy of the downloaded
  PKG and some free space. Initial use is smaller; see [Storage](#storage).
- Internet access for online setup and apps.

## Installation

Installing the PKG puts the launcher on the PS4 home screen. On first launch,
it copies the system and boot files, then boots Linux to prepare the data
image and start Android TV. Later launches reuse that installation and keep
your apps and settings.

1. Load GoldHEN and enable BinLoader on port **9090**.
2. Install the PKG with the PS4 package installer.
3. Open **Android TV for PS4** from the home screen.
4. Let the first-run installation finish and wait for Android TV to start.
5. Complete Android TV setup.

For later boots, load GoldHEN, enable BinLoader and open the app again.
Restarting the console returns to the PS4 operating system.

## Storage

This release uses a **32 GiB sparse data image** for Android's apps, settings
and downloads. It occupies space as data is written, sharing the internal
drive with your PS4 games. The system files and launcher use additional space.

The 32 GiB capacity is set in the build configuration. It can be changed for a
larger build, but changing that value won't resize an existing installation.
This release starts at 32 GiB. Formatting leaves slightly less usable space
inside Android.

Android's system stays compressed and read-only. The PS4-specific changes are
applied in memory at boot, while apps and settings are saved in the data image.
That keeps the base system intact and your data persistent between boots.

Linux mounts `system.sfs`, then the `system.img` inside it. The separate
`data.img` is an ext4 filesystem mounted as a virtual disk. The installer
creates these files on the existing PS4 filesystem without partitioning or
formatting the drive.

With the data image fully allocated, the data, copied system files and
installed launcher total approximately **36.4 GiB (39 GB)**. Keeping the downloaded PKG
on the internal drive adds about **2.19 GiB**. The 42 GiB recommendation
includes room for overhead and free space. These figures are calculated from
the build files; actual installed disk usage has not been measured.

The installer's **2 GiB spare-space check is not the total space requirement**
and does not reserve room for future writes. The [storage documentation](docs/STORAGE.md)
explains the calculation and how the image capacity is configured.

Uninstalling the launcher PKG does not delete the Android data image.

## Preview

![Android TV setup screen](releases/v015/artwork/android-first-run.png)

![Controller navigation preview](releases/v015/artwork/controller-preview.png)

*Current installer artwork, updated since the last PKG build.*

## Source

The current installer is in [`releases/v015`](releases/v015/).
[Build instructions and source map](docs/BUILD.md) explain where to start
reading and which tools and files you need to build it. Older versions are in
[`installer/`](installer/README.md).

You can ask a coding agent to read the source and explain the parts you want
to understand. For example:

- [How does installation work?](releases/v015/source/install-prebuilt.c)
- [What happens if a copy is interrupted?](releases/v015/source/image-copy.c)
- [How does Android's restart request reach the console?](releases/v015/power/android-supervisor.c)

Ask it to show you the code behind its explanation and check which version
it is reading. For console test results, see [Release and compatibility](#release-and-compatibility).

The build needs external components listed in the build instructions. Each
build records their hashes in a manifest so its inputs can be identified.

## Credits

Thanks to **BRTDTV** for their work bringing Android TV to x86 PCs. This PS4
port builds on that foundation.

- [BRTDTV Telegram group](https://t.me/+7cbIufx3Eh5hZmYx)
- [New Telegram group](https://t.me/+t15cB5esYJUxZjdh)
- [TD Android TV no PC — YouTube](https://www.youtube.com/@TDAndroidTVnoPC)

[Artwork sources and font licence](docs/ASSETS.md).
