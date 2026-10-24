# Android TV for PS4 1.0

The first public release: Android TV 13 on PlayStation 4, installed from a single PKG and booted from the console's internal drive.

[Download 1.0](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.0) · [Join the download](DOWNLOAD.md) · [Install](INSTALL.md) · [Compatibility](COMPATIBILITY.md)

## Highlights

- **Android TV 13** with Google Play services and the Play Store
- **One-PKG install** from the PS4 home screen. Nothing is repartitioned, and Android lives in ordinary files on the internal drive.
- **Boots without a PC or network.** The launcher hands its payload to GoldHEN on the console itself.
- **32 GiB of Android storage** that only takes up space as you use it
- **Ten apps pre-installed:** YouTube, Spotify, VLC, Jellyfin, Kodi, Plex, TV Bro, BiglyBT, Crossy Road and AIDA64 ([versions](APPS.md))
- **Bluetooth controllers and remotes:** DualShock 4 and Google TV Streamer remote tested; the PS button goes to Home
- **Wi-Fi and Ethernet**, managed by Android
- **Restart and Shut down** in Android return to the PS4 system or power the console off

## Requirements

- PS4 **CUH-1102A (Aeolia)** on firmware **13.52** with GoldHEN. Other models and firmware aren't supported yet.
- GoldHEN **BinLoader** enabled on port **9090**
- An exFAT USB drive to install the PKG
- About 8 GiB of free internal space to install. Usage grows as Android fills its storage, up to about 43 GiB if all 32 GiB is used ([Storage](STORAGE.md)).

## Install

1. Download both PKG parts and the joining tool from the release page.
2. Windows: double-click **Join-PKG-Windows.cmd**. Linux/macOS: run `sh join-pkg.sh`. Wait for **READY**.
3. Copy `Android-TV-for-PS4.pkg` to an exFAT USB drive and install it with GoldHEN's Package Installer.
4. Enable BinLoader and open **Android TV for PS4**.

The **first launch takes 5–10 minutes**. Later launches take about **2 minutes**.

## Known issues

- No HDCP, and this isn't a Google-certified device. Some DRM-protected video won't play (7plus, for example).
- YouTube needs you to sign in; guest playback can fail.
- On one Kayo 4.6.1 screen, the controller's X button does nothing. Use the Google TV remote's centre button.
- Setup may leave the base device name in place. Set it to **PlayStation 4** in Settings so Spotify Connect shows the right name.
- If BinLoader is unavailable (error 61), close the app, toggle BinLoader off and on, and reopen it.

See [Compatibility](COMPATIBILITY.md) for the full list.

## Credits

Built on **BRTDTV's Android TV x86**, with work from the PS4 Linux community, GoldHEN, OpenOrbis, Scene-Collective, sleirsgoevy, Ps3itaTeam, Android-x86, AOSP, Linux, Mesa and the app developers. [Full credits](CREDITS.md).
