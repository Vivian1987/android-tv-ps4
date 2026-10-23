# Installer source

**Current installer: [v0.15](../releases/v015/source/).**

This directory retains the preceding installer iterations, through v0.14.

These are the older native PS4 installers and their package tools. See the
[README](../README.md#release) for current release and test status.

## v0.14 source

| File | Purpose |
| --- | --- |
| [`source/install-prebuilt.c`](sparse-v014/source/install-prebuilt.c) | Installation flow and file preparation |
| [`source/image-copy.c`](sparse-v014/source/image-copy.c) | Copying image data |
| [`source/installer-ui.c`](sparse-v014/source/installer-ui.c) | Native display, installation status and progress |
| [`build.py`](sparse-v014/build.py) | Compile and link the installer |
| [`package.py`](sparse-v014/package.py) | Assemble and validate the PS4 package |
| [`upload.py`](sparse-v014/upload.py) | Development deployment to the console |

See [build preparation](../docs/BUILD.md) for external dependencies and current
build inputs. Upload scripts act on a console; they are not build checks.

## Earlier iterations

`launcher/`, `prebuilt-*`, `raw-v007/` and `sparse-v008/` through `sparse-v013/`
contain earlier development versions. Start with [`releases/v015/source`](../releases/v015/source/) when
reading the current installer.
