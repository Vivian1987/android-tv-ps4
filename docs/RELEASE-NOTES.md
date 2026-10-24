# Android TV for PS4 1.0 — 32 GiB

[Installation](INSTALL.md) · [Package checksum and compatibility](COMPATIBILITY.md) · [Usage checklist](RELEASE-CHECKLIST.md)

[Download 1.0](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.0). GitHub hosts the PKG in two parts; [join them and verify the checksum](DOWNLOAD.md) before installing.

Android TV 13 boots directly on PlayStation 4 hardware through a PS4 home-screen launcher. The package installs its system and startup files on the internal drive. Later launches reuse your Android apps, accounts and settings.

## Package and requirements

- `Android-TV-for-PS4.pkg`, approximately **3.11 GB**.
- **32 GiB** of Android userdata capacity, allocated on the PS4 drive as it is used. No disk repartitioning or 32 GiB download is required.
- Tested development hardware: **CUH-1102A / Aeolia / firmware 13.52**, with GoldHEN. The payload checks this firmware; other models and firmware are not supported by the current test evidence.
- GoldHEN **BinLoader on port 9090** must be enabled. The launcher sends its bundled payload locally; boot does not require a PC, FTP, a router or internet access.
- Online services need internet access after Android starts. Android handles its own Ethernet and Wi-Fi settings.

## Included applications

**YouTube, Spotify, VLC, Jellyfin, Kodi, Plex, TV Bro, BiglyBT, Crossy Road and AIDA64** are bundled, along with native Google Play services. You can open them without downloading them first. You supply your own accounts, subscriptions, servers and media.

YouTube **7.27.302** and Crossy Road use ARM64 translation. Native x86/x86-64 builds are selected for other native-code applications; BiglyBT is Java-only. Exact signed APK versions and sources are in [Apps](APPS.md).

The default friendly device name is **PlayStation 4**, including the Android setting read by Spotify discovery. The compatibility model is kept separate so naming the console does not repeat the earlier YouTube compatibility rejection.

## First use

Load GoldHEN, enable BinLoader, install the PKG and open **Android TV for PS4**. **Allow 5–10 minutes for the first installation and boot.** Android's files are installed to the console, runtime components are extracted, and its storage, apps and environment are prepared. Leave the console on while installation progress or the Android animation is running. After the first installation, subsequent boots take about **2 minutes** and reuse the setup. HDMI can reconnect during the operating-system handoff; the [installation guide](INSTALL.md) explains each stage and how to distinguish the initial wait from a startup failure.

Sign into YouTube and Spotify using their offered phone/QR/PIN flows. Use Spotify Connect or YouTube's phone-pairing flow to control playback from another device. Pair accessories through Android's **Remotes & accessories** settings. A DualShock 4 and Google TV Streamer 4K Voice Remote have paired and navigated Android on the tested hardware. The checklist covers their buttons and reconnection separately.

Android **Restart** returns to PS4 mode; load GoldHEN again before opening Android TV. **Shut down** maps to console power-off. Accounts, apps, network settings and pairings live in persistent Android storage.

## Compatibility limits

Signed-in YouTube playback has worked with the current app and native services on the development console. Guest playback previously selected an unavailable secure decoder. 7plus protected playback has an unresolved HDCP limitation. This port does not establish Google certification, hardware-secure DRM or compatibility with every streaming service.

Startup issues include BinLoader connection refusal and a recorded failure to reserve the contiguous Linux kernel buffer. A later retry also failed to execute in GoldHEN after delivery. [Troubleshooting](INSTALL.md#if-binloader-startup-stops) distinguishes these errors; a completed Android installation is retained.

The runtime uses SELinux permissive mode and authenticated network ADB. Developer access requires authorization; developer accounts and trusted debugging keys are not bundled. This is a homebrew OS for the stated hardware, with service-specific limits documented in [Compatibility](COMPATIBILITY.md).

## Source and further development

The repository contains the port's launcher, payload/loader changes, runtime scripts, helper sources, kernel configuration/patch, graphics corrections, tests and packaging tools. [Build instructions](BUILD.md) identify the pinned source dependencies and external Android, graphics and APK inputs; this is not a full AOSP distribution source tree. [Contributing](../CONTRIBUTING.md) explains how to extend hardware support and provide useful test results.

Based on **BRTDTV's Android TV x86** distribution and the work of the PS4 Linux community, GoldHEN, OpenOrbis, Scene-Collective, sleirsgoevy, Ps3itaTeam, Android-x86, AOSP, Linux, Mesa and the bundled app authors. See [Credits](CREDITS.md).
