# Compatibility

## Supported hardware

| Component | Version 1.0 |
| --- | --- |
| Console | PlayStation 4 CUH-1102A (Aeolia southbridge) |
| Firmware | 13.52 with GoldHEN; the payload checks for `13.520.001` |
| Android | Android TV 13 (API 33), based on BRTDTV Android TV x86 |
| Kernel | PS4 Linux 6.15.4 |
| Graphics memory | 2048 MiB reserved for the GPU |
| Android storage | 32 GiB, allocated as used |
| Boot | GoldHEN BinLoader on port 9090 (local only) |

Other PS4 models and firmware versions haven't been tested. Supporting them requires porting work; changing the firmware check alone won't do it. Reports from other consoles are welcome, even when they fail ([how to report](#reporting-a-result)).

## Release package

`Android-TV-for-PS4.pkg`: **3,108,306,944 bytes** (3.11 GB)

```text
SHA256  5564ccb30329123407ad03769732c0c4fc4e63084b1795d7fc7faf04dcf8ff25
```

This exact package was installed fresh on the test console and booted to Android TV. Allow 5–10 minutes for the first boot and about 2 minutes after that.

## Tested and working

On the test console:

- Fresh installation, Android setup, Google sign-in and relaunching from the internal drive
- HDMI video and audio
- YouTube 7.27.302, signed in, at 1080p and 1440p
- Kayo sign-in and streaming
- Wi-Fi and Ethernet
- Bluetooth pairing and navigation with a DualShock 4 and a Google TV Streamer 4K remote
- PS button as Android Home
- Restart to PS4 mode and power-off from Android (last tested on the console with a slightly earlier boot runtime)
- Correct rendering of browser icons and Crossy Road graphics

Results may differ on other hardware, accessories, or newer versions of apps.

## Known issues

| Issue | Details |
| --- | --- |
| Protected video / HDCP | There is no HDCP on this path. 7plus plays audio with no video and reports an HDCP error. Other services with strict DRM may behave the same way. |
| YouTube guest mode | Guest playback can request a secure decoder that isn't available. Sign in to watch. |
| Kayo controller button | On one Kayo 4.6.1 selection screen, the DualShock 4's X button does nothing. The Google TV remote's centre button works there. |
| Device name | Setup may leave the base device name in place. Set **Device name** to **PlayStation 4** in Settings. Spotify Connect and similar apps show this name. |
| Setup navigation | Some setup screens have been reported to jump back or repeat. |
| BinLoader connection (error 61) | The launcher couldn't reach BinLoader. Close the app, toggle BinLoader off and on, and reopen it ([steps](INSTALL.md#troubleshooting)). |
| Startup memory (error 12) | One test boot failed to reserve memory for the kernel. A later fresh install booted normally; the cause isn't known. |
| Payload received but not run | GoldHEN may show the payload as received but then report "failed to launch payload". The launcher keeps waiting. Restart the console and try again. |
| Not certified | This isn't a Google-certified Android TV device. Some apps and services may refuse to run or limit playback. |
| App updates | Play Store updates can change how an app behaves. The bundled versions are listed in [Apps](APPS.md). |
| Security | SELinux runs in permissive mode, and network ADB is on with per-computer authorization. |

## Reporting a result

Include your console model, firmware, the PKG SHA256, and whether it was a first install or a later launch. For startup problems, add the last thing on screen and any error message. For video problems, say whether the app refused to play, played audio only, or showed broken video. Keep account names, codes and private logs out of public reports.

The [testing checklist](RELEASE-CHECKLIST.md) covers everything worth checking.
