# Installation and use checklist: Android TV for PS4 1.0

Use this walkthrough for the **32 GiB** release. Include the exact PKG hash from [Compatibility](COMPATIBILITY.md) with your results so reports from different builds stay distinguishable.

Record each item as **Pass**, **Fail**, or **Not tested**, with a short observation. A failure should include the last visible message and whether reopening the app changes it. Keep account names, QR codes, pairing codes and raw private logs out of public reports.

## 1. Fresh installation and startup

- [ ] Start with no Android installation at the active install paths. Removing the PS4 launcher alone is not a reset; the maintainer must confirm the clean test state.
- [ ] Install the PKG, open the launcher once, and let it install and boot without a PC sending a boot payload or changing files mid-boot.
- [ ] Installer progress is visible, readable and advances. Record any error, unexpected exit or recovery needed.
- [ ] Observe the Linux text, display transitions and Android animation. Record each period with a blank screen or no HDMI signal.
- [ ] Android reaches setup, with no existing account, Wi-Fi credentials or Bluetooth pairing inherited from the developer.
- [ ] Complete setup once. Record any page that jumps backwards, repeats, freezes or fails to play an introductory video.

Start a stopwatch when opening the launcher and record elapsed times:

| Milestone | First installation | Existing-install launch |
| --- | --- | --- |
| Launcher opened | 0:00 | 0:00 |
| File installation/checks complete | | |
| First Linux text | | |
| Android animation visible | | |
| Setup or usable launcher | | |
| Longest blank/no-signal interval | | |

The first-boot guide asks users to allow 5–10 minutes. Record actual timings here alongside the package hash so that guidance can be refined for different consoles and drives.

## 2. Google account and applications

- [ ] Complete Google sign-in using the normal TV flow, including phone/QR approval if offered.
- [ ] Open Play Store, search for an app not already bundled, install it and launch it.
- [ ] Check that all ten bundled apps are present before installing anything from the Store.
- [ ] Android's device name is **PlayStation 4**. The compatibility model remains separate; do not change it for this test.
- [ ] Check storage in Settings. Install an additional app and confirm it does not incorrectly report insufficient space.

## 3. YouTube

- [ ] Open bundled YouTube **7.27.302** and sign in using the QR/phone flow.
- [ ] Browse and select several videos through the TV app's ordinary menus. Test a previously failing selection as well as a different new video.
- [ ] Check picture, sound, seeking, pausing, resuming, and switching videos. Watch long enough to distinguish the video itself from an advertisement.
- [ ] Check the spinner, thumbnails and overlay controls for distorted/pixelated assets, horizontal lines, or old boot frames.
- [ ] Link the phone to YouTube on the TV using the TV-code/pairing flow, then control playback from the phone. Record the method used; TV-code pairing is not proof of generic Chromecast support.
- [ ] Record guest-mode behaviour separately. Earlier guest requests selected an unavailable secure decoder; signed-in playback is the verified development route.

## 4. Spotify

- [ ] Sign in through the offered QR/PIN or phone flow, then play audio.
- [ ] Open Spotify Connect on a phone on the same network. Select **PlayStation 4** and confirm audio comes from the console's TV/output.
- [ ] Test play/pause, next track and seeking from the phone. Record whether volume control works in the actual output configuration.
- [ ] Switch away from Spotify and return. Confirm the session and controls remain usable.

## 5. Bluetooth and controls

Use Android **Settings → Remotes & accessories → Add accessory**. Accept a pairing/authentication prompt when offered.

- [ ] **Google TV Streamer 4K Voice Remote:** hold **Back + Home** for about three seconds to enter pairing mode, then select it in Android. Test directions, Select, Back and Home. [Google's pairing instructions](https://support.google.com/chromecast/answer/10089168?hl=en).
- [ ] **DualShock 4:** disconnect USB, turn the controller off, then hold **SHARE + PS** until its light bar flashes. Pair the wireless controller in Android. Test navigation and PS/Home without reconnecting USB. [Sony's pairing instructions](https://www.playstation.com/en-ca/support/hardware/ps4-pair-dualshock-4-wireless-with-pc-or-mac/).
- [ ] Play Crossy Road using the controller; report missed, repeated or delayed inputs.
- [ ] Test both paired devices after the subsequent Android boot without removing/re-pairing them.

Record voice search, remote power, TV volume/mute, shortcut buttons and controller extras separately. Pairing and navigation alone do not establish support for those functions. Returning the DualShock 4 to PS4 mode may require USB and the PS button; Android and PS4 mode use separate Bluetooth environments.

## 6. Network independence

- [ ] Verify internet access through Ethernet.
- [ ] Connect Android to Wi-Fi, then unplug Ethernet while Android is running. Open a new stream/page to confirm Wi-Fi carries traffic.
- [ ] Reconnect Ethernet and confirm connectivity returns without a console restart.
- [ ] On a later PS4-mode launch, disable/disconnect external networking but leave GoldHEN BinLoader enabled. Confirm the installed launcher still boots Android. Reconnect Android to Wi-Fi and verify internet access.

The phone used for local discovery should be on the same network as Android. Boot independence and online-service connectivity are separate tests.

## 7. Bundled app smoke tests

| App | Check |
| --- | --- |
| YouTube | Signed-in video/audio, ordinary menu selection and phone pairing as above. |
| Spotify | Sign-in, music and Connect as above. |
| VLC | Open a local or permitted network media file; check video/audio and seeking. |
| Jellyfin | Open the app; connect to an available server and play media if one is available. |
| Kodi | Complete first launch, change a setting, play a file, then confirm the setting survives relaunch. |
| Plex | Open/sign in and play available media; record account/server limitations separately. |
| TV Bro | Open a web page, navigate back and check text/icons render correctly. |
| BiglyBT | Open the interface and choose a writable download folder. If testing transfer, use an authorized small torrent and confirm pause/resume. |
| Crossy Road | Launch, play and check graphics plus controller input. |
| AIDA64 | Open and navigate hardware/system pages without a crash. |

A server/account-dependent test can be **Not tested**; that app's playback must then remain unclaimed in release notes. Installation alone is not a playback pass.

## 8. Power and persistence

- [ ] Choose Android **Restart**. The console returns to PS4 mode.
- [ ] Reload GoldHEN, enable BinLoader and open the installed launcher. It reuses Android data and does not repeat first-time installation/setup.
- [ ] Google/YouTube/Spotify sign-ins, Wi-Fi, installed apps and the friendly device name survive.
- [ ] Check Bluetooth reconnection and play media again after that boot.
- [ ] Choose Android **Shut down**. The console physically powers off, with no persistent black-screen/hung state.

## Build and distribution checks

- [ ] Package structure, digests and signatures pass; transferred PKG matches the local SHA256 by full readback.
- [ ] Source, runtime snapshot, APK versions/hashes, artwork and package manifest identify the exact package tested.
- [ ] No account data, saved network credentials, trusted ADB keys, private keys or developer identifiers are included. Review the fixed system input as well as newly added files.
- [ ] Record host checks, instrumented console results and human observations separately.
- [ ] Resolve mandatory boot/setup/sign-in/playback/network/power failures, or narrow the published claim explicitly. Record optional/unavailable service tests honestly.
- [ ] Verify third-party distribution terms, notices and source obligations, and the final binary download route/checksums.
- [ ] Freeze the tested artifact. Any later runtime or APK change requires testing the resulting package again.

Keep the completed checklist with the package hash. Unchecked items are not test results.
