# Component sources and credits

This port combines existing projects with PS4-specific installation, runtime and hardware work. Keep each component's upstream notices with copies and identify changes in derivative builds. There is currently no blanket licence covering every file or binary in this repository.

## Operating system and PS4 support

| Component | Source / attribution | Role |
| --- | --- | --- |
| BRTDTV / TD Android TV | [Project channel](https://www.youtube.com/@TDAndroidTVnoPC), [community](https://t.me/+t15cB5esYJUxZjdh) | Android TV x86 base distribution. |
| Android / AOSP | [Android source](https://source.android.com/) | Framework, init, system services and runtime. |
| Android-x86 | [Project](https://www.android-x86.org/) | Android on x86 PCs and relevant userspace adaptations. |
| Linux and PS4 Linux contributors | [Linux](https://www.kernel.org/), [sony-jaguar-devs/ps4-linux](https://github.com/sony-jaguar-devs/ps4-linux) | Console kernel and hardware support. Kernel commit, exact configuration and source delta are published under `kernel/`. |
| PS4 Linux loader | [Repository](https://github.com/ps4-linux/ps4-linux-loader), commit `f70f43a60a973b3662daeb29c1f115d95408db93` | Base loader; modified kexec source and its licence are retained under `loader-source/`. |
| GoldHEN | [Repository](https://github.com/GoldHEN/GoldHEN) | Homebrew environment and the local BinLoader receiver. |
| OpenOrbis | [Toolchain](https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain) | Native app SDK, runtime stubs and packaging tools. |
| LibOrbisPkg | [Repository](https://github.com/maxton/LibOrbisPkg) | PKG/SFO generation, extraction and validation through PkgTool.Core. |
| sleirsgoevy / libjbc | [Repository](https://github.com/sleirsgoevy/ps4-libjbc), commit `4dd18714fa7af7e15813d6a11537b60bb8c6f79c` | Privilege context helper source fetched for the build. |
| Scene-Collective PS4 Payload SDK | [Repository](https://github.com/Scene-Collective/ps4-payload-sdk), commit `b7326416c23ce14639e9180a24093bdc5eedb579` | Freestanding payload headers and helper source. Its README credits CTurt, IDC, xvortex and stooged. |
| Mesa | [Project](https://www.mesa3d.org/) | Userspace graphics driver. The current 64-bit fix adapts a pinned binary. |
| Ps3itaTeam | [PS4 driver patches](https://github.com/Ps3itaTeam/ps4linux-video-drivers/blob/master/mesa-git/mesa.patch) | Liverpool raster configuration reference. |

Binary hashes identify the particular build inputs; they do not replace corresponding-source and licence obligations. The repository does not claim a complete source rebuild of the BRTDTV base, kernel or all graphics binaries. The [build guide](BUILD.md) identifies which components are source-built here and which remain external inputs.

## Applications

- [VLC for Android](https://code.videolan.org/videolan/vlc-android) — VideoLAN.
- [Jellyfin for Android TV](https://github.com/jellyfin/jellyfin-androidtv) — Jellyfin contributors.
- [Kodi](https://github.com/xbmc/xbmc) — Kodi Foundation and contributors.
- [TV Bro](https://github.com/truefedex/tv-bro) — TV Bro contributors.
- [BiglyBT for Android](https://github.com/BiglySoftware/BiglyBT-Android) — Bigly Software and contributors.
- YouTube — Google; Spotify — Spotify; Plex — Plex; Crossy Road — its respective publisher/developer; AIDA64 — FinalWire.

Exact versions, original download links and signer hashes are in [Apps](APPS.md) and the bundled-app manifest. The repository does not relicense those applications.

## Artwork and fonts

The repository banner uses the selected Android TV and PS4 logo composition under `branding/`. The current installer artwork is under `releases/release-1.0/artwork/`.

The four installer previews introduce Android TV, controller input, internal-drive boot and returning to PS4. They use the original Android TV/PlayStation logos, Sony's DualShock 4 and PS4 product photographs, and setup/power-menu screenshots captured from Android on the console.

`official-asset-sources.json` and `additional-asset-sources.json` identify the original sources. The controller's white background is excluded by an SVG silhouette mask. The screenshots have no visible personal account data.

`build-slides.py` generates the 1280×720 preview PNGs. These are artwork, not captures of the complete native progress UI. `build-release.py` converts them to raw BGRA files and places them outside the launcher ELF so artwork does not inflate the executable retained during boot preparation.

The native text renderer uses the included Roboto font atlas and `Roboto-LICENSE.txt`. Android TV and PlayStation branding belongs to its respective owners. Provenance records are not a licence grant or an indication of affiliation.

This project is not affiliated with Google or Sony.
