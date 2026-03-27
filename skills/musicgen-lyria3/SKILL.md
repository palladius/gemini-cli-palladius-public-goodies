---
name: musicgen-lyria3
description: Generate 30-second music clips with the Lyria 3 model from Google GenAI. Supports creating music with lyrics, vocals, and specific genres from text prompts. Now includes metadata/lyrics saving and custom output filenames.
---

# Musicgen Lyria3

## Overview

This skill enables the generation of high-quality 30-second music previews using Google's Lyria 3 model via the GenAI SDK. It can produce music in various genres, including tracks with vocals and specific lyrics provided in the text prompt.

## Core Capability

The skill utilizes a bundled Python script (`scripts/musicgen-lyria3.py`) that interacts with the `lyria-3-clip-preview` model.

### Workflow

1.  **Understand the Request**: Identify if the user wants music, a song, or an audio clip based on a description.
2.  **Formulate a Prompt**: Ensure the prompt includes genre, mood, instruments, and any specific lyrics or vocal styles requested.
3.  **Execute Generation**: Run the script using `uv run` or `python` (if dependencies are met).
4.  **Confirm Output**: 
    - The script saves the resulting audio as `clip.mp3` (default) or a custom filename.
    - **New**: Lyrics and metadata are automatically saved to a matching `.txt` file (e.g., `clip.txt`).

### Example Usage

```bash
# Basic generation
uv run scripts/musicgen-lyria3.py --prompt "A high-energy synth-pop song with female vocals"

# Custom output filename and specific lyrics
uv run scripts/musicgen-lyria3.py -o "neon-lights" -p "A synth-pop song with these lyrics: 'Electrified, we're living for the night, under neon lights so bright.'"
```

## Guidance for Prompts

To achieve the best results with Lyria 3, be as descriptive as possible:

- **Style & Genre**: "90s grunge", "lo-fi hip hop", "cinematic orchestral".
- **Tempo & Mood**: "120 BPM energetic", "slow and atmospheric".
- **Instruments**: "synthesizers", "distorted guitar", "pounding drums".
- **Vocals & Lyrics**: Explicitly state if vocals are needed and provide the lyrics in quotes.

## Resources

- `scripts/musicgen-lyria3.py`: The Python script (v0.0.4) that performs the generation using `google-genai`.
