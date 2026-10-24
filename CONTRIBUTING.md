# Contributing

This project brings Android TV to PS4 hardware through a native launcher and a PS4 Linux runtime. Contributions that make the installation reliable, improve hardware support, explain the code or establish behaviour on another console are welcome.

Start with [Architecture](docs/DEVELOPMENT.md), then [Build](docs/BUILD.md). The active source is `releases/release-1.0`. Older installer experiments in Git history explain how the project developed; they are not the release build path.

## Where to work

| Area | Entry point | Useful work |
| --- | --- | --- |
| Installation and recovery | `source/install-prebuilt.c`, `image-copy.c` | Interrupted copies, storage checks, update/uninstall design. |
| Boot reliability | `source/boot-stage.c`, `boot-payload.c`, `loader-source/` | Receiver readiness, memory preparation, explicit handoff states. |
| Another firmware or PS4 revision | Loader offsets/checks, kernel, runtime disk/radio checks | Establish each hardware assumption and publish a model-specific test report. |
| Graphics and video | `patches/`, `runtime-source/patch-mesa-raster.py`, composer/gralloc inputs | Rebuildable driver adaptations, 32-bit raster testing, codec and frame-presentation diagnostics. |
| Wi-Fi and Bluetooth | `connectivity/`, `source/bluetooth*`, runtime interface handoff | Reconnection, pairing, hardware variants, Android network policy. |
| Controller input | `runtime/opt/androidtv-ps4/controller-home.sh` | Keylayout coverage, latency and remote mappings. |
| Power control | `power/android-supervisor.c` | Safe unmount order and physical restart/shutdown. |
| Apps | `bundled-apps.json`, `prepare-apps.py` | Native ABI selection, signed split layouts, reproducible playback tests. |
| User experience | `source/installer-ui.c`, `artwork/`, `docs/INSTALL.md` | Clear stage information, useful recovery instructions and measured first-run timings. |
| Build portability | `prepare-build.py`, `build-release.py` | Fresh-checkout builds, pinned inputs and source provenance. |

## Development loop

1. Reproduce one problem and record the package hash, console model and firmware.
2. Identify the failing layer: launcher, payload preparation, Linux, Android framework, graphics or app/service.
3. Make the smallest relevant source change and run its host tests.
4. Build a new PKG. Record its manifest and hash.
5. Test both a fresh installation and relaunch when the change affects those paths.
6. Include the observation and logs supporting the result in your pull request.

A live Android change can establish a diagnosis. It becomes part of the project only when the build produces it on a fresh installation. A payload's successful delivery is not proof of Linux boot, and a screenshot is not proof of sustained playback.

## Test reports

Useful reports include console model, southbridge if known, PS4 firmware, GoldHEN version, PKG SHA256, first-install/relaunch status and the last stage reached. For graphics, include a repeatable screen or clip and whether the artifact is present in Android screenshots or only on HDMI output. For playback, distinguish app rejection, decoding, rendering, audio and protected-output errors.

Remove account identifiers, Wi-Fi credentials, access tokens and private device identifiers before sharing captures. Do not attach a userdata image.

## Preserve these contracts

- Boot preparation and display release remain condition-based. A delay is not permission to hand off hardware.
- Boot works without a LAN connection. GoldHEN's local receiver is an explicit prerequisite.
- Existing userdata is preserved on failure or edition mismatch.
- Apps and credentials come from each user's own setup. Build inputs contain no personal Android state.
- Every mount introduced by a feature has a matching cleanup path.
- Hardware/service claims identify the tested scope. Device labels and compatibility fingerprints are not certification.

## Licensing and attribution

Retain upstream notices and identify the origin of copied code, patches and binary inputs. The repository currently has component-specific licences and no blanket project licence; do not relabel upstream material as newly licensed code. Link the relevant source/version when proposing an additional bundled app.

Open an issue or pull request on [GitHub](https://github.com/odiecay/android-tv-ps4) with a focused change and the evidence you have. Reports from additional PS4 revisions are useful even when the port does not boot: knowing exactly where a hardware assumption fails helps define the next port.
