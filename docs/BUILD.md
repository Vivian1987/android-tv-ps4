# Building v0.15

The current package builder is [`releases/v015/build-release.py`](../releases/v015/build-release.py).
It compiles the 32 GiB installer, creates the PS4 executable and package,
validates the package, and writes `release.json` and `SHA256SUMS` beside it.

## Dependencies

- Clang 18 and LLD 18.
- OpenOrbis PS4 Toolchain, including create-fself, create-gp4 and PkgTool.Core.
- The runtime libraries required by PkgTool.Core.
- A package template containing `sce_sys/` and `sce_module/`.
- Prepared `privileged.o`, `jailbreak.o` and `kernelrw.o` helper objects.
- Prepared release assets: `bzImage`, `initramfs.cpio.gz`, `system.sfs`,
  `libgallium-baseline.so`, `linux.elf`, `bootargs.txt`, `vram.txt` and
  `data-gib.txt` containing `32` followed by a newline.

The toolchain, template, helper objects and system assets are external inputs.
The public checkout does not yet reproduce all of them from source. The builder
records the helper and asset hashes in its output manifest.

## Package build

Replace these example paths with your prepared inputs:

```sh
python3 releases/v015/build-release.py \
  --sdk /path/to/OpenOrbis/PS4Toolchain \
  --template /path/to/package-template \
  --objects /path/to/helper-objects \
  --runtime /path/to/pkgtool-runtime-libraries \
  --assets /path/to/release-assets \
  --build /path/to/build-directory \
  --output /path/to/output-directory
```

Output: `Android-TV-PS4-13-v0.15-32GiB.pkg`, `validation.txt`, `release.json`
and `SHA256SUMS`. Package validation checks package structure and integrity;
it does not substitute for testing installation and playback on a console.

## Installer artwork

Generated artwork and font headers are included under `releases/v015/source/`.
To regenerate the preview slides, install Pillow and Inkscape, then run:

```sh
python3 releases/v015/artwork/build-slides.py
```

Rebuild the PKG after changing artwork. Regenerating a header does not modify
an already-built package.

## Earlier development tools

`installer/` retains earlier installer revisions. The root-level boot scripts
and `ramboot/` include tools from the network-backed prototype and may rely on
local manifests, paths and credentials. They are separate from the standalone
release installer. Upload and boot scripts act on hardware; do not run them as
build checks.
