# Compatibility and test status

## Hardware target

| Component | Current target |
| --- | --- |
| Console | PlayStation 4 CUH-1102A |
| Southbridge | Aeolia |
| PS4 firmware | 13.52; payload checks `13.520.001` |
| Android | Android TV 13, API 33, based on BRTDTV Android TV x86 |
| Kernel | PS4 Linux 6.15.4 adaptation |
| Graphics reservation | Loader requests 2048 MiB |
| Storage edition | 32 GiB sparse userdata image |
| Boot receiver | GoldHEN BinLoader on loopback port 9090 |

Other PS4 models and firmware versions are not validated. The base distribution's compatibility fingerprint is not proof of a newer Android version or Google certification.

## Release package

`Android-TV-for-PS4.pkg` — **3,108,306,944 bytes** (approximately 3.11 GB), 32 GiB edition.

SHA256:

```text
5564ccb30329123407ad03769732c0c4fc4e63084b1795d7fc7faf04dcf8ff25
```

The package includes the signed APK set, native x86/x86-64 Google Play services libraries and both Mesa raster corrections. The boot service attempts to set the friendly device name to **PlayStation 4**, but the fresh setup test still showed the base name. Set **Device name** in Android Settings if needed; this was verified separately and preserves the compatibility model.

Package structure, digests and signatures passed validation, and the transferred file matched its SHA256 by full readback. The same package has since completed a fresh installation and reached Android TV successfully, confirmed by the console operator. Allow 5–10 minutes initially and about 2 minutes for subsequent boots. Hardware and service behaviour are described below.

## Hardware observations

The following functions have worked on the stated console during development:

- Android setup, Google sign-in and internal-drive relaunch.
- YouTube picture and sound, including signed-in playback using version 7.27.302.
- Kayo sign-in and streaming.
- HDMI video and audio with the YV12 video-layout correction.
- Wi-Fi and Ethernet connectivity.
- Bluetooth pairing/navigation with a DualShock 4 and Google TV Streamer 4K remote.
- Controller PS/Home mapping.
- Physical restart to PS4 mode and console shutdown.
- Corrected browser icons and Crossy Road assets with the Liverpool raster configuration.

These observations describe the tested hardware and app paths. They do not establish compatibility with every PS4 revision, peripheral, streaming service or app update. Use the [setup checklist](RELEASE-CHECKLIST.md) to report your configuration and results.

## Known issues and limits

| Item | Behaviour and scope |
| --- | --- |
| Linux startup memory allocation | An earlier boot attempt during testing failed to allocate the 12,305,408-byte contiguous kernel buffer after three attempts (`ENOMEM`, code 12). That attempt completed file installation but did not start Linux. A later fresh install and boot succeeded; the earlier allocation failure's underlying cause is not established. |
| GoldHEN payload execution | A retry following that failed attempt delivered the full payload, but GoldHEN reported “failed to launch payload, error: 1.” The launcher can remain waiting for a startup report even though execution failed. A received-payload banner is not proof of Linux startup. |
| BinLoader connection refused | Error 61 means no connection was established and no payload bytes were sent. Closing the app and toggling BinLoader has recovered this condition. Empty TCP health probes also disturbed the receiver during testing; do not scan/probe its payload port. [Recovery](INSTALL.md#if-binloader-startup-stops). |
| YouTube | Version 7.27.302 ARM64 with native Play services plays signed-in selections, including a previously failing video, as unencrypted VP9 at 1080p/1440p. Guest playback previously requested a missing secure decoder. Hardware-secure playback is not fixed by sign-in. |
| Native Play services | Version 26.11.32 (190800) resolves the ARM JNI/provider mismatch and permits provisioning when installed as an update. The packaged APK replaces the original service in its privileged product location. That update test does not establish every first-run TV setup or Store flow. |
| Power cleanup | The supervisor releases app/service binds before the overlay, app filesystem and PS4 filesystem. Host tests cover dependency order and refusal to power off with busy mounts. Earlier physical power tests used an earlier runtime. |
| 7plus protected video | Audio with missing video and an HDCP error; the current connector/DRM path does not supply the required HDCP protection. |
| Kayo controller selection | On a screen in Kayo 4.6.1, DualShock 4 X did not advance, while the Google TV Streamer remote's select button did. Use a TV remote for that screen. X uses Android's standard gamepad A mapping with a Select fallback; no global game-control remapping is applied in this package. |
| Graphics | The 32-bit Liverpool correction passed all 40 depth/stencil cases, compared with 27 failures before correction; the YouTube spinner was visually confirmed corrected. Both 32-bit and 64-bit corrections are encoded in the boot inputs. |
| Kodi first launch | The runtime removes the inherited Linux `HOME=/` so Kodi can choose Android app storage. |
| Android shell application | Earlier logs contain repeated `setgroups` failures involving an invalid supplementary GID. ADB shell access still worked; the cause is unresolved. |
| Setup navigation | Backward jumps and repeated setup pages have been reported. No fix for that behaviour is claimed. |
| Phone and remote features | Spotify Connect, YouTube phone pairing and generic casting are distinct mechanisms. Bluetooth navigation alone does not establish voice search, TV power/volume, shortcut keys or every controller feature. |
| App updates | Store updates can change ABI selection and service behaviour. Exact bundled versions are listed in [Apps](APPS.md). |
| Security configuration | SELinux is permissive and authenticated network ADB is enabled. This homebrew OS is not a certified retail Android TV device. |

## Reporting a result

Include the package SHA256, console model and firmware, and whether this was a fresh installation or a subsequent launch. For startup failures, include the last visible stage and exact error. For media issues, distinguish sign-in, menu navigation, actual video playback, advertisements and phone control.

The [checklist](RELEASE-CHECKLIST.md) covers first installation, boot timings, Google/YouTube/Spotify sign-in, phone pairing, bundled apps, networking, Bluetooth, physical power and persistence. Keep account identifiers, pairing codes and private logs out of public reports.

## Source build verification

A clean source export built a complete PKG with fresh pinned libjbc and payload-SDK checkouts, a generated SFO/template and the recorded external runtime inputs. All nine helper objects matched their recorded hashes. Ten host regression suites passed, and the build output passed package structure, hash and signature validation. See [Build](BUILD.md) for the source/input boundary and commands.
