---
name: veo
description: Generate short videos from text or image prompts using Google's Veo model. Use when the user asks to create a video, generate a clip, or animate an image.
---

# Veo Video Generation

This skill uses a Python script to generate videos via the Google Veo API, leveraging pre-existing code from the user's `genai-googlecloud-scripts` repository.

## Workflow

1.  **Get Prompt:** The user provides a text prompt and optionally an input image.
2.  **Generate Video:** Call the main script to handle video generation.
3.  **Return Video:** The script will output a `MEDIA:` path that OpenClaw will automatically render in the chat.

## Usage

Execute the bundled Python script with the desired prompt. The script handles API authentication, initiates the generation, polls for completion, and saves the final video file.

**Basic text-to-video:**
```bash
python {baseDir}/scripts/generate_video.py "A capybara relaxing in a hot spring"
```

**Image-to-video:**
```bash
python {baseDir}/scripts/generate_video.py "Make this capybara swim" -i /path/to/capybara.jpg
```
