# Installing and using Android TV for PS4

## Requirements

The current target is **CUH-1102A / Aeolia / firmware 13.52**, running GoldHEN. The payload has a 13.52 firmware check; enabling GoldHEN on another firmware does not make that firmware supported.

You need the release PKG and enough internal drive space. Allow about **43 GiB** if Android's full 32 GiB capacity will be used and the downloaded PKG is also kept internally. Initial usage is much smaller. [Storage accounting](STORAGE.md) explains the estimate.

A USB controller is useful for setup. A DualShock 4 and a Google TV Streamer 4K remote have been paired over Bluetooth during development.

## First installation

1. Load GoldHEN in PS4 mode.
2. In **GoldHEN → Servers**, enable **BinLoader** on **9090**.
3. Install `Android-TV-for-PS4.pkg` using the PS4 package installer.
4. Open **Android TV for PS4** from the home screen.
5. Let installation and startup finish, then complete the Android TV setup screens.

The launcher contains the installation and boot files. FTP is only one way of transferring the PKG during development; it is not required to launch Android. The payload is delivered internally to `127.0.0.1`, so the PS4 does not need a LAN address or an internet connection to boot.

## What appears on screen

| Stage | What the console is doing |
| --- | --- |
| Installer slides and progress | Copying the compressed system, bundled apps, graphics and startup files to internal storage. |
| Startup progress in the app | GoldHEN receives the local payload, which reads the boot files, prepares memory and verifies the prepared images. |
| HDMI transition and Linux text | The console changes operating systems; Linux initializes hardware and opens the internal filesystem. |
| Android animation | Android starts its graphics and framework services. On first boot it also prepares apps and user storage. |
| Android setup | Choose language, network and account options, then enter the launcher. |

The first start takes longer than later starts. The display can reconnect during the handoff and graphics initialization. Timings depend on the actual console and build; the release walkthrough will supply measured timings rather than a guaranteed countdown.

## If BinLoader startup stops

For the observed connection-refused failure, recover in this order:

1. Press **PS** and fully close **Android TV for PS4**.
2. Open **GoldHEN → Servers → BinLoader** and toggle it **off**, then **on**.
3. Reopen **Android TV for PS4**.

You do not need to reinstall a completed installation. The launcher checks the existing files and tries a new local payload delivery. A successful send is only the first part of booting; the progress display and logs distinguish delivery from Linux preparation.

This recovery was observed after the 1.0 candidate's first installation. The first attempt returned `ECONNREFUSED` (`61`) with zero payload bytes sent; after the toggle, the retry delivered the complete payload and reached Linux preparation. This identifies the failed stage, not the underlying reason the listener was unavailable.

## Returning to PS4 and launching again

Android **Restart** is mapped to a physical console restart into PS4 mode. Android **Shut down** is mapped to physical power-off. GoldHEN must be loaded again after restarting before opening the launcher.

The previous installation, apps, accounts and pairings are stored in Android's data image. A normal subsequent launch reuses that image. Reinstalling the same storage edition is not a factory reset.

The new bundled-app filesystem adds a shutdown cleanup requirement that must be resolved and console-tested before this candidate is accepted. Current status is recorded in [Compatibility](COMPATIBILITY.md).

## Connectivity and controllers

Wi-Fi credentials are entered in Android. Ethernet obtains its configuration through Android's network services. PS4-mode networking and the Android connection are separate.

To pair a Bluetooth device, put it into pairing mode and use Android's accessory settings. Accept an authentication prompt if one appears. The Sony controller keylayout maps the PS/Home button to Android Home.

## Diagnostics

The console stores installation and boot reports under `/user/app/ps4-android` in PS4 mode. `launcher-boot.log` records local delivery and handoff preparation; `boot-progress.log`, `kernel.log`, and `android-stages.log` cover Linux and Android startup.

ADB is configured on TCP port 5555 with authentication. Developer options, USB debugging and an authorization prompt may be needed before a computer can connect. No developer computer's trusted ADB key is shipped. Only authorize computers you intend to use for debugging.

Before posting logs, remove account identifiers, Wi-Fi names, IP addresses and session information. Include the PKG SHA256, console model, firmware, last visible stage, and whether this was a first install or a later launch.

## Removing or resetting Android

Deleting the launcher from the PS4 home screen does not reliably describe the state of the separate Android files. Android storage lives at `/user/app/ps4-android`; boot assets live at `/data/linux/boot`. The latter path can also be used by other Linux setups.

There is no supported one-click uninstall or storage-resize operation in this build. Back up Android data before any manual reset. Do not format the PS4 drive or delete another Linux installation's boot files to remove Android.
