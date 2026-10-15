# Changelog — niccolo-game-design

## [0.2.1] - 2026-10-12

- 👤🎯 Refined **Mode B (Face-Grafting & Adversarial Biometric Likeness Loop)** in [references/2d-to-3d-sdf-uv-baking.md](references/2d-to-3d-sdf-uv-baking.md):
  - Ground-truth photo-anchored template seeding (`build_photo_seeded_template`, avoiding alpha-blend ghosting).
  - Piecewise-linear 3D facial landmark calibration (`scale_y_upper` vs `scale_y_lower`).
  - Stripping 2D sideburns and mirroring clean temple skin (`prepare_clean_front_face`).
  - Dual-chart 2048×1024 atlas with zero-bleed barycentric hair recoloring (`recolor_strict_hair_texels_zero_bleed`).
  - Multimodal adversarial biometric critic loop (`adversarial_riccardo_likeness.py`) with 6-panel evaluation sheet.

## [0.2.0] - 2026-10-11

- 🗿🎨 Added [references/2d-to-3d-sdf-uv-baking.md](references/2d-to-3d-sdf-uv-baking.md): deterministic, zero-GPU recipes for:
  - **Mode A (Full 2D→3D SDF Visual-Hull + Relief Sculpting & Seamless `1024×1024` UV Baking)**: turns dual-orthographic (`0° Front + 90° Side`) or single-view 2D character sheets into watertight, UV-textured `.glb` models using `rembg` neural segmentation, 2px erosion + 36-iteration RGB halo removal, 3D Signed Distance Field carving with luminance/chroma relief embossing, Taubin surface fairing, and boundary-matched UV atlas baking.
  - **Mode B (2D Portrait Face-Grafting onto Existing 3D `.glb`)**: projects/blends the true front-facing 2D portrait face onto an existing `TRELLIS.2` / `Hunyuan3D` `.glb` mesh whose 3D body/crown/clothes are good but whose face texture was distorted.

## [0.1.0] - 2026-10-08

- ✨ Initial release. Distilled from Niccolò's code-review feedback ("use Managers; a MapManager decides
  Game Over; a DropManager whose drops improve with kills and reset on important finds") and Robert
  Nystrom's *Game Programming Patterns*.
- 7 rules, canonical manager set, lifecycle contract, Event Bus rules, strangler-fig refactor recipe,
  MR review checklist, anti-pattern table.
- References: pattern catalog, MapManager win/lose recipe, DropManager pity-timer recipe,
  `tsc --strict`-verified TypeScript skeletons with Monte-Carlo self-test, Godot 4 mapping.
