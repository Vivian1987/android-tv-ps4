# Download Android TV for PS4 1.0

Download both package parts from the [1.0 release](https://github.com/odiecay/android-tv-ps4/releases/tag/v1.0) into the same folder:

- `Android-TV-for-PS4.pkg.part1`
- `Android-TV-for-PS4.pkg.part2`

GitHub limits individual release assets to under 2 GiB. These are two pieces of one **3,108,306,944-byte PKG**, not separate packages. Join them before transferring the PKG to your PS4. Allow about 6.3 GB of free space on your computer for the parts and the reconstructed file together.

## Windows: double-click to join and verify

1. Download [Join-PKG-Windows.cmd](https://github.com/odiecay/android-tv-ps4/releases/download/v1.0/Join-PKG-Windows.cmd) into the same folder as both parts.
2. Double-click **Join-PKG-Windows.cmd**. No extra program or administrator access is needed on Windows 10/11.
3. Leave the window open while it joins the parts and checks the SHA256. Wait for **READY: Android-TV-for-PS4.pkg**.
4. Copy that completed PKG to the top level of an **exFAT USB drive**, connect it to the PS4, load GoldHEN and install it through the **Package Installer**.
5. Enable **GoldHEN → Servers → BinLoader** on port **9090**, then open **Android TV for PS4**.

The tool keeps your downloads. If a PKG already exists, it verifies it without overwriting it. An incomplete download or checksum failure produces an error instead of an install-ready file. The tool's [source](../tools/Join-PKG-Windows.cmd) is in this repository.

**Allow 5–10 minutes for the first installation and boot**, while Android installs and extracts its files and prepares its storage, apps and environment. Subsequent boots take about **2 minutes**.

## Linux or macOS: join and verify script

Download [join-pkg.sh](https://github.com/odiecay/android-tv-ps4/releases/download/v1.0/join-pkg.sh) beside both parts. Open a terminal in that folder and run:

```sh
sh join-pkg.sh
```

The script joins the parts, verifies the completed PKG and reports **READY**. Follow steps 4–5 above to install it. [Script source](../tools/join-pkg.sh).

## Manual alternative: Windows

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

## Manual alternative: Linux or macOS

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

The release targets **CUH-1102A / Aeolia / firmware 13.52** with GoldHEN and its BinLoader enabled. Read [Compatibility](COMPATIBILITY.md) for the recorded startup and streaming limitations. Fresh installation and Android boot have been confirmed on the stated test console.
