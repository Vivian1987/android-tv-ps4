# Storage

Android uses files on the PS4's existing internal filesystem. Installation does not create, resize or format a disk partition. Linux opens the existing encrypted user storage and mounts UFS2; Android's writable data is an ext4 filesystem inside `data.img`.

## Layout

```text
/user/app/ps4-android/
  system.sfs                  compressed read-only Android system
  bundled-apps.sfs             signed APKs, splits and prepared native libraries
  libgallium-baseline.so       selected 64-bit PS4 graphics adaptation
  ndk-translation.tar.gz       native-bridge support
  data-gib.txt                selected userdata capacity: 32
  data.img                    sparse ext4 userdata image, created on first boot
  ready                       native installation completion marker
  data-ready                  userdata creation completion marker
  device-id                   random identifier generated on this installation
  *.log                       console-local diagnostics
  boot/
    bzImage
    initramfs.cpio.xz
    bootargs.txt
    vram.txt
```

`system.sfs` contains `system.img`, mounted read-only as ext4. An OverlayFS RAM layer holds the PS4 adaptations. The data image contains directories bound to Android's `/data` and `/metadata`; accounts, app data, downloads and pairings persist there.

The installed launcher retains its original assets. Copies under `/user/app/ps4-android` therefore add to the installed application's space. A downloaded PKG kept in internal storage is another copy.

## Capacity versus allocated space

The first-boot script uses `truncate -s` and `mke2fs` to create a **32 GiB logical image** without writing 32 GiB of empty blocks. It formats with lazy inode/journal initialization, checks the new filesystem, then commits it with a completion marker. This is why the PKG can be approximately 3.11 GB rather than a 32 GiB download.

The file grows in physical allocation as Android writes data. It still has a fixed 32 GiB filesystem capacity, and the PS4's physical free space is shared with games and other files. Android's apparent free space inside its image does not reserve that space on the PS4 drive.

## Storage accounting for release 1.1

These figures describe the package SHA256 `bf1c57e836963efe12347c6a6ce720dd217056c9c731b6bc103293aed23acc9e`.

| Item | Bytes | GiB |
| --- | ---: | ---: |
| Userdata, fully allocated | 34,359,738,368 | 32.000 |
| Copied system, apps, graphics and boot files | 3,087,239,057 | 2.875 |
| Installed PKG size used as an estimate | 3,108,634,624 | 2.895 |
| Combined estimate with full userdata | 40,555,612,049 | 37.770 |
| Also retaining the download and a 2 GiB margin | 45,811,730,321 | 42.665 |

Allow approximately **43 GiB** for that full-use scenario. Initial allocation is lower. Filesystem overhead, logs, updates, interrupted copies and development backups consume additional space. The installed PKG estimate is not a measured PS4 allocation figure.

One GiB is 1,073,741,824 bytes; one decimal GB is 1,000,000,000 bytes.

## Free-space and recovery checks

The native installer checks the system/app copy requirement plus a 2 GiB margin, adjusting for existing files. The app-filesystem step also checks its remaining copy requirement. Linux checks for more than 2 GiB physically free before creating/mounting data. These checks are not a continuously enforced reserve during use.

A partial compressed-system or app copy is compared with its source before resuming. Existing userdata without its commit marker is preserved for recovery rather than formatted again. Edition mismatches are rejected.

The installer retains historical layout markers for compatibility with earlier tests. A public version number is not inferred from those strings. Likewise, deleting the launcher icon is not an explicit userdata reset operation.

## Larger editions

The runtime recognizes capacity values of 32, 64 and 128 GiB. The current builder, manifest and compiler definition select **32 GiB**. A different edition requires those inputs to agree and its own installation test.

Changing a number does not resize an existing ext4 filesystem. This release does not include a user-facing resize tool or one-click uninstaller. Never substitute whole-drive formatting for image-file management.
