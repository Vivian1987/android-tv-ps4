# Assets

The selected branding is v6, recorded in `branding/selected.json`:

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
third-party licence notices remain applicable. No blanket project licence has
been selected in this initial repository setup.

No desktop screenshots, personal userdata, account records, keys or private
runtime archives are included. Gameplay/playback screenshots can be selected
for the release post when its notes are complete.
