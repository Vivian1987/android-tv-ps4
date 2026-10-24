# Downloading Android TV for PS4 1.0

GitHub limits release files to 2 GiB, so the 3.11 GB PKG is split into two parts. Download both from the [1.0 release](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.0) into the same folder, then join them using one of the methods below. Joining restores the original PKG exactly. You'll need about 6.3 GB free for the parts and the finished file.

## Windows

1. Download `Android-TV-for-PS4.pkg.part1`, `Android-TV-for-PS4.pkg.part2` and [Join-PKG-Windows.cmd](https://github.com/odiecay/android-tv-ps4/releases/download/v1.0/Join-PKG-Windows.cmd) into one folder.
2. Double-click **Join-PKG-Windows.cmd**.
3. Wait for **READY: Android-TV-for-PS4.pkg**.

The tool checks the SHA256 of the finished PKG. It works on Windows 10 and 11 with nothing extra to install and no admin rights. Your downloaded parts are kept, and an existing PKG is checked rather than overwritten. If a part is incomplete or the checksum is wrong, you'll get an error instead of a PKG. [Tool source](../tools/Join-PKG-Windows.cmd).

## Linux or macOS

Download both parts and [join-pkg.sh](https://github.com/odiecay/android-tv-ps4/releases/download/v1.0/join-pkg.sh) into one folder, open a terminal there, and run:

```sh
sh join-pkg.sh
```

Wait for **READY**. [Script source](../tools/join-pkg.sh).

## Joining manually

Windows (Command Prompt):

```bat
copy /b Android-TV-for-PS4.pkg.part1+Android-TV-for-PS4.pkg.part2 Android-TV-for-PS4.pkg
certutil -hashfile Android-TV-for-PS4.pkg SHA256
```

Windows (PowerShell):

```powershell
cmd /c "copy /b Android-TV-for-PS4.pkg.part1+Android-TV-for-PS4.pkg.part2 Android-TV-for-PS4.pkg"
Get-FileHash .\Android-TV-for-PS4.pkg -Algorithm SHA256
```

Linux or macOS:

```sh
cat Android-TV-for-PS4.pkg.part1 Android-TV-for-PS4.pkg.part2 > Android-TV-for-PS4.pkg
shasum -a 256 Android-TV-for-PS4.pkg
```

The result must be **3,108,306,944 bytes** with this SHA256:

```text
5564ccb30329123407ad03769732c0c4fc4e63084b1795d7fc7faf04dcf8ff25
```

If it doesn't match, don't install it. Check each part against `SHA256SUMS` on the release page, re-download the bad one and join again.

## Next steps

Install the joined **`Android-TV-for-PS4.pkg`**, not the `.part` files. The **Source code** ZIP/TAR on the release page is the repository, not the installer.

Copy the PKG to the top level of an exFAT USB drive and follow the [installation guide](INSTALL.md).
