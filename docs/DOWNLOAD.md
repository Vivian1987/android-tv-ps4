# Download Android TV for PS4 1.0

Download both package parts from the [1.0 release](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.0) into the same folder:

- `Android-TV-for-PS4.pkg.part1`
- `Android-TV-for-PS4.pkg.part2`

GitHub limits individual release assets to under 2 GiB. These are two pieces of one **3,108,306,944-byte PKG**, not separate packages. Join them before transferring the PKG to your PS4. Allow about 6.3 GB of free space on your computer for the parts and the reconstructed file together.

## Windows

Open **Command Prompt** in the download folder and run:

```bat
copy /b Android-TV-for-PS4.pkg.part1+Android-TV-for-PS4.pkg.part2 Android-TV-for-PS4.pkg
certutil -hashfile Android-TV-for-PS4.pkg SHA256
```

If using PowerShell, run the first command through `cmd /c`:

```powershell
cmd /c "copy /b Android-TV-for-PS4.pkg.part1+Android-TV-for-PS4.pkg.part2 Android-TV-for-PS4.pkg"
Get-FileHash .\Android-TV-for-PS4.pkg -Algorithm SHA256
```

## Linux or macOS

Open a terminal in the download folder and run:

```sh
cat Android-TV-for-PS4.pkg.part1 Android-TV-for-PS4.pkg.part2 > Android-TV-for-PS4.pkg
shasum -a 256 Android-TV-for-PS4.pkg
```

On Linux, `sha256sum Android-TV-for-PS4.pkg` is an alternative checksum command.

## Check the result

The reconstructed PKG must have this SHA256:

```text
5564ccb30329123407ad03769732c0c4fc4e63084b1795d7fc7faf04dcf8ff25
```

If the hash differs, do not install it. Check both downloads against the individual hashes in the release's `SHA256SUMS`, redownload a damaged part and join them again. Joining the files does not change or rebuild the package.

Install **`Android-TV-for-PS4.pkg`** using the [installation guide](INSTALL.md). The `.part1` and `.part2` downloads cannot be installed directly. GitHub's automatically generated **Source code** archives contain the repository, not the installable PKG.

The release targets **CUH-1102A / Aeolia / firmware 13.52** with GoldHEN and its BinLoader enabled. Read [Compatibility](COMPATIBILITY.md) for the recorded startup and streaming limitations. The latest test of this exact PKG installed successfully but stopped before Linux boot; that result is documented alongside the download.
