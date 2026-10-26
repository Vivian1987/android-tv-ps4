# Downloading Android TV for PS4 1.1

The 1.1 PKG is a single 3.12 GB file on Google Drive. GitHub doesn't accept files over 2 GiB, so the [1.1 release page](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.1) links to it instead of attaching the PKG.

It must be **3,123,380,224 bytes** with this SHA256:

```text
1446d78046bd64fb0faa215b5b52b3431191ebaa7037270f5002c25c250048dd
```

Google Drive shows a "can't scan this file for viruses" page for large files. That's normal; choose **Download anyway**. If Drive says the download quota has been exceeded, too many people downloaded it today. Try again later.

## Checking the download

Windows (Command Prompt):

```bat
certutil -hashfile Android-TV-for-PS4-1.1.pkg SHA256
```

Windows (PowerShell):

```powershell
Get-FileHash .\Android-TV-for-PS4-1.1.pkg -Algorithm SHA256
```

Linux or macOS:

```sh
shasum -a 256 Android-TV-for-PS4-1.1.pkg
```

If it doesn't match, don't install it. Delete it and download it again.

## Next steps

Copy the PKG to the top level of an exFAT USB drive and follow the [installation guide](INSTALL.md). The **Source code** ZIP/TAR on the GitHub release page is the repository, not the installer.

## Version 1.0

1.0 was published as two `.pkg.part` files on the [1.0 release](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.0) with joining tools, which are attached to that release page. The joined 1.0 PKG is 3,108,306,944 bytes with SHA256 `5564ccb30329123407ad03769732c0c4fc4e63084b1795d7fc7faf04dcf8ff25`. 1.1 replaces it.
