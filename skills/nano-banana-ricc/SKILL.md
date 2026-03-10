---
name: nano-banana-ricc
description: (💛) Generate or edit images via Gemini 3 Pro Image (🍌 Nano Banana Pro) with Riccardo character consistency.
homepage: https://ai.google.dev/
version: 0.3
# 10mar26 v0.3 Added Riccardo character consistency via assets/riccardo/ images.
# 10mar26 v0.2 Added emojis and some suggestions.
# ??? v0.1 Initial copy I believe from openclaw skills
metadata:
  {
    "openclaw":
      {
        "emoji": "🍌",
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
        "primaryEnv": "GEMINI_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Nano Banana Riccardo (Gemini 3 Pro Image)

Use the bundled script to generate or edit images. This version is specialized for creating images featuring Riccardo with high character consistency.

## Character Consistency (Riccardo)

When the user asks for a picture of **Riccardo** (e.g., "Do a picture of Riccardo doing X"), you MUST use the following reference images as input to the script to ensure character consistency:

- `{baseDir}/assets/riccardo/ricc-pineapple-pizza.png`
- `{baseDir}/assets/riccardo/riccardosouthafrica.png`
- `{baseDir}/assets/riccardo/ricc-za-lake.png`
- `{baseDir}/assets/riccardo/ricc-za-view-with-kids.png`
- `{baseDir}/assets/riccardo/ricc-za-wine-tasting.png`

Pass these images as input (`-i`) to the script.

Example for Riccardo:

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "Riccardo surfing in Hawaii, wearing a red shirt" --filename "output.png" -i "{baseDir}/assets/riccardo/ricc-pineapple-pizza.png" -i "{baseDir}/assets/riccardo/riccardosouthafrica.png" -i "{baseDir}/assets/riccardo/ricc-za-lake.png" -i "{baseDir}/assets/riccardo/ricc-za-view-with-kids.png" -i "{baseDir}/assets/riccardo/ricc-za-wine-tasting.png"
```

## General Usage

### Generate

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png" --resolution 1K
```

### Edit (single image)

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "edit instructions" --filename "output.png" -i "/path/in.png" --resolution 2K
```

### Multi-image composition (up to 14 images)

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "combine these into one scene" --filename "output.png" -i img1.png -i img2.png -i img3.png
```

## Configuration

- `GEMINI_API_KEY` env var
- Or set `skills."nano-banana-ricc".apiKey` / `skills."nano-banana-ricc".env.GEMINI_API_KEY` in `~/.openclaw/openclaw.json`

## Notes

- Resolutions: `1K` (default), `2K`, `4K`.
- Use timestamps in filenames: `yyyy-mm-dd-hh-mm-ss-name.png`.
- The script prints a `MEDIA:` line for OpenClaw to auto-attach on supported chat providers.
- Do not read the image back; report the saved path only.
