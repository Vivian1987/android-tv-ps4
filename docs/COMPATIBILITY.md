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

## Current package

`Android-TV-for-PS4.pkg` — 2,977,038,336 bytes.

SHA256:

```text
a65d8c2a1c31f66e3a7a180fe0f7c3ea7806659e933dfee5b31ae6f199190a3e
```

Package validation and a complete transfer readback passed. The fresh console installation completed. Its first launch failed at local BinLoader connection with errno 61 and zero bytes delivered. Closing the app and toggling BinLoader allowed a retry to deliver the payload and reach Linux preparation; the operator reports startup working.

**This exact candidate is not accepted for public release.** The source now includes clearer recovery text for the next build. The source correction now unmounts app binds and their filesystem in dependency order. Host tests pass; physical power behaviour requires a new package test.

## Demonstrated during development

- Android setup, Google sign-in and internal-drive relaunch.
- YouTube video and audio after correcting the app-facing model.
- Kayo sign-in and streaming on this console.
- Native video output and corrected YV12 video layout.
- Wi-Fi connectivity and Ethernet connectivity.
- Bluetooth pairing with a DualShock 4 and Google TV Streamer 4K remote.
- Controller Home mapping.
- Physical restart to PS4 and shutdown on the prior runtime.
- Corrected browser icons and Crossy Road assets after the 64-bit Mesa raster fix.

These observations concern their recorded development builds. They do not substitute for testing all of those paths in the final combined PKG.

## Known issues and limits

| Item | Evidence / scope |
| --- | --- |
| YouTube playback on the ten-app candidate | Operator reports videos do not play. Runtime inspection awaits fresh-install ADB authorization; no cause or fix established. |
| BinLoader connection refused on first launch | Observed on this candidate; close/toggle/reopen recovery worked. [Steps](INSTALL.md#if-binloader-startup-stops). |
| Bundled-app shutdown cleanup | The new app SquashFS mount is absent from the current supervisor's unmount list. The corrected source passes host cleanup tests; console validation of the rebuilt package is required. |
| 7plus protected video | Audio with missing video and HDCP error; current Widevine/connector state does not supply the required HDCP path. |
| 32-bit Mesa | The Liverpool raster correction was applied and measured in the 64-bit driver. No equivalent 32-bit correction is claimed. |
| Kodi first launch | Source correction removes inherited `HOME=/`; writable app data needs acceptance on the packaged runtime. |
| Android shell application | Prior runtime logs show repeated `setgroups` failure involving an invalid supplementary GID. ADB shell access still worked. Root cause and packaged-runtime impact need investigation. |
| Setup navigation | Backward jumps during setup were reported. The media-extractor correction does not establish that it resolves navigation. |
| App updates | Store updates can change architecture selection and service behaviour. Tested versions are listed in [Apps](APPS.md). |
| Security configuration | The runtime uses SELinux permissive mode and authenticated network ADB; it is a homebrew/development OS, not a certified retail TV image. |

## Acceptance record

A release record must name the exact PKG hash and separate host tests, console observations and user observations. The full first-install walkthrough includes network setup, bundled app discovery and playback, graphics, Bluetooth, restart/shutdown, and launching the existing installation again.

Public reports should not include private console logs or device identifiers. A model/firmware/package-hash report and the relevant redacted error are enough to begin diagnosis.

## Source build verification

A clean export of the current source built a complete PKG using fresh libjbc
and payload-SDK checkouts, a generated SFO/template, and runtime assets extracted
from the candidate. All nine helper objects matched the original inputs byte
for byte. Ten host regression programs passed from that clean source tree.
The reconstructed package passed structural/hash/signature validation. This
checks the documented build path; it is not console acceptance of that package.
