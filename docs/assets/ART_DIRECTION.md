# Art direction

Use this as the base prompt for every illustrated asset. Each asset's specific prompt is in `manifest.json`.

## Base prompt

> Original cartoon illustration for a mobile party game, "party night" mood. Thick soft dark outlines, chunky rounded shapes, gentle cel shading, warm wood textures and candy-bright accents set against a deep purple and indigo night palette. The cast are friendly, sleepy-eyed lazy bears with round bellies and expressive faces. Playful and warm, never corporate, never cyberpunk, never scary. Family-friendly. No text or lettering anywhere, except the game logo where explicitly requested. Portrait 9:19.5, keeping the stated UI safe areas calm and low-detail so buttons and signs stay readable on top.

## Palette

| Name | Hex | Use in art |
|---|---|---|
| Deep purple | `#2B1452` | Main night background |
| Indigo | `#3D1F7A` | Secondary background, walls |
| Deep navy | `#0F0A1F` | Deepest shadows, vignette |
| Violet | `#7C4DFF` | Magical glow, accents |
| Electric blue | `#4FC3F7` | Rim light, cool accents |
| Warm yellow | `#FFD54F` | Lamps, spotlights, sparkles |
| Coral | `#FF6B8A` | Party accents, confetti |
| Off-white | `#F7F4FF` | Highlights |
| Wood | `#A9713E`, `#6E4321` | Signs, furniture |
| Cream | `#FFF1D6` | Stitched labels, bear muzzles |

## Rules for every final

- Keep the exact file name, pixel size and format listed in the manifest, so swapping needs no code changes.
- Keep the safe areas listed for that asset calm. UI is drawn on top of them.
- Keep important subjects away from the top 5 % and bottom 3 %, which phones may cover with system UI.
- The characters and logo must be your own original designs. Do not reference existing games, brands, or copyrighted characters in prompts.
- `wood_sign.png` must keep its 9-slice geometry: corners stay within 40 px horizontally and 36 px vertically at 1x.
- `rope.png` must tile seamlessly from top to bottom.
- `app_icon.png` must be fully opaque. Keep adaptive foreground content inside the central 66 %.

## Swapping in a final

1. Replace the file at the same path, including the `2.0x/` and `3.0x/` versions where they exist.
2. Set that asset's `status` to `final` in `manifest.json`. `tool/generate_assets.py` will then leave it alone.
3. Run `python3 tool/build_asset_library.py` to refresh the asset library page.
