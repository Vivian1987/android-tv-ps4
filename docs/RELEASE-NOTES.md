# Release notes

## 1.1

More consoles and a single download. Thanks to everyone who commented and opened issues on 1.0; most of this release came from those reports.

[Download 1.1](DOWNLOAD.md) · [Install](INSTALL.md) · [Compatibility](COMPATIBILITY.md)

`Android-TV-for-PS4-1.1.pkg`, 3,123,052,544 bytes, SHA256 `57cfbaffa8b5e5a894bebfa15b4e61745cefe6a6ab25847d62916c4d88b30ff5`

### What's new

- **Every firmware the Linux loader supports.** The package now contains a kexec build for each firmware [ps4-linux-loader](https://github.com/ps4-linux/ps4-linux-loader) has kernel offsets for (5.05 to 13.52, [full list](COMPATIBILITY.md#firmware)), and picks the right one at launch. 1.0 only ran on 13.52.
- **No console model is blocked.** 1.0 stopped on anything but the Aeolia southbridge, both in the launcher and in the Linux start script. 1.1 records the southbridge in the log and carries on. Slim, Pro and Belize/Baikal fat models are untested; reports are very welcome.
- **Boots without Ethernet hardware.** A console with no Ethernet interface used to stop the Linux start; now it continues without it.
- **Single-file download** from Google Drive. No more joining parts.
- **Clearer errors.** Unsupported firmware, low memory (error 12) and boot-file problems now say what happened and what to do. If the previous Linux start didn't finish, the launcher shows the last step it reached.
- **More reliable video.** Some video could freeze after a few seconds while the sound kept playing, for example in YouTube and the NBA app. The graphics allocator now lays out video frames the way the PS4's GPU driver needs, so playback keeps going.
- **The controller works like a TV remote in every app.** X selects and Circle goes back everywhere. In 1.0, a few apps only listened to a TV remote on some screens, so the controller did nothing there, for example Kayo's sign-in button and going back in the NBA app.
- **Screensaver instead of sleep.** When idle, Android now shows a screensaver and keeps running. Android's sleep mode froze PS4 Linux, so the console needed a hard restart. A small stick dead zone also stops a resting DualShock 4 from keeping the screen awake.
- **Device name defaults to "PlayStation 4"**, so Spotify Connect and casting list the console by name.
- **Slim, Pro and Baikal hardware support.** Wi-Fi and Bluetooth firmware for the Marvell 88W8897 and MediaTek MT7668, a separate kernel for Baikal consoles with their Ethernet driver, and a graphics fix for the Pro's GPU. None of it has been tested on those consoles yet; see [Hardware support](HARDWARE.md).
- **Failed starts explain themselves.** If Linux can't start Android, it says why, makes it safe to power off, and copies its reports to a USB stick as soon as one is plugged in. Every start also saves a hardware report (`hardware.txt`) listing the console's chips and the drivers that loaded.
- **App storage folders work.** Android tags each app's shared-storage folder with an ext4 project ID, which the 1.0 kernel couldn't do, so apps were refused the folder. That made Google setup restart itself and some apps crash. The kernel now has quota support, new installs format Android storage with it, and existing installs get it added once at startup, checked before and after. It only happens if the running kernel can mount the result.
- **No background crash loop.** A permission in this Android build mapped to a group the system doesn't know, so the Shell app failed to start and was retried every 10 seconds. That mapping is removed at boot.
- **Faster launches.** The launcher used to re-read about 1.5 GB of installed files on every launch to check them, which could take up to two minutes after a restart and fragmented memory just before Linux needed it. Each file is now checked once and remembered until it or the package changes.
- **Clearer error screen.** When startup stops, the launcher stops its activity bar and leads with what to do, for example "Restart your PS4, then open Android TV again" when memory is short.
- **Internal drive found reliably.** Linux now finds the PS4's drive by its Android partition, so consoles whose internal drive sits behind a USB bridge aren't skipped.
- **Updating no longer fails with errno 17** when an older backup of the boot files is present.
- **Own boot folder.** Boot files now live in `/user/app/ps4-android/boot` instead of `/data/linux/boot`, so 1.1 can't collide with another PS4 Linux setup. That is the likely cause of the errno 13 install error reported on 1.0.

### Tested

Fresh install over FTP and first boot to Android TV with this exact package on a CUH-1102A on 13.52, plus video, controller, screensaver, Spotify Connect and the bundled apps. Everything else is waiting on [test reports](COMPATIBILITY.md#reporting-a-result).

### Updating

Delete Android TV for PS4 from the PS4 home screen, then install the 1.1 PKG. Your Android apps and data are stored separately and are kept ([details](INSTALL.md#updating-from-10)). If you had renamed the device, it's set to PlayStation 4 once; rename it again in Settings.

On the first start, Linux adds project quota support to Android's storage once. After that, the 1.0 kernel can't open it, so going back to 1.0 isn't supported.

The first launch after installing or updating is the one most likely to stop with "Restart your PS4, then open Android TV again" (code 12): installing the PKG and the launcher's one-time file check leave the PS4's memory too fragmented to load Linux. Restart, load GoldHEN and open the app. Restarting straight after installing avoids it ([details](INSTALL.md#troubleshooting)).

## 1.0

The first public release: Android TV 13 on PlayStation 4, installed from a single PKG and booted from the console's internal drive.

[1.0 release](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.0)

### Highlights

- **Android TV 13** with Google Play services and the Play Store
- **One-PKG install** from the PS4 home screen. Nothing is repartitioned, and Android lives in ordinary files on the internal drive.
- **Boots without a PC or network.** The launcher hands its payload to GoldHEN on the console itself.
- **32 GiB of Android storage** that only takes up space as you use it
- **Ten apps pre-installed:** YouTube, Spotify, VLC, Jellyfin, Kodi, Plex, TV Bro, BiglyBT, Crossy Road and AIDA64 ([versions](APPS.md))
- **Bluetooth controllers and remotes:** DualShock 4 and Google TV Streamer remote tested; the PS button goes to Home
- **Wi-Fi and Ethernet**, managed by Android
- **Restart and Shut down** in Android return to the PS4 system or power the console off

### Requirements

- PS4 **CUH-1102A (Aeolia)** on firmware **13.52** with GoldHEN. Other models and firmware aren't supported yet.
- GoldHEN **BinLoader** enabled on port **9090**
- An exFAT USB drive to install the PKG
- About 8 GiB of free internal space to install. Usage grows as Android fills its storage, up to about 43 GiB if all 32 GiB is used ([Storage](STORAGE.md)).

### Install

1. Download both PKG parts and the joining tool from the release page.
2. Windows: double-click **Join-PKG-Windows.cmd**. Linux/macOS: run `sh join-pkg.sh`. Wait for **READY**.
3. Copy `Android-TV-for-PS4.pkg` to an exFAT USB drive and install it with GoldHEN's Package Installer.
4. Enable BinLoader and open **Android TV for PS4**.

The **first launch takes 5–10 minutes**. Later launches take about **2 minutes**.

### Known issues

- No HDCP, and this isn't a Google-certified device. Some DRM-protected video won't play (7plus, for example).
- YouTube needs you to sign in; guest playback can fail.
- On one Kayo 4.6.1 screen, the controller's X button does nothing. Use the Google TV remote's centre button.
- Setup may leave the base device name in place. Set it to **PlayStation 4** in Settings so Spotify Connect shows the right name.
- If BinLoader is unavailable (error 61), close the app, toggle BinLoader off and on, and reopen it.

See [Compatibility](COMPATIBILITY.md) for the full list.

### Credits

Built on **BRTDTV's Android TV x86**, with work from the PS4 Linux community, GoldHEN, OpenOrbis, Scene-Collective, sleirsgoevy, Ps3itaTeam, Android-x86, AOSP, Linux, Mesa and the app developers. [Full credits](CREDITS.md).
