# Artwork

The Derbent decision banner is an original AI-generated historical landscape, created with the built-in image generation tool. It is an illustrative reconstruction, not a surveyed reconstruction of medieval Derbent.

- Source: `source/CAUC_derbent_generated.png`
- Preview: `previews/CAUC_derbent_banner.png`
- Game texture: `../gfx/interface/illustrations/decisions/CAUC_derbent_pass.dds`
- Texture: 1100 × 440 pixels, opaque BC1/DXT1, 11 mip levels.
- Used by the repair and review decisions for Derbent.

The other decisions and all events currently reference installed vanilla artwork. They do not bundle or redistribute those textures. Character portraits use the installed game and EPE.

## Further art production

| Group | Decision banner | Event scene |
| --- | --- | --- |
| Derbent | Completed initial generated banner | Separate 1592 × 848 scene with space for character portraits |
| Lori | Stone monastic buildings and a manuscript workroom | Quiet workroom with unobstructed foreground |
| Svaneti | Stone tower dwellings in a mountain valley | Tower village, room for foreground portraits |
| Kutaisi/Gelati | Georgian monastic learning, available after 1106 | Can share a scholarly interior at first |

Aim for restrained historical painting, subdued earth colors and a readable composition at small size. Use no embedded text so the images work across languages. Decision pictures are referenced directly in `picture.reference`. Event scenes need a registered event background and theme; changing a decision picture does not change event art.

The source and exact generation prompt are retained for revision. Texture dimensions, file integrity and script references can be checked without starting CK3. Final in-game cropping and lighting remain unverified.
