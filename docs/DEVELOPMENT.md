# Developer notes

This port adapts BRTDTV's Android TV 13 for x86 PCs to the PS4. The PS4 app
installs the files and starts the Linux payload. Linux then mounts Android,
applies the PS4-specific changes and starts Android's init process.

These notes describe the v0.15 implementation. The [build guide](BUILD.md)
lists the tools and external inputs needed to produce the package. The boot
scripts discussed below are supplied inside the initramfs; their standalone
sources are not currently included in this public checkout.

## Keeping Android on the existing drive

Android lives in files on the PS4's existing internal filesystem. The native
installer copies the compressed system to `/user/app/ps4-android` and the boot
files to `/data/linux/boot`. Linux opens the existing encrypted storage and
mounts its UFS2 filesystem. It does not create an Android partition.

`system.sfs` contains the read-only `system.img`. Linux mounts both, then adds
a writable overlay in RAM. The boot script applies the PS4 graphics libraries,
Android configuration and controller changes through that overlay. The base
system stays intact; those changes are applied again on each boot.

Apps and settings need to survive a reboot, so they use a separate ext4 image,
`data.img`. Android's `/data` and `/metadata` directories are bound to directories
inside that image. This separates persistent user data from the system changes
applied at boot.

The first release starts at 32 GiB. `data-gib.txt` selects the capacity, and
first boot uses `truncate` and `mke2fs` to create a sparse ext4 image. Physical
drive space is used as data is written. The selected capacity still limits the
filesystem; sparse allocation does not make it unlimited.

For a larger build, the capacity file, `EDITION_GIB` compiler definition,
package name and manifest values need to agree. Changing those values does
not resize an existing installation. The installer checks the edition before
writing and rejects a mismatch. See [Storage](STORAGE.md) for the settings,
mount layout and disk-space calculation.

## Separating installation from boot

The [native installer](../releases/v015/source/install-prebuilt.c) opens its
bundled assets before obtaining privileged filesystem access. It copies the
system, graphics library and boot files, then records a completion marker.
Only after that does it send `linux.elf` to BinLoader at `127.0.0.1:9090`.
The payload is supplied by the installed app; no PC sends it during launch.

On subsequent launches, the marker selects the boot path. The app checks the
system file's size and prepares the boot files before sending the payload.
Linux checks its separate `data-ready` marker and mounts the existing data
image instead of creating another one.

These markers cover different stages: the native installer can finish before
Linux has created Android's storage. Treating them separately lets the boot
script detect an unfinished data-image creation without assuming that an
existing file is disposable.

## Recovering an interrupted install

A system copy is written to `system.sfs.part`. On retry, the
[copy routine](../releases/v015/source/image-copy.c) compares the entire existing
prefix with the package source before appending any bytes. If they differ, it
stops and leaves the file alone. A completed copy is synchronized and renamed
to its final name.

Boot files are staged individually. Existing versions can be retained as
`.before-sparse-v015` backups, and the launcher waits for all four boot files
to match before starting Linux. Conflicting backups stop the operation rather
than being silently overwritten.

Data-image creation is more conservative. If first boot finds `data.img` or
`data.img.part` without a completion marker, it stops for recovery. It does
not format that file again. Same-capacity v0.14 installations are accepted by
the v0.15 native installer; unknown installation markers are rejected.

When changing this code, keep the distinction between resuming a verified
system copy and recovering user data. The existing host tests cover copy
validation, edition checks and boot-file recovery. They are under
[`releases/v015/tests`](../releases/v015/tests/).

## Targeting PS4 hardware

This build targets Aeolia hardware. The supplied `autoboot.sh` requires
`aeolia` in the kernel log before opening the internal disk, and expects the
PS4 storage device at `/dev/sda27`. The tested console is CUH-1102A on firmware
13.52.

Adding another hardware revision means checking the kernel support and disk
layout first, then graphics and networking on that console. Update the check
only once those assumptions have been established, and rebuild the initramfs
that goes into the package. Removing the Aeolia check alone does not add
hardware support.

The Android adaptation also happens in the boot scripts. They install the
selected graphics and composer libraries into the RAM overlay and verify the
graphics-library hashes before launching Android. Network interfaces are
attached to Android's network namespace, where Android handles its own DHCP.
The controller adjustment changes `BUTTON_MODE` to `HOME` in the matching Sony
keylayout files so that Android receives a Home action.

These are useful places to start when extending the port: identify whether a
change belongs in the kernel, the boot environment or Android's configuration,
then include that change in the corresponding package input.

## Getting restart requests out of Android

Android init runs as PID 1 inside its own process namespace. Its restart
request ends that namespace; the host needs to handle the physical console.

The [Android supervisor](../releases/v015/power/android-supervisor.c) stays
outside Android's namespace and waits for init. It maps the namespace's restart
and power-off signals to host actions. An ordinary exit or crash does not
trigger a console power operation.

Before a power operation, it checks the PS4 boot markers, lets boot logging
finish, synchronizes storage and unmounts the Android and PS4 filesystems.
If an unmount fails, it refuses the power operation. Keep that shutdown order
in mind when adding mounts or background processes that hold files open.

The [power-control notes](../releases/v015/power/README.md) include the build
command and namespace tests. Those tests exercise the signal handling without
rebooting the development machine.

## A filesystem detail worth preserving

The PS4 installer uses a small
[`stat` compatibility header](../releases/v015/source/ps4-stat-abi.h).
The SDK's type layout can put `st_size` at the wrong offset for the PS4 ABI,
causing a size check to read the block count instead. The header sets the
expected type and checks the structure offsets at compile time.

It must be included before the SDK headers. If the toolchain changes, check
those assertions against the target ABI before removing the workaround.

## Building a change into the release

The [package builder](../releases/v015/build-release.py) compiles the native
installer and packages the supplied kernel, initramfs, Android system and other
assets. It records helper-object and asset hashes in `release.json`, validates
the package and writes `SHA256SUMS`.

Changing a boot script requires rebuilding the initramfs input. Changing
installer artwork requires regenerating its header and rebuilding the native
app. Neither changes an already-built PKG. Test the resulting package, not
just files copied into a running development installation.

Package validation, host tests and console testing answer different questions.
Keep the package hash with the test result so someone can tell which build was
actually used. The README records the release status; these notes explain the
implementation behind it.
