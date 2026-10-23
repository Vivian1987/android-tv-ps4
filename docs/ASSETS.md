# Assets

The selected branding is v6, recorded in `branding/selected.json`:

- `repository-banner.svg`: compact README layout using the same v6 logo assets.

- `icon-official-assets-v6.png` and `.svg`: installer/package icon.
- `banner-official-assets-v6.png` and `.svg`: package and repository banner.
- `identity-official-assets-v6.png` and `.svg`: combined artwork layout.
- `refine-layout.py`: composition script using the included Android TV and PS4
  logo images. Its final convenience copy uses a local Pictures path.
- `official-asset-sources.json`: original logo URLs and recorded hashes.

The current installer source includes `installer-artwork.h` and
`installer-font.h`, because the native interface requires these generated data
headers. `Roboto-LICENSE.txt` is retained beside the font data.

Android TV and PlayStation branding belongs to its respective owners. The
source URL records identify provenance; they are not a licence grant. Existing
third-party licence notices remain applicable. The repository has no overall project licence.


## v0.15 previews

`releases/v015/artwork/` contains the installer slides and their generator.
The controller slide uses Sony's DualShock 4 product image; its original URL
and hash are recorded in that directory's `official-asset-sources.json`.
`android-first-run.png` shows the Android setup screen from development.
The rendered slides are artwork, not captures of the running progress UI.
