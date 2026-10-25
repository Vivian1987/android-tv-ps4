# Downloading Android TV for PS4 1.1

The 1.1 PKG is a single 3.11 GB file hosted on the Internet Archive. GitHub doesn't accept files over 2 GiB, so the GitHub release page links here instead of attaching the PKG.

**[Android-TV-for-PS4-1.1.pkg](https://archive.org/download/android-tv-for-ps4-1.1/Android-TV-for-PS4-1.1.pkg)** · [Internet Archive page](https://archive.org/details/android-tv-for-ps4-1.1)

It must be **3,108,634,624 bytes** with this SHA256:

```text
bf1c57e836963efe12347c6a6ce720dd217056c9c731b6bc103293aed23acc9e
```

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

The Internet Archive page also offers a torrent, which can be faster and resumes cleanly if the connection drops.

## Next steps

Copy the PKG to the top level of an exFAT USB drive and follow the [installation guide](INSTALL.md). The **Source code** ZIP/TAR on the GitHub release page is the repository, not the installer.

## Version 1.0

1.0 was published as two `.pkg.part` files on the [1.0 release](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.0) with joining tools ([Windows](../tools/Join-PKG-Windows.cmd), [Linux/macOS](../tools/join-pkg.sh)). The joined 1.0 PKG is 3,108,306,944 bytes with SHA256 `5564ccb30329123407ad03769732c0c4fc4e63084b1795d7fc7faf04dcf8ff25`. 1.1 replaces it.
