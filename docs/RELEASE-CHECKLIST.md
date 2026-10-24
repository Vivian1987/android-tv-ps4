# Testing checklist

Use this list to test a build on your console and share the results. Mark each item **Pass**, **Fail** or **Not tested** with a short note. Include the PKG SHA256 from [Compatibility](COMPATIBILITY.md) so results can be matched to a build. Leave out account names, QR codes, pairing codes and raw logs.

## 1. Installation and first boot

- [ ] Install the PKG and open the launcher. Installation progress appears and keeps moving.
- [ ] Note any blank screen or loss of HDMI signal, and how long it lasted.
- [ ] Android reaches the setup screens.
- [ ] Complete setup. Note any screen that jumps back, repeats or freezes.

Start a timer when you open the launcher:

| Milestone | First install | Later launch |
| --- | --- | --- |
| Launcher opened | 0:00 | 0:00 |
| Installation finished | | |
| First Linux text | | |
| Android animation | | |
| Setup or home screen | | |
| Longest blank screen | | |

## 2. Google account and apps

- [ ] Sign in to Google, including phone/QR approval if offered.
- [ ] All ten bundled apps are present.
- [ ] Install and open an app from the Play Store.
- [ ] **Settings → Device name** shows or can be set to **PlayStation 4**.
- [ ] Storage in Settings looks sensible, and installing an app doesn't report a false lack of space.

## 3. YouTube

- [ ] Sign in with the QR/phone flow.
- [ ] Play several videos from the menus. Check picture, sound, seeking, pause and resume.
- [ ] Thumbnails, the loading spinner and controls look correct, with no lines or blocky artwork.
- [ ] Link your phone with a TV code and control playback from it.
- [ ] Try guest mode and note what happens.

## 4. Spotify

- [ ] Sign in and play music.
- [ ] On a phone on the same network, choose **PlayStation 4** in Spotify Connect. Audio comes from the TV.
- [ ] Play/pause, skip, seek and volume work from the phone.
- [ ] Switching away from Spotify and back keeps the session working.

## 5. Bluetooth and controls

Pair under **Settings → Remotes & accessories → Add accessory**.

- [ ] **Google TV Streamer remote:** hold **Back + Home** for about three seconds and pair. Directions, Select, Back and Home work.
- [ ] **DualShock 4:** unplug USB, turn it off, hold **SHARE + PS** until the light flashes and pair. Navigation and PS/Home work without USB.
- [ ] Play Crossy Road with the controller and note any missed or delayed inputs.
- [ ] Both devices reconnect after rebooting Android.
- [ ] Note voice search, TV power/volume and other extra buttons separately.

## 6. Network

- [ ] Internet works over Ethernet.
- [ ] Connect Wi-Fi, unplug Ethernet, and confirm a new video or page still loads.
- [ ] Plug Ethernet back in; the connection returns without restarting.
- [ ] With the console's network unplugged, the launcher still boots Android.

## 7. Bundled apps

| App | Check |
| --- | --- |
| VLC | Play a local or network file; video, audio and seeking work. |
| Jellyfin | Connect to a server and play something, if you have one. |
| Kodi | Complete first launch, change a setting, play a file, and check the setting survives a relaunch. |
| Plex | Sign in and play available media. |
| TV Bro | Load a page, go back, and check text and icons look right. |
| BiglyBT | Open it and choose a download folder. |
| Crossy Road | Play, and check graphics and controls. |
| AIDA64 | Browse the hardware pages without a crash. |

## 8. Power and persistence

- [ ] Android **Restart** returns to the PS4 system.
- [ ] Reload GoldHEN and reopen the launcher. Android starts without repeating installation or setup.
- [ ] Sign-ins, Wi-Fi, installed apps and the device name are all still there.
- [ ] Bluetooth devices reconnect and media plays.
- [ ] Android **Shut down** turns the console off completely.

## For maintainers: before publishing a build

- [ ] Package structure, digests and signatures validate. The copy on the console matches the local SHA256.
- [ ] Sources, runtime snapshot, app manifest and artwork match the package being published.
- [ ] No accounts, saved Wi-Fi, ADB keys, private keys or developer identifiers are included.
- [ ] Sections 1–8 have been run on this exact package. Any change after testing means testing again.
- [ ] Release notes only claim what was tested.
