# Android TV 13 for PS4

![Android TV for PS4](branding/banner-official-assets-v6.png)

Android TV 13 adapted for PlayStation 4, based on **BRTDTV's Android TV x86**.
PS4 adaptation and installer by Codey O'Connor.

## Status

In development. This repository contains source code and development tooling.
No downloadable release or end-user installation guide has been published yet.

| Component | Current target |
| --- | --- |
| Android | Android TV 13 |
| Development console | PS4 CUH-1102A (Aeolia) |
| Installer source | `installer/sparse-v014` |
| Storage design | Compressed system image and sparse ext4 userdata within the existing PS4 user partition; no repartitioning |

Other console models are not confirmed by the testing recorded here.

## Source layout

| Path | Contents |
| --- | --- |
| `installer/` | Native PS4 installer, interface and packaging scripts |
| `ramboot/` | Linux boot, Android startup and diagnostic tools |
| `patches/` | Kernel, graphics and quota patches |
| `probe/` | Console hardware probe |
| `branding/` | Icon and banner assets |

## Building

See [build dependencies and preparation](docs/BUILD.md).

The build scripts currently depend on development-machine paths, external
toolchains and prepared inputs. A clean clone is not yet a standalone build.
Android system images and compiled packages are not stored in Git.

## Credits

**BRTDTV** provides the Android TV x86 foundation used by this project.

- [BRTDTV](https://t.me/brtdtv)
- [Android TV x86 BR](https://t.me/Android_roms_x86)
- [TD Android TV no PC](https://www.youtube.com/@TDAndroidTVnoPC)
- [Community FAQ](https://brtdtvfaqs.page.gd/)

See [asset attribution](docs/ASSETS.md) for branding sources and included font
licence information.
