# Hardware support

Every PS4 model has the same CPU, but the chips around it changed over the years. This page lists what is inside each model, what Android TV for PS4 does for that hardware, and what has actually been tested.

Only one console has been tested so far: a fat **CUH-1102A (Aeolia) on 13.52**. Everything else on this page is built from PS4 Linux community work and source code, and is waiting on real hardware reports. If you have one of these consoles, a [console report](https://github.com/odiecay/android-tv-ps4/issues/new?template=console-report.yml) is the most useful thing you can send, even if it fails.

**Key:** ✅ tested on a console · 🟢 supported in the build, not yet tested · 🟡 in progress or uncertain · ❌ not supported yet

## Which model do I have?

| Model numbers | Type | Southbridge |
| --- | --- | --- |
| CUH-10xx, CUH-11xx | Original ("fat") | Aeolia |
| CUH-12xx | Late fat | Belize |
| CUH-2xxx | Slim | Belize or Baikal, depending on the motherboard |
| CUH-7xxx | Pro | Belize or Baikal, depending on the motherboard |

Model-to-southbridge details vary by board revision and aren't fully documented, so treat this table as a guide. The southbridge is the chip that connects the drive, USB, Wi-Fi and Ethernet. The model number alone doesn't always tell you which one you have. The launcher writes it to `launcher-boot.log`, and Linux writes it to `boot-progress.log` (`Southbridge: ...`).

## Support by model

| | Fat, Aeolia | Fat CUH-12xx, Belize | Slim, Belize | Slim, Baikal | Pro, Belize | Pro, Baikal |
| --- | --- | --- | --- | --- | --- | --- |
| Starting Linux (all GoldHEN firmware) | ✅ | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| GPU and graphics fixes | ✅ Liverpool | 🟢 Liverpool | 🟢 Liverpool | 🟢 Liverpool | 🟢 Gladius | 🟢 Gladius |
| HDMI picture and sound | ✅ | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| Internal drive | ✅ | 🟢 | 🟢 | 🟡 Baikal port | 🟢 | 🟡 Baikal port |
| USB | ✅ | 🟢 | 🟢 | 🟡 Baikal port | 🟢 | 🟡 Baikal port |
| Wi-Fi and Bluetooth | ✅ Marvell 88W8797 | 🟢 Marvell 88W8897 | 🟢 88W8897 or MT7668 | 🟡 Baikal port | 🟢 88W8897 or MT7668 | 🟡 Baikal port |
| Ethernet | ✅ | 🟢 | 🟢 | 🟡 Baikal port | 🟢 | 🟡 Baikal port |
| Video playback fix (720p/4K freeze) | ✅ | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| Controller as remote, screensaver | ✅ | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |

## What is inside, and what we do with it

### GPU

| GPU | Consoles | PCI ID | Notes |
| --- | --- | --- | --- |
| Liverpool | Fat and Slim | `1002:9920`, `9922`, `9923` | Android's graphics driver gets the Liverpool raster configuration. Tested. |
| Gladius | Pro | `1002:9924` | Needs a second raster value because it has twice the shader engines. Applied at boot only when this GPU is present. Not yet tested. |

The GPU firmware is read from the console's own system software by the Linux loader, so nothing GPU-specific needs to be downloaded.

### Wi-Fi and Bluetooth

The Wi-Fi and Bluetooth chip sits on the southbridge's SDIO bus. The boot log's `Hardware:` line lists the SDIO IDs, which identify the chip.

| Chip | SDIO ID | Consoles | What Android TV for PS4 includes |
| --- | --- | --- | --- |
| Marvell 88W8797 | `02df:9129` | Fat CUH-10xx/11xx | Kernel driver, firmware and a Bluetooth fix. Tested. |
| Marvell 88W8897 | `02df:912d` (Wi-Fi), `02df:912e` (Bluetooth) | Fat CUH-12xx, many Slims | Kernel driver plus `mrvl/sd8897_uapsta.bin` from linux-firmware. Reported working on a Baikal Slim in another PS4 Linux project. |
| MediaTek MT7668 | `037a:7608` | Later Pros (CUH-7215/7216), some Slims | Wi-Fi driver loaded only when this chip is present, its firmware, and the MT7668 Bluetooth firmware. |

### Ethernet

Aeolia and Belize consoles use a Marvell Yukon-compatible controller (`sky2` driver). Baikal consoles use a different controller, which has its own experimental driver in the Baikal port.

### Internal drive

Android lives in files on the PS4's internal drive, in its user partition (number 27 on every model). Since 1.1 the drive is found by looking for the non-USB disk that has that partition, so a USB stick left plugged in no longer stops startup.

## The Baikal port

Baikal is the newest southbridge, in later Slims and Pros. It handles the drive, USB, Wi-Fi bus and Ethernet differently enough that it needs its own kernel changes: southbridge interrupt handling, the drive controller's registers and link start-up, the IOMMU, Bluetooth fixes and a new Ethernet driver.

That work exists in the PS4 Linux community. It is being brought into a **separate Baikal kernel**, which the launcher picks only on Baikal consoles, so fat, Belize and Pro-Belize consoles keep the tested kernel unchanged. Until a Baikal owner reports back, treat Baikal as experimental. If it can't find the internal drive it stops before writing anything, and holding the power button returns the console to normal.

## Firmware versions

Every firmware the Linux loader has kernel offsets for: 5.05, 6.72, 7.00–7.55, 8.00–8.52, 9.00–9.60, 10.00–10.71, 11.00, 11.02, 11.50–11.52, 12.00–12.52 and 13.00–13.52. Only 13.52 has been tested. See [Compatibility](COMPATIBILITY.md#firmware).

## Reporting your console

1. Install and open Android TV for PS4, even if you expect it to fail.
2. Note how far it got and any message on screen.
3. If you can, copy `launcher-boot.log` and `boot-progress.log` from `/user/app/ps4-android` over GoldHEN FTP. The `Southbridge:`, `GPU:` and `Hardware:` lines describe your console exactly.
4. Open a [console report](https://github.com/odiecay/android-tv-ps4/issues/new?template=console-report.yml), or post in [Discussions](https://github.com/odiecay/android-tv-ps4/discussions).

## Credits for hardware support

The model-specific work builds on the PS4 Linux community: the [ps4-linux-loader](https://github.com/ps4-linux/ps4-linux-loader) developers, the Liverpool and Gladius kernel work, [crashniels](https://github.com/crashniels/linux) for the 6.15 PS4 and Baikal kernels, [feeRnt's ps4-linux-12xx](https://github.com/feeRnt/ps4-linux-12xx) for the 88W8897 and MT7668 work, [noob404's MT7668 firmware collection](https://github.com/noob404yt/mt7668-wifi-bt-firmware), and [linux-psx](https://github.com/meerzulee/linux-psx) for the Baikal storage, SDIO and Ethernet research.
