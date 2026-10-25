# Android TV for PS4

![Android TV for PS4](branding/repository-banner.svg)

Android TV 13 on a PlayStation 4, based on **BRTDTV's Android TV x86** build. Install one PKG, open it from the home screen, and the console boots straight into Android TV from its internal drive. Your apps, accounts and settings are kept between launches.

[Download](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.1) · [Installation](docs/INSTALL.md) · [Compatibility](docs/COMPATIBILITY.md) · [Hardware support](docs/HARDWARE.md) · [Release notes](docs/RELEASE-NOTES.md) · [How it works](docs/DEVELOPMENT.md) · [Build it](docs/BUILD.md) · [Contribute](CONTRIBUTING.md)

## Version 1.1

- **Android TV 13**, with 32 GiB of Android storage
- **One 3.12 GB PKG**, downloaded from Google Drive. No joining needed.
- Runs on **any firmware with GoldHEN that the Linux loader has offsets for**: 5.05, 6.72, 7.00–7.55, 8.00–8.52, 9.00–9.60, 10.00–10.71, 11.00, 11.02, 11.50–11.52, 12.00–12.52 and 13.00–13.52
- No console model is blocked. Tested on a fat CUH-1102A on 13.52; everything else is waiting on test reports.

The 32 GiB is how much Android can store. It is not the download size, and space on the PS4 drive is only used as Android fills it. Nothing is repartitioned: Android lives in ordinary files on the existing PS4 filesystem.

Slim and Pro models use a different southbridge. The kernel has drivers for them, but nobody has reported a boot yet. If you try one, please [report how far it got](https://github.com/odiecay/android-tv-ps4/issues/new?template=console-report.yml), even if it fails.

## Quick start

1. Download **Android-TV-for-PS4-1.1.pkg** from the [1.1 release page](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.1) ([checksum and tips](docs/DOWNLOAD.md)).
2. Copy the PKG to an exFAT USB drive and install it with GoldHEN's **Package Installer**.
3. Enable **GoldHEN → Servers → BinLoader** (port 9090).
4. Open **Android TV for PS4**.

**The first launch takes 5–10 minutes** while Android is installed to the internal drive and set up. Leave the console alone while progress or the Android animation is showing. After that, Android boots in about **2 minutes**.

To launch again later, load GoldHEN, make sure BinLoader is on, and open the app. In Android, **Restart** takes you back to the PS4 system and **Shut down** turns the console off.

Booting needs no PC, network or internet connection. The app hands its payload to GoldHEN on the console itself. Once Android is running, it manages Wi-Fi and Ethernet on its own.

If the launcher reports that BinLoader is unavailable, close the app, turn BinLoader off and on again, and reopen it. If startup stops with error 12, restart the PS4 and open the app before doing anything else. More fixes are in the [installation guide](docs/INSTALL.md#troubleshooting).

## What's included

**YouTube, Spotify, VLC, Jellyfin, Kodi, Plex, TV Bro, BiglyBT, Crossy Road and AIDA64** come pre-installed, along with Google Play services and the Play Store. Sign in with your own accounts. [Exact app versions](docs/APPS.md).

Working on the test console:

- HDMI picture and sound
- Wi-Fi, Ethernet and Bluetooth
- DualShock 4 and Google TV Streamer remote; the PS button goes to Home
- Google sign-in, YouTube (signed in), Spotify, Kodi and Kayo
- Restart to PS4 mode and power-off from Android

Known limitations: this isn't a Google-certified device, and there is no HDCP. Some protected streams won't play (7plus is one), and YouTube needs you to sign in. Details are in [Compatibility](docs/COMPATIBILITY.md#known-issues).

## How it works

```mermaid
flowchart TD
    A[GoldHEN and PS4 launcher] --> B[Install or verify internal files]
    B --> C[Send bundled payload to 127.0.0.1:9090]
    C --> D[Prepare Linux memory, verify kernel and initramfs]
    D --> E[Launcher releases the display; payload hands over]
    E --> F[Linux and initramfs]
    F --> G[Open internal storage; mount system and user data]
    G --> H[Apply PS4 graphics, input and network setup]
    H --> I[Android init, SurfaceFlinger and the TV launcher]
```

Android runs on a Linux kernel booted directly on the console, with full access to the GPU, display, audio and network hardware. The PS4 system comes back when the console restarts.

The Android system image is read-only. PS4-specific changes are applied in memory at each boot, and your data lives in a separate ext4 image. The [architecture guide](docs/DEVELOPMENT.md) walks through the code, and [Storage](docs/STORAGE.md) explains disk usage.

## Help wanted: test reports

1.1 lets every console try, so what's needed now is people running it on other models and firmware. If you test it, [open a console report](https://github.com/odiecay/android-tv-ps4/issues/new?template=console-report.yml) with your model, firmware and how far it got. "Black screen after the Linux text" is useful too. Anyone with PS4 Linux experience on Slim or Pro hardware is especially welcome.

## Development

The source is in [`releases/release-1.0/`](releases/release-1.0/): native launcher, modified kexec loader, boot runtime, tests and artwork. Start with the [build guide](docs/BUILD.md), then [Contributing](CONTRIBUTING.md) for areas that need work and how to report a test.

## Credits

- **BRTDTV / TD Android TV**: the Android TV x86 distribution this port is built on. [Channel](https://www.youtube.com/@TDAndroidTVnoPC) · [Community](https://t.me/+t15cB5esYJUxZjdh)
- **PS4 Linux contributors**: the PS4 kernel and [Linux loader](https://github.com/ps4-linux/ps4-linux-loader).
- **[GoldHEN](https://github.com/GoldHEN/GoldHEN)**: homebrew environment and payload loader.
- **OpenOrbis**, **Scene-Collective** and **sleirsgoevy**: PS4 toolchain, payload SDK and libjbc.
- **Ps3itaTeam**: the Liverpool raster configuration used in the graphics fix.
- **Android-x86, AOSP, Linux, Mesa** and the app developers.

[Full credits](docs/CREDITS.md) · [Artwork sources](docs/ASSETS.md). Android TV and PlayStation are trademarks of their respective owners. This is an independent homebrew project and is not affiliated with Google or Sony.
