# Bundled applications

The manifest records the exact signed APKs and splits selected for the ten-app candidate. Each installation creates its own app data. APK signatures are preserved; extracted native libraries are copied unchanged into the system-app layout.

| App | Version | Selected native ABI | Source |
| --- | --- | --- | --- |
| YouTube | 7.05.301 | x86 | [Upstream/download](https://www.apkmirror.com/apk/google-inc/youtube-for-android-tv-android-tv/youtube-for-android-tv-7-05-301-release/youtube-for-android-tv-7-05-301-6-android-apk-download/) |
| Spotify | 9.1.94.1926 | x86_64 | [Upstream/download](https://play.google.com/store/apps/details?id=com.spotify.tv.android) |
| VLC | 3.7.1 | x86_64 | [Upstream/download](https://get.videolan.org/vlc-android/3.7.1/VLC-Android-3.7.1-x86_64.apk) |
| Jellyfin | 0.19.10 | x86_64 | [Upstream/download](https://github.com/jellyfin/jellyfin-androidtv/releases/download/v0.19.10/jellyfin-androidtv-v0.19.10-release.apk) |
| Kodi | 21.3 | x86 | [Upstream/download](https://mirrors.kodi.tv/releases/android/x86/kodi-21.3-Omega-x86.apk) |
| Plex | 10.28.0.3441 | x86_64 | [Upstream/download](https://downloads.plex.tv/Kepler/kepler-x86_64-googlePlay-10.28.0.3441-367a93b4.apk) |
| TV Bro | 2.1.6 | x86_64 | [Upstream/download](https://github.com/truefedex/tv-bro/releases/download/v2.1.6/tvbro-2.1.6-generic-geckoExcluded.apk) |
| BiglyBT | 1.3.3 | Java-only | [Upstream/download](https://github.com/BiglySoftware/BiglyBT-Android/releases/download/v1.3.3/BiglyBT-1.3.3.apk) |
| Crossy Road | 7.14.0 | arm64-v8a (translation) | [Upstream/download](https://play.google.com/store/apps/details?id=com.yodo1.crossyroad) |
| AIDA64 | 2.22 | x86_64 | [Upstream/download](https://play.google.com/store/apps/details?id=com.finalwire.aida64) |

The package has ten apps across sixteen APK files, including language/density/native splits. `bundled-apps.sfs` also holds their extracted native libraries because Android scans these as immutable system applications. Selecting a universal APK does not force ARM translation: the preparation script chooses x86-64 or x86 where present. Crossy Road is the explicit ARM64 exception.

The APK set has passed file, package, ABI and signing checks. Application playback and sign-in require console testing; the table is not a claim that every service works. The current candidate has a newly reported YouTube playback failure awaiting runtime diagnosis.

App updates can change code, ABI selection or service behaviour. The repository retains the version/signature manifest for diagnosis. Account requirements and playback restrictions remain those of each service.

## Distribution and provenance

[bundled-apps.json](../releases/release-1.0/bundled-apps.json) contains package names, signer digests, APK sizes and hashes. [bundled-apps-image.json](../releases/release-1.0/bundled-apps-image.json) records the prepared filesystem. Neither contains account state.

Open-source app code and notices are linked in [Credits](CREDITS.md). Proprietary app redistribution permissions and applicable source-delivery obligations must be settled before publishing a bundle. Download provenance and a matching signature establish file identity, not permission to redistribute.
