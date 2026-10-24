# Bundled applications

The manifest records the exact signed APKs and splits selected for the ten-app candidate and its native Google Play services replacement. Each installation creates its own app data. APK signatures are preserved; extracted native libraries are copied unchanged into the system-app layout.

| App | Version | Selected native ABI | Source |
| --- | --- | --- | --- |
| YouTube | 7.27.302 | arm64-v8a (translation) | [Play Store](https://play.google.com/store/apps/details?id=com.google.android.youtube.tv) |
| Spotify | 9.1.94.1926 | x86_64 | [Upstream/download](https://play.google.com/store/apps/details?id=com.spotify.tv.android) |
| VLC | 3.7.1 | x86_64 | [Upstream/download](https://get.videolan.org/vlc-android/3.7.1/VLC-Android-3.7.1-x86_64.apk) |
| Jellyfin | 0.19.10 | x86_64 | [Upstream/download](https://github.com/jellyfin/jellyfin-androidtv/releases/download/v0.19.10/jellyfin-androidtv-v0.19.10-release.apk) |
| Kodi | 21.3 | x86 | [Upstream/download](https://mirrors.kodi.tv/releases/android/x86/kodi-21.3-Omega-x86.apk) |
| Plex | 10.28.0.3441 | x86_64 | [Upstream/download](https://downloads.plex.tv/Kepler/kepler-x86_64-googlePlay-10.28.0.3441-367a93b4.apk) |
| TV Bro | 2.1.6 | x86_64 | [Upstream/download](https://github.com/truefedex/tv-bro/releases/download/v2.1.6/tvbro-2.1.6-generic-geckoExcluded.apk) |
| BiglyBT | 1.3.3 | Java-only | [Upstream/download](https://github.com/BiglySoftware/BiglyBT-Android/releases/download/v1.3.3/BiglyBT-1.3.3.apk) |
| Crossy Road | 7.14.0 | arm64-v8a (translation) | [Upstream/download](https://play.google.com/store/apps/details?id=com.yodo1.crossyroad) |
| AIDA64 | 2.22 | x86_64 | [Upstream/download](https://play.google.com/store/apps/details?id=com.finalwire.aida64) |

The package has ten apps plus Google Play services across eighteen APK files, including language/density/native splits. `bundled-apps.sfs` also holds their extracted native libraries because Android scans these as immutable system applications. Selecting a universal APK does not force ARM translation: the preparation script chooses x86-64 or x86 where present. YouTube and Crossy Road use ARM64 translation.

The APK set has passed file, package, ABI and signing checks. On the development console, YouTube 7.27.302 plays ordinary menu-selected videos after sign-in, including a previously failing selection; logs show unencrypted VP9 at 1080p and 1440p. Guest playback previously selected an unavailable secure decoder. Sign-in is the verified working route on this build; this does not establish hardware DRM support or universal success for protected content. A fresh install of the combined package must reproduce these results.

Google Play services **26.11.32 (190800-885792908)** replaces the base ARM-only service in `/system/product/priv-app/GooglePlayServices`. Both x86 and x86-64 native library sets are included, preserving the signed APK. This version fixed the native provider/provisioning error when installed as an update on the test console. It is the general Android variant; first-run TV setup, Play Store installation and sign-in must be checked with it preinstalled. No account databases, tokens, provisioning state or trusted debugging keys are copied from the console.

App updates can change code, ABI selection or service behaviour. The repository retains the version/signature manifest for diagnosis. Account requirements and playback restrictions remain those of each service.

## Distribution and provenance

[bundled-apps.json](../releases/release-1.0/bundled-apps.json) contains package names, signer digests, APK sizes and hashes. [bundled-apps-image.json](../releases/release-1.0/bundled-apps-image.json) records the prepared filesystem. Neither contains account state.

Open-source app code and notices are linked in [Credits](CREDITS.md). Proprietary app redistribution permissions and applicable source-delivery obligations must be settled before publishing a bundle. Download provenance and a matching signature establish file identity, not permission to redistribute.
