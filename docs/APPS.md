# Bundled apps

These apps come pre-installed, so you can open them without visiting the Play Store. They start with no data. Sign in with your own accounts and bring your own subscriptions, servers and media.

| App | Version | Architecture | What it's for | Source |
| --- | --- | --- | --- | --- |
| YouTube | 7.27.302 | arm64 (translated) | Video; sign in to watch | [Play Store](https://play.google.com/store/apps/details?id=com.google.android.youtube.tv) |
| Spotify | 9.1.94.1926 | x86_64 | Music and Spotify Connect | [Play Store](https://play.google.com/store/apps/details?id=com.spotify.tv.android) |
| VLC | 3.7.1 | x86_64 | Local and network media player | [VideoLAN](https://get.videolan.org/vlc-android/3.7.1/VLC-Android-3.7.1-x86_64.apk) |
| Jellyfin | 0.19.10 | x86_64 | Jellyfin server client | [GitHub](https://github.com/jellyfin/jellyfin-androidtv/releases/download/v0.19.10/jellyfin-androidtv-v0.19.10-release.apk) |
| Kodi | 21.3 | x86 | Media centre | [Kodi](https://mirrors.kodi.tv/releases/android/x86/kodi-21.3-Omega-x86.apk) |
| Plex | 10.28.0.3441 | x86_64 | Plex client | [Plex](https://downloads.plex.tv/Kepler/kepler-x86_64-googlePlay-10.28.0.3441-367a93b4.apk) |
| TV Bro | 2.1.6 | x86_64 | Web browser built for TV remotes | [GitHub](https://github.com/truefedex/tv-bro/releases/download/v2.1.6/tvbro-2.1.6-generic-geckoExcluded.apk) |
| BiglyBT | 1.3.3 | Java | Torrent client | [GitHub](https://github.com/BiglySoftware/BiglyBT-Android/releases/download/v1.3.3/BiglyBT-1.3.3.apk) |
| Crossy Road | 7.14.0 | arm64 (translated) | Game | [Play Store](https://play.google.com/store/apps/details?id=com.yodo1.crossyroad) |
| AIDA64 | 2.22 | x86_64 | Hardware and system information | [Play Store](https://play.google.com/store/apps/details?id=com.finalwire.aida64) |

Native x86 or x86_64 builds are used wherever one exists. YouTube and Crossy Road run ARM code through Android's translation layer.

## Google Play services

The base distribution ships an ARM-only Google Play services. This release replaces it with the x86/x86_64 version **26.11.32 (190800-885792908)**, which fixes the provisioning errors the ARM version caused on the console.

## YouTube

YouTube works once you're signed in. Videos play at 1080p and 1440p. Guest mode can fail with a secure-decoder error, so sign in first. Content that requires hardware DRM may not play.

## About the packaging

Every APK is the unmodified original, with its signature intact. Native libraries are pre-extracted, because Android doesn't do that for built-in system apps. Apps live on a read-only image, so an app update from the Play Store installs alongside the bundled version as usual.

[`bundled-apps.json`](../releases/release-1.0/bundled-apps.json) lists every APK and split with its size, SHA256 and signer. [`bundled-apps-image.json`](../releases/release-1.0/bundled-apps-image.json) describes the prepared app image. Neither file, nor the release itself, contains any account data.

Open-source app credits are in [Credits](CREDITS.md).
