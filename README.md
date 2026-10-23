# Android TV 13 for PS4

![Android TV for PS4](branding/repository-banner.svg)

Based on **BRTDTV's Android TV x86 builds**, adapted to run on PlayStation 4.

[Downloads](#downloads) · [Compatibility](#compatibility) · [Source code](#source-code) · [Credits](#credits)

## Downloads

The installer is still being tested. There is no download available yet;
installation instructions will accompany the release.

This version runs Android TV 13. Newer versions are planned after testing.

## Compatibility

Development and testing have been on a **PS4 CUH-1102A (Aeolia)**.
Other models have not been confirmed yet.

The installer is designed to keep Android and its data on the PS4's internal
drive without repartitioning it.

## Source code

The repository includes the [PS4 installer](installer/README.md),
[boot tools](ramboot/), [hardware probe](probe/) and [kernel and graphics patches](patches/).

For build requirements and setup, see the [build guide](docs/BUILD.md).
The scripts still rely on files and tools from the development setup, so
building from a fresh checkout needs additional preparation.

## Credits

Thanks to **BRTDTV** for their work bringing Android TV to x86 PCs. This PS4
port builds on that foundation.

- [BRTDTV Telegram group](https://t.me/+7cbIufx3Eh5hZmYx)
- [New Telegram group](https://t.me/+t15cB5esYJUxZjdh)
- [TD Android TV no PC — YouTube](https://www.youtube.com/@TDAndroidTVnoPC)

[Artwork sources and font licence](docs/ASSETS.md).
