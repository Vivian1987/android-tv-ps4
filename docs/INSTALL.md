# Installing Android TV for PS4

## What you need

- A PS4 running GoldHEN on one of the [firmware versions the loader supports](COMPATIBILITY.md#firmware). It has been tested on a fat CUH-1102A on 13.52; other models and firmware are untested, so please [report how it goes](COMPATIBILITY.md#reporting-a-result).
- `Android-TV-for-PS4-1.1.pkg` ([download](DOWNLOAD.md)).
- An exFAT-formatted USB drive.
- Free space on the PS4's internal drive. Android starts small and grows as you use it. If you fill all 32 GiB and keep the PKG on the console, allow about **43 GiB** ([how that's calculated](STORAGE.md)).
- A controller. USB is easiest for setup; Bluetooth devices can be paired once Android is running.

## First installation

1. Copy `Android-TV-for-PS4-1.1.pkg` to the top level of the USB drive and plug it into the PS4.
2. Load GoldHEN and install the PKG with the **Package Installer**.
3. In **GoldHEN → Servers**, enable **BinLoader** on port **9090**.
4. Open **Android TV for PS4** from the home screen.
5. Wait for installation and startup to finish, then go through Android TV setup.

**The first launch takes 5–10 minutes.** The launcher copies Android to the internal drive, then the console switches to Linux and Android prepares its storage and apps. Leave the console on while the installer progress or the Android animation is showing. Later launches skip the installation and take about **2 minutes**.

The 5–10 minutes is a guide; timing depends on the console and drive. An error message means something has gone wrong, so don't keep waiting. If the screen stays blank with no animation well past that time, see [Troubleshooting](#troubleshooting).

Booting doesn't need a PC, network or internet connection. The launcher sends its payload to GoldHEN on the console itself (`127.0.0.1`).

## What you'll see

| Stage | What's happening |
| --- | --- |
| Installer slides and progress | Copying the Android system, apps, graphics and startup files to the internal drive. |
| Startup progress | GoldHEN runs the boot payload, which loads Linux into memory and checks it. |
| Screen blanks, Linux text appears | The console switches from the PS4 system to Linux. Your TV may briefly lose signal. |
| Android animation | Android is starting. On the first boot it also sets up apps and storage. |
| Android setup | Choose language, network and account, then you're in. |

## Launching again

Load GoldHEN, make sure BinLoader is on, and open **Android TV for PS4**. Your apps, accounts, Wi-Fi and Bluetooth pairings are all kept.

In Android, **Restart** returns the console to the PS4 system, where GoldHEN needs to be loaded again. **Shut down** powers the console off. Android unmounts its storage cleanly before either one.

Reinstalling the same PKG keeps your existing Android data. It doesn't reset anything.

## Updating from 1.0

Install the 1.1 PKG over 1.0 with the Package Installer and open the app. The installer reuses your existing Android files and data, so your apps and logins stay. 1.1 keeps its boot files in `/user/app/ps4-android/boot` instead of `/data/linux/boot`; the old 1.0 copies in `/data/linux/boot` are no longer used (see [Removing Android](#removing-android)).

## Network and controllers

Set up Wi-Fi or Ethernet in Android's settings. These are separate from the PS4's own network settings.

To pair Bluetooth devices, go to **Settings → Remotes & accessories → Add accessory**:

- **Google TV Streamer 4K Voice Remote:** hold **Back + Home** for about three seconds, then select the remote.
- **DualShock 4:** unplug USB, make sure the controller is off, then hold **SHARE + PS** until the light bar flashes. Select it and accept any prompt.

On the controller, the PS button goes to Android Home. To use the DualShock 4 on the PS4 system again, connect it by USB and press PS.

## Signing in

**Google account (Play Store):** on the sign-in screens, press **down** on the D-pad a couple of times to reach the email and password boxes, and again to reach the **I agree** button.

**YouTube:** sign in with the QR code or phone flow. Signed-in playback works; guest mode can fail with a secure-decoder error. To control YouTube from your phone, use YouTube's link-with-TV-code option.

**Spotify:** sign in with the QR code, PIN or phone. To play from your phone, pick **PlayStation 4** in Spotify Connect while both are on the same network.

## Troubleshooting

**"BinLoader unavailable" or error 61.** The launcher couldn't reach GoldHEN's BinLoader. To fix it:

1. Press **PS** and fully close **Android TV for PS4**.
2. In **GoldHEN → Servers**, turn **BinLoader** off and back on.
3. Reopen the app.

You don't need to reinstall, because a completed installation is reused. Don't test port 9090 with a port scanner or `nc`: an empty connection can disrupt BinLoader.

**Error 12 during startup ("Not enough free memory to start Linux right now").** Linux needs one large block of free memory, and the PS4 may not have one after it's been busy, especially straight after copying and installing the PKG. Restart the console, load GoldHEN and open the app before doing anything else. Your installation is kept. If it keeps happening, report it with `launcher-boot.log`.

**"Firmware X isn't supported yet."** The Linux loader has no kernel offsets for your firmware, so nothing was loaded and nothing was changed. The supported list is in [Compatibility](COMPATIBILITY.md#firmware).

**"Last start stopped at: ..."** The previous Linux start didn't finish, and this shows the last step it reached. The launcher carries on and tries again. If it keeps stopping at the same step, include that line in your report.

**GoldHEN says the payload was received, but nothing happens.** "Received" only means the payload arrived, not that it ran. Restart the console, reload GoldHEN and try again. If GoldHEN shows "failed to launch payload", include that in your report.

**Blank screen for a long time.** Note how long it's been and the last thing you saw on screen, then hold the power button to turn the console off and start it again. On consoles other than the tested one, this is the most likely way a start fails.

## Logs and reporting problems

**If a start fails after Linux has started,** the screen says so and asks for a USB stick. Plug in a FAT32 or exFAT stick, now or later, and the reports are copied to a folder called `AndroidTV-PS4-report-…` on it. The console keeps watching for a stick until it's turned off, and it never writes to its own drive for this.

The console also keeps the logs in `/user/app/ps4-android`, which you can reach over GoldHEN's FTP server:

- `launcher-boot.log`: installation and handing off to Linux, including firmware and southbridge
- `hardware.txt`: the console's chips, which kernel booted and which drivers loaded
- `boot-progress.log`, `boot.log`, `kernel.log`: Linux startup
- `android-stages.log`: Android startup

To report a problem, open a [console report](https://github.com/odiecay/android-tv-ps4/issues/new?template=console-report.yml) and drag the files (or a ZIP of the USB report folder) into the **Logs** box.

Include your console model, firmware, the PKG SHA256, whether it was a first install or a later launch, and the last thing on screen. Remove account names, Wi-Fi names and IP addresses from logs first.

Network ADB is enabled on port 5555 and requires you to approve each computer on the TV. No debugging keys ship with the release.

## Removing Android

There's no one-click uninstall yet. All of Android's files, including its boot files, are in `/user/app/ps4-android`. Deleting the app from the home screen doesn't remove them; delete that folder over FTP instead. If you installed 1.0, it also left boot files in `/data/linux/boot`. Other Linux setups on the console may use that folder too, so check before deleting anything there. Never format the PS4 drive to remove Android.
