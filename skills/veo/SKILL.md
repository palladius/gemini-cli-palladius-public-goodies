---
name: veo
description: Generate short videos from text or image prompts using Google's Veo model (via API Key or Vertex AI). Use when the user asks to create a video, generate a clip, or animate an image.
compatibility: Antigravity, Gemini CLI, Claude, OpenClaw
metadata:
  version: 0.2.0
  author: Riccardo Carlesso
  license: Apache-2.0
---

# Veo Video Generation 🎥🎬

Generate high-quality short videos from text prompts or input images using Google's **Veo** video generation model (`veo-3.1-fast-generate-001`).

---

## 🛠️ Authentication Modes

This skill supports two authentication options:

### 1. API Key Mode (Recommended)
Requires `GEMINI_API_KEY` set in the environment. Uses `$SKILL_DIR/scripts/generate_video_apikey.py`.

```bash
python "$SKILL_DIR/scripts/generate_video_apikey.py" "A cinematic drone shot of a misty pine forest at sunrise"
```

### 2. Vertex AI / GCP Mode
Requires `gcloud auth print-access-token` and Vertex AI API access on Google Cloud. Uses `$SKILL_DIR/scripts/generate_video.py`.

```bash
python "$SKILL_DIR/scripts/generate_video.py" "A cinematic drone shot of a misty pine forest at sunrise"
```

---

## 🚀 Workflows

### Text-to-Video
Provide a descriptive text prompt detailing the scene, camera movement, and lighting:

```bash
python "$SKILL_DIR/scripts/generate_video_apikey.py" "A capybara relaxing in a steaming hot spring, cherry blossoms falling, 4k cinematic"
```

### Image-to-Video (Image Animation)
Provide a starting image with `-i` along with instructions describing the desired motion:

```bash
python "$SKILL_DIR/scripts/generate_video_apikey.py" "Make the water ripple and steam rise gently" -i path/to/initial_frame.jpg
```

---

## ⚙️ Model Parameters & Defaults

Both scripts invoke the Veo predict endpoint with the following default configuration:

| Parameter | Default | Options / Description |
|---|---|---|
| **Model ID** | `veo-3.1-fast-generate-001` | Fast Veo video generation endpoint |
| **Location** | `us-central1` | Default Vertex AI publisher region |
| **Aspect Ratio** | `16:9` | Standard widescreen (`16:9` or `9:16` vertical) |
| **Duration** | `8s` | Video clip duration in seconds |
| **FPS** | `24` | 24 frames per second |
| **Audio** | `true` | Automatically generates synchronized ambient audio |
| **Polling** | 10s intervals (max 60 attempts) | Asynchronous Long-Running Operation (LRO) polling |
| **Output** | `veo_videos/` | Automatically decoded from base64 and saved as `.mp4` |

---

## 📱 Chat Delivery Protocol

Upon successful generation, the scripts output:
```text
Video saved to: veo_videos/YYYYMMDD-HHMMSS-prompt_slug.mp4
MEDIA:veo_videos/YYYYMMDD-HHMMSS-prompt_slug.mp4
```
The `MEDIA:<path>` line enables chat harnesses (OpenClaw, Telegram, Discord, Hermes) to automatically render and stream the video inline in chat messages.
