# Installing and using Android TV for PS4

## Requirements

The current target is **CUH-1102A / Aeolia / firmware 13.52**, running GoldHEN. The payload has a 13.52 firmware check; enabling GoldHEN on another firmware does not make that firmware supported.

You need the release PKG and enough internal drive space. Allow about **43 GiB** if Android's full 32 GiB capacity will be used and the downloaded PKG is also kept internally. Initial usage is much smaller. [Storage accounting](STORAGE.md) explains the estimate.

A USB controller is useful for setup. A DualShock 4 and a Google TV Streamer 4K remote have been paired over Bluetooth during development.

## First installation

First [download and join the two release parts](DOWNLOAD.md), then verify the reconstructed PKG's SHA256.

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

**Allow 5–10 minutes for the first installation and boot after opening the launcher.** It installs the Android files to the console, extracts the runtime components and prepares Android's storage, apps and operating environment. Leave the console on while the installation progress or Android animation is running. After the first installation, allow about **2 minutes** for subsequent boots; they reuse that setup.

The display can reconnect during the handoff and graphics initialization. The 5–10 minutes is a guide, not a countdown; timing varies with the console and storage. An explicit startup error is a failure to investigate, not part of that wait. If the display stays blank with no animation or progress beyond that window, note the elapsed time and last visible stage and follow the troubleshooting below. The [walkthrough](RELEASE-CHECKLIST.md#1-fresh-installation-and-startup) includes a timing table for reporting your experience.

## If BinLoader startup stops

For the observed connection-refused failure, recover in this order:

1. Press **PS** and fully close **Android TV for PS4**.
2. Open **GoldHEN → Servers → BinLoader** and toggle it **off**, then **on**.
3. Reopen **Android TV for PS4**.

You do not need to reinstall a completed installation. The launcher checks the existing files and tries a new local payload delivery. A successful send is only the first part of booting; the progress display and logs distinguish delivery from Linux preparation.

Error `61` means the launcher could not connect to BinLoader; no payload bytes were delivered. Avoid probing port 9090 with a scanner or an empty TCP connection, which can disturb the receiver.

Error `12` during Linux preparation means the loader could not allocate a required contiguous memory buffer. The recorded allocation failure during testing involved the 12,305,408-byte kernel image buffer. Installation had completed, but Linux had not started. Preserve `launcher-boot.log` and report the failure; repeatedly reopening the app is not a confirmed remedy.

A payload-received banner confirms delivery, not execution. If the launcher remains waiting, the GoldHEN log and payload status identify whether the runner actually started. See [known startup issues](COMPATIBILITY.md#known-issues-and-limits).

## Returning to PS4 and launching again

Android **Restart** is mapped to a physical console restart into PS4 mode. Android **Shut down** is mapped to physical power-off. GoldHEN must be loaded again after restarting before opening the launcher.

The previous installation, apps, accounts and pairings are stored in Android's data image. A normal subsequent launch reuses that image. Reinstalling the same storage edition is not a factory reset.

The power supervisor closes Android's app and system mounts before requesting the console power operation.

## Connectivity and controllers

Wi-Fi credentials are entered in Android. Ethernet obtains its configuration through Android's network services. PS4-mode networking and the Android connection are separate.

Open **Settings → Remotes & accessories → Add accessory**. For a **Google TV Streamer 4K Voice Remote**, hold **Back + Home** for about three seconds, then select the remote. For a **DualShock 4**, unplug USB and hold **SHARE + PS** with the controller initially off until the light flashes. Select the controller and accept any authentication prompt. See [Google](https://support.google.com/chromecast/answer/10089168?hl=en) and [Sony](https://www.playstation.com/en-ca/support/hardware/ps4-pair-dualshock-4-wireless-with-pc-or-mac/) for their pairing instructions.

The controller's PS/Home action returns to Android Home. Test wireless operation with USB unplugged. Navigation has worked with both devices during development; voice search, TV power/volume and special buttons are separate capabilities. To use a DualShock 4 in PS4 mode again, connect it by USB and press PS if it does not reconnect.

If **Kayo 4.6.1** ignores X on a selection screen, use the **Google TV remote's centre/select button**; it advanced the screen in testing. The controller uses Android's standard gamepad mapping, and some app screens handle it differently from a TV remote. A global remap is not included because it would also change game controls.

## Accounts, phone pairing and the device name

After setup, check Android's **Device name** setting and name it **PlayStation 4** if the base device name is still shown. Apps that read this setting, including this Spotify build's discovery service, can use it. The boot service attempts to supply the PS4 name; the fresh setup test still showed the base name, so check it explicitly. The app-facing compatibility model remains the base distribution's model; changing that model previously caused YouTube rejection.

Open YouTube and use its QR/phone sign-in flow. After sign-in, select videos through the TV app and check picture and sound. Phone sign-in and controlling playback from a phone are different flows: use YouTube's TV-code/pairing instructions for the latter. This does not imply generic Chromecast support.

Open Spotify and use its offered QR/PIN or phone sign-in method. On the same network, open Spotify Connect on your phone and select **PlayStation 4**. Confirm that the console plays the audio and responds to the phone. [Spotify's TV sign-in guide](https://support.spotify.com/article/spotify-on-tv/) and [YouTube's TV sign-in guide](https://support.google.com/youtube/answer/3015415) describe these flows.

YouTube signed-in playback works in development testing; guest playback previously requested an unavailable secure decoder. Neither sign-in nor bundled Google services makes the PS4 a certified Android TV device or supplies hardware HDCP. [App versions and known limits](APPS.md) document the selected builds.

## Diagnostics

The console stores installation and boot reports under `/user/app/ps4-android` in PS4 mode. `launcher-boot.log` records local delivery and handoff preparation; `boot-progress.log`, `kernel.log`, and `android-stages.log` cover Linux and Android startup.

ADB is configured on TCP port 5555 with authentication. Developer options, USB debugging and an authorization prompt may be needed before a computer can connect. No developer computer's trusted ADB key is shipped. Only authorize computers you intend to use for debugging.

Before posting logs, remove account identifiers, Wi-Fi names, IP addresses and session information. Include the PKG SHA256, console model, firmware, last visible stage, and whether this was a first install or a later launch.

## Removing or resetting Android

Deleting the launcher from the PS4 home screen does not reliably describe the state of the separate Android files. Android storage lives at `/user/app/ps4-android`; boot assets live at `/data/linux/boot`. The latter path can also be used by other Linux setups.

There is no supported one-click uninstall or storage-resize operation in this build. Back up Android data before any manual reset. Do not format the PS4 drive or delete another Linux installation's boot files to remove Android.
