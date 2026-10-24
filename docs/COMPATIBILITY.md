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

`Android-TV-for-PS4.pkg` — **3,108,306,944 bytes** (approximately 3.11 GB), 32 GiB edition.

SHA256:

```text
5564ccb30329123407ad03769732c0c4fc4e63084b1795d7fc7faf04dcf8ff25
```

This is the golden candidate selected for the final [release walkthrough](RELEASE-CHECKLIST.md). Package validation passed. The signed APK set, both Google Play services library architectures and the persistent graphics corrections are included. The friendly device name defaults to **PlayStation 4**, while the compatibility model is preserved.

**Console acceptance failed at Linux startup and is under investigation.** The checklist records first installation, Google/YouTube/Spotify sign-in and phone pairing, app playback, networking, Bluetooth controls, physical power and relaunch. A transferred package is not an installed or accepted package.

The current fresh file installation completed. One boot attempt delivered and executed the full payload but failed to allocate the 12,305,408-byte contiguous kernel image buffer (`ENOMEM`, code 12), before Linux handoff. A later attempt delivered the payload but GoldHEN reported execution failure, leaving the launcher waiting for a status report. An earlier empty TCP health probe had also disturbed BinLoader; the next controlled test must use a clean session with no payload-port probing. These failures are not Android playback or device-name failures.

The preceding console test completed installation and boot after one BinLoader connection-refused recovery. Its live YouTube/Play services fixes informed this build; those observations do not substitute for this exact package's fresh test.

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
| YouTube playback | YouTube 7.27.302 ARM64 and native Play services run on the test console. After sign-in, normal selections and a previously failing video play unencrypted VP9 at 1080p/1440p. Guest playback previously requested a missing secure decoder; hardware-secure playback is not fixed. Fresh combined-package testing is required. |
| Native Play services | Version 26.11.32 (190800) resolves the ARM JNI/provider mismatch and permits app provisioning when installed as an update. The same signed APK and both native library sets are now packaged in the original privileged product location. Fresh TV setup and Play Store checks remain. |
| BinLoader connection refused on first launch | Observed on this candidate; close/toggle/reopen recovery worked. [Steps](INSTALL.md#if-binloader-startup-stops). |
| Bundled-app shutdown cleanup | The rebuilt supervisor unmounts application binds and the privileged Play services bind before the overlay, app SquashFS and PS4 filesystem. Host tests cover ordering and busy-mount refusal; console validation is required. |
| 7plus protected video | Audio with missing video and HDCP error; current Widevine/connector state does not supply the required HDCP path. |
| 32-bit Mesa | The same Liverpool correction now passes all 40 depth/stencil cases (27 failed before). YouTube's spinner is visually confirmed corrected. Both boot-script copies include the hash-checked correction; a fresh packaged boot remains to be tested. |
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
