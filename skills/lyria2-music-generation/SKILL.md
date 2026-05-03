---
name: lyria2-music-generation
description: Generate music using Google's Lyria (v2) model via Vertex AI. Use when the user wants to create audio clips, background music, or experiment with AI music generation.
---

# Lyria Music Generation (v2)

This skill enables music generation using Google's Lyria model (currently v2) via the Vertex AI REST API. It includes a script to generate audio from text prompts and another to discover newer music-capable models.

## Workflow

1.  **Check for Models (Optional):** If the user asks for the latest models, use the `list_music_models.py` script.
2.  **Generate Music:** Call `generate_music.py` with the user's prompt and a target filename.
3.  **Return Audio:** The skill returns the path to the generated `.wav` file, which OpenClaw will render.

## Usage

### 🔍 List Music Models
Check for available music/audio models (e.g., to see if Lyria v3 has arrived).
```bash
python {baseDir}/scripts/list_music_models.py --project ric-cccwiki --location us-central1
```

### 🎵 Generate Music
Generate a music clip from a text prompt.
```bash
python {baseDir}/scripts/generate_music.py --prompt "A high-energy electronic dance track with a heavy bassline" --filename "output.wav" --project-id ric-cccwiki
```

## Note on Quality
This skill uses **Lyria v2**. If the output is not as expected, verify if a newer model (like Lyria v3) is available using the list script and update the `LYRIA_MODEL` environment variable or command arguments accordingly.
