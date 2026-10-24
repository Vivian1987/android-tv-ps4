# Installing Android TV for PS4

## What you need

- A **CUH-1102A (Aeolia) PS4 on firmware 13.52** running GoldHEN. Other models and firmware aren't supported yet, and the boot payload checks the firmware version.
- The joined `Android-TV-for-PS4.pkg` ([download and join guide](DOWNLOAD.md)).
- An exFAT-formatted USB drive.
- Free space on the PS4's internal drive. Android starts small and grows as you use it. If you fill all 32 GiB and keep the PKG on the console, allow about **43 GiB** ([how that's calculated](STORAGE.md)).
- A controller. USB is easiest for setup; Bluetooth devices can be paired once Android is running.

## First installation

1. Copy `Android-TV-for-PS4.pkg` to the top level of the USB drive and plug it into the PS4.
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

## Network and controllers

Set up Wi-Fi or Ethernet in Android's settings. These are separate from the PS4's own network settings.

To pair Bluetooth devices, go to **Settings → Remotes & accessories → Add accessory**:

- **Google TV Streamer 4K Voice Remote:** hold **Back + Home** for about three seconds, then select the remote.
- **DualShock 4:** unplug USB, make sure the controller is off, then hold **SHARE + PS** until the light bar flashes. Select it and accept any prompt.

On the controller, the PS button goes to Android Home. To use the DualShock 4 on the PS4 system again, connect it by USB and press PS.

**Kayo 4.6.1:** one selection screen ignores the controller's X button. The Google TV remote's centre button works there. The controller keeps standard gamepad mappings so games aren't affected.

## Signing in

**Device name:** after setup, check **Settings → Device name** and set it to **PlayStation 4** if it shows a different name. Apps like Spotify Connect show this name on your phone.

**YouTube:** sign in with the QR code or phone flow. Signed-in playback works; guest mode can fail with a secure-decoder error. To control YouTube from your phone, use YouTube's link-with-TV-code option.

**Spotify:** sign in with the QR code, PIN or phone. To play from your phone, pick **PlayStation 4** in Spotify Connect while both are on the same network.

## Troubleshooting

**"BinLoader unavailable" or error 61.** The launcher couldn't reach GoldHEN's BinLoader. To fix it:

1. Press **PS** and fully close **Android TV for PS4**.
2. In **GoldHEN → Servers**, turn **BinLoader** off and back on.
3. Reopen the app.

You don't need to reinstall, because a completed installation is reused. Don't test port 9090 with a port scanner or `nc`: an empty connection can disrupt BinLoader.

**Error 12 during startup.** Linux couldn't get a large enough block of memory. This happened once during testing and didn't recur after a fresh install. Restart the console, load GoldHEN and try again. If it keeps happening, report it with `launcher-boot.log`.

**GoldHEN says the payload was received, but nothing happens.** "Received" only means the payload arrived, not that it ran. Restart the console, reload GoldHEN and try again. If GoldHEN shows "failed to launch payload", include that in your report.

**Blank screen for a long time.** Note how long it's been and the last thing you saw on screen, then restart the console and try again.

## Logs and reporting problems

The console keeps install and boot logs in `/user/app/ps4-android`. You can reach them over GoldHEN's FTP server:

- `launcher-boot.log`: installation and handing off to Linux
- `boot-progress.log`, `kernel.log`: Linux startup
- `android-stages.log`: Android startup

When reporting a problem, include your console model, firmware, the PKG SHA256, whether it was a first install or a later launch, and the last thing on screen. Remove account names, Wi-Fi names and IP addresses from logs first.

Network ADB is enabled on port 5555 and requires you to approve each computer on the TV. No debugging keys ship with the release.

## Removing Android

There's no one-click uninstall yet. Android's files are in `/user/app/ps4-android` and its boot files are in `/data/linux/boot`. Deleting the app from the home screen doesn't remove them. Other Linux setups on the console may share `/data/linux/boot`, so check before deleting anything there. Never format the PS4 drive to remove Android.
