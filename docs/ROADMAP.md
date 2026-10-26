# Roadmap

Known work after 1.1, with what's already known about each item. Nothing here has a date. If you want to pick something up, say so in [Discussions](https://github.com/odiecay/android-tv-ps4/discussions) so work isn't doubled up.

## Starting reliably

**Linux's memory at startup: done in the 26 Oct update.** The loader used to need two unbroken blocks of physical memory, about 12 MB for the kernel and 10 MB for the startup files, and a busy or freshly installed console often had none that large (code 12). It now stages both in pieces of 2 MB down to 64 KB, outside the area Linux will occupy, and the handover stub copies them into place once Orbis has shut down (`loader-source/linux/ps4-kexec-common/kexec.c`, `linux_thunk.S`). Each launch logs the piece counts and whether the old single-block method would have worked. Still worth doing:

- Copy and check the big files without filling the file cache, so our own install leaves memory tidier.
- Confirm the fix on a Pro and a Slim from their `logs/launcher.log`.

**Automatic restart or not.** When memory is short, the launcher currently asks the user to restart. Whether it should restart the console by itself is an open question for users; answers are welcome in Discussions.

**First setup jumping back.** Google's setup app can still jump back to the start once on the first setup. Logs show its audit logging crashing when the signed-in account's ID isn't available (`AuditMetaData.createIdentifiersForCurrentUser`). This is inside Google's app, so the fix is likely in what the environment provides it rather than in the app.

## Video and graphics

**Hardware video decoding.** Drawing is GPU-accelerated through Mesa (OpenGL ES 3.2 with radeonsi, Vulkan 1.1 with RADV), but every video decoder Android has here is software (`c2.android.*`, `c2.ffmpeg.*`), so decoding runs on the CPU. The PS4's GPU has a dedicated decoder block (AMD UVD) that Linux and Mesa can drive on this GPU generation. Wiring it into the FFmpeg decoders through VA-API is the biggest playback upgrade available, especially for 4K.

**Newer Mesa.** The build uses Mesa 24.0.8. A newer release may bring performance and fixes, but it means rebuilding the graphics libraries and re-checking the Liverpool and Gladius raster fixes (`runtime-source/patch-mesa-raster.py`).

## Hardware

**Slim, Pro and Baikal reports.** Support is built in but untested. Real reports decide what gets fixed next; see [Hardware support](HARDWARE.md).

**Baikal USB.** The Baikal kernel builds on community work that reportedly booted but without working USB. Expect USB to be the first thing Baikal reports need.

**MT7668 Wi-Fi.** The driver and firmware are included for later Slims and Pros but have never run on real hardware.

## Beyond Android TV

**Native app ports.** The launcher already does the PS4-side work a native app needs (OpenOrbis build, video output, controller input). A native VLC for PS4 looks achievable; a VLC port exists for PS5. Requests for other apps are welcome.

**Other Android versions.** The Linux side is largely independent of the Android release, so newer Android TV builds are possible in principle.

## Housekeeping

- Rename `releases/release-1.0/`, which holds the 1.1 source.
- Develop on a branch and merge to `main` at release time, so the public README always matches the downloadable release.
