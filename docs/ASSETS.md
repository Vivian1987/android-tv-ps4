# Artwork and fonts

The repository banner uses the selected Android TV and PS4 logo composition under `branding/`. The current installer artwork is under `releases/release-1.0/artwork/`.

The four installer previews introduce Android TV, controller input, internal-drive boot and returning to PS4. They use the original Android TV/PlayStation logos, Sony's DualShock 4 and PS4 product photographs, and setup/power-menu screenshots captured from Android on the console.

`official-asset-sources.json` and `additional-asset-sources.json` identify the original sources. The controller's white background is excluded by an SVG silhouette mask. The screenshots have no visible personal account data.

`build-slides.py` generates the 1280×720 preview PNGs. These are artwork, not captures of the complete native progress UI. `build-release.py` converts them to raw BGRA files and places them outside the launcher ELF so artwork does not inflate the executable retained during boot preparation.

The native text renderer uses the included Roboto font atlas and `Roboto-LICENSE.txt`. Android TV and PlayStation branding belongs to its respective owners. Provenance records are not a licence grant or an indication of affiliation.
