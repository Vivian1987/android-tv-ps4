# Development build notes

These notes describe the existing build scripts. They are not installation
instructions, and the initial repository setup does not modify their behaviour.

## Current installer

`installer/sparse-v014/build.py` compiles the native installer with Clang 18
and links it with LLD 18 and the OpenOrbis PS4 toolchain. It expects:

- The OpenOrbis SDK at the development workspace's `toolchains/OpenOrbis/PS4Toolchain`.
- A prepared `/dev/shm/ps4-v014` build directory, including `image-metadata.h`
  and the referenced vendor include directory.
- Prepared `privileged.o`, `jailbreak.o` and `kernelrw.o` objects under
  `installer-pkg-build/32` in the local workspace.
- The source headers, including the artwork/font headers, in this checkout.

`installer/sparse-v014/package.py` then uses Pillow, Inkscape, create-gp4 and
PkgTool.Core. It expects prepared `sce_sys` and `sce_module` inputs from the
local recovery workspace and a populated build-directory `assets/` containing
the Android/Linux boot assets. It selects the v6 branding in `branding/`.

The scripts currently contain absolute paths. Their external inputs are not
all reconstructed by this repository. A clean clone cannot yet reproduce the
package without that preparation; packaging portability remains work to do.

## Prototype boot tools

`ramboot/build-standard.py` builds the earlier network-backed development
prototype from locally retained boot artifacts and verifies expected hashes.
`boot-orbis.py` reads a local boot manifest, stages files on the console and
sends a loader payload. These are operational development tools, not a generic
end-user installer. Local manifests and credentials are intentionally untracked.

## Repository checks

Python syntax can be checked without executing deployment scripts. Do not run
upload, remote, or boot scripts merely to test a checkout: they act on hardware.

Large Android images, packages, toolchains, private userdata and authentication
material are not included in Git. Downloadable release artifacts are separate
from the source repository.
