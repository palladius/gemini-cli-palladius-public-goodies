---
name: demo-agentic-video
description: Record browser-based video demos from YAML storyboards using shot-scraper.
compatibility: Antigravity / Gemini CLI
metadata:
  version: 1.0.0
---

# Demo Agentic Video (`shot-scraper video`) 🎥🚛

This skill explains how to record browser-based video demos programmatically using Simon Willison's `shot-scraper` tool (v1.10+).

## 1. Come Installarlo

`shot-scraper` relies on Playwright to run and record a headless browser. On macOS, the cleanest way to install it globally without cluttering python environments is using `uv` (Riccardo's preferred tool manager):

```bash
# 1. Install the tool globally
uv tool install shot-scraper

# 2. Download Playwright's Chromium browser drivers
shot-scraper install
```

Verify that `shot-scraper` is installed and has the `video` subcommand:
```bash
shot-scraper video --help
```

---

## 2. Che Cosa Puoi Fare Con Esso

You can record WebM videos (and convert them to MP4 via `ffmpeg`) by defining a YAML **Storyboard** file. The storyboard acts as a script, detailing exactly what pages to open, where to click, and what to type.

### Esempio di Storyboard (`storyboard.yml`)

```yaml
output: demo.webm
url: https://studio--meditrack-29c9m.us-central1.hosted.app/

viewport:
  width: 1280
  height: 800

# Highlights the cursor with an orange dot and shows rings on click!
cursor:
  visible: true
  clicks: true
  color: "#ff4f00"
  size: 18
  click_size: 44

scenes:
- name: Open Dashboard
  do:
  - pause: 2

- name: Enter Today's Weight
  do:
  - fill:
      into: "input[name='weight']"
      text: "97.2"
  - pause: 1.5

- name: Write Daily Notes
  do:
  - fill:
      into: "textarea[name='notes']"
      text: "Ermete oggi peso 97.2! Ciao da Ermete 🚛"
  - pause: 1.5

- name: Save the Log
  do:
  - click: "text=Save Today's Log"
  - pause: 4
```

### Generare il Video

Run the video recorder and automatically convert it to an `.mp4` using `ffmpeg`:
```bash
shot-scraper video storyboard.yml --mp4
```

---

## 3. Tips per Agenti (Hermes, Openclaw, etc.)

If you are an AI agent responding to Riccardo in a Telegram or Discord chat, here are critical tips to deliver video demos flawlessly:

### A. Automatic Compression & Zero-Timeout Delivery
High-resolution videos or PNGs can be quite heavy and trigger timeouts on the Telegram/Discord gateways.
- **WebM vs MP4:** Always use `--mp4` to generate an MP4 file. WebM files may not play inline on mobile Telegram clients.
- **JPEG Compression for Screenshots:** If taking screenshots at the end of a video run, convert heavy PNGs (>1.5MB) to JPEG using `sips` inside a Python subprocess (to avoid shell hangs):
  ```python
  import subprocess
  subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", "in.png", "--out", "out.jpg"])
  ```
- **File size targeting:** For extremely unstable network environments, compress or scale your video using ffmpeg so the file size is under **2MB**, ensuring it uploads in a single packet.

### B. Immediate Media Delivery (The Ermete Protocol)
Whenever you successfully generate an MP4 or a screenshot image, do not wait for the user to ask for it. Immediately deliver it to the active channel using the `send_message` tool with the `MEDIA:` prefix:

```python
# python code example to dispatch to Telegram
from hermes_tools import send_message
send_message(action="send", target="telegram", message="MEDIA:/path/to/demo.mp4")
```
This delivers the video as an inline playable clip on the user's phone, giving an instant, satisfying "Wow" factor.
