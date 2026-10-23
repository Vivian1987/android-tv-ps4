# Android TV 13 for PS4

![Android TV for PS4](branding/repository-banner.svg)

I took **BRTDTV's Android TV 13 for PCs** and adapted it to run on the PS4.
You install and launch it through a PS4 app. Android lives in files on the
existing internal drive, so there's no repartitioning.

## Release

**v0.15 · Android TV 13 · 32 GiB**

`Android-TV-PS4-13-v0.15-32GiB.pkg` · 2.35 GB

The package is built but has not been published to
[GitHub Releases](https://github.com/odiecay/android-tv-ps4/releases).
It has passed package checks; console testing is incomplete.

This build targets **Aeolia** hardware. v0.14 installed and booted with
Ethernet on **CUH-1102A, firmware 13.52**. Other models, firmware versions and streaming apps are unverified.

## Installation

You need GoldHEN. Allow about **42 GiB (45 GB)** for a fully used installation,
a retained PKG download and some free space. This is a planning estimate, not
the minimum needed to install; initial disk use is smaller.

1. Load GoldHEN and enable BinLoader on port **9090**.
2. Install the PKG with the PS4 package installer.
3. Open **Android TV for PS4** from the home screen. On first launch it copies
   the system and boot files, boots Linux, and creates Android's data image.
4. Wait for Android TV to start, then complete setup.

For later boots, load GoldHEN, enable BinLoader and open the app again. It
reuses the installation and keeps your apps and settings. Restarting the
console returns to the PS4 operating system.

## Storage

This release uses a **32 GiB sparse data image** for Android's apps, settings
and downloads. It occupies space as data is written, sharing the internal
drive with your PS4 games. The system files and launcher use additional space.

[Storage details](docs/STORAGE.md) cover the disk-space calculation, how the
system and data images are mounted, and how the 32 GiB capacity is set.

## Source

The [developer notes](docs/DEVELOPMENT.md) explain how the port works, the
decisions behind it and what to consider when changing it.

The current installer is in [`releases/v015`](releases/v015/).
[Build instructions](docs/BUILD.md) list the tools and external files it needs,
with a source map for installation, file copying and power control.

If you use a coding agent to explore the project, ask it to read those files
and show the code behind its explanation.

## Credits

This port builds on **BRTDTV's Android TV x86** work.

- [BRTDTV Telegram group](https://t.me/+7cbIufx3Eh5hZmYx)
- [New Telegram group](https://t.me/+t15cB5esYJUxZjdh)
- [TD Android TV no PC — YouTube](https://www.youtube.com/@TDAndroidTVnoPC)

[Artwork sources and font licence](docs/ASSETS.md).
