# Roadmap

Known work after 1.1, with what's already known about each item. Nothing here has a date. If you want to pick something up, say so in [Discussions](https://github.com/odiecay/android-tv-ps4/discussions) so work isn't doubled up.

## Starting reliably

**Reserve Linux's memory before the heavy copying.** The loader needs two unbroken blocks of physical memory, about 12 MB for the kernel and 10 MB for the startup files. It looks for them only between 138 MB and 2 GB, where the PS4 also keeps its file cache. Installing a 3 GB PKG, the launcher's first install and the one-time file check after an update all scatter that cache, so the first launch afterwards often stops with code 12. Logs from a fat PS4 show the kernel block sometimes only succeeding on its third and last try, even straight after a restart. Ideas, roughly in order of payoff:

- Allocate the kernel's staging copy from memory above 4 GB, which the file cache doesn't crowd. An earlier attempt hung because it asked to wait for memory (`M_WAITOK`); asking without waiting and falling back to the current range avoids that. The staging copy is moved into place at handover, so it doesn't need to be low (see `loader-source/linux/ps4-kexec-common/contiguous-allocation.h` and `kexec.c`).
- Copy and check the big files without filling the file cache, so our own install doesn't fragment memory.
- Retry automatically after a short wait before showing the restart screen.
- Prepare Linux before the install copy rather than after it.

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
