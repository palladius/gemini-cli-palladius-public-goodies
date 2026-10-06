# 🌐 Browser Video Demos with `shot-scraper video`

Record browser-based video demos programmatically using Simon Willison's [`shot-scraper`](https://github.com/simonw/shot-scraper) tool (v1.10+) backed by Playwright and Chromium.

---

## 🛠️ Prerequisites

Install `shot-scraper` globally and fetch Playwright browser binaries using `uv`:

```bash
# 1. Install shot-scraper globally
uv tool install shot-scraper

# 2. Download Playwright's Chromium browser drivers
shot-scraper install
```

Verify that the `video` subcommand is available:
```bash
shot-scraper video --help
```

---

## 📜 Storyboard YAML Specification

`shot-scraper video` uses a YAML **Storyboard** file describing viewport dimensions, cursor highlighting, and step-by-step actions across scenes.

### Example: `storyboard.yml`

```yaml
output: demo.webm
url: https://studio--meditrack-29c9m.us-central1.hosted.app/

viewport:
  width: 1280
  height: 800

# Highlights the cursor with an animated dot and shockwave rings on click
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

---

## 🎬 Generating the Video

Run the recorder and convert automatically to MP4 via `ffmpeg`:

```bash
shot-scraper video storyboard.yml --mp4
```

This renders both `demo.webm` and `demo.mp4`.

---

## 💡 Best Practices

1. **Always use `--mp4`**: WebM files frequently fail to play inline on mobile clients (Telegram, Discord, iOS Safari).
2. **Deterministic Selectors**: Use stable CSS selectors (`input[name="..."]`, `button#submit`, `text=Save`) rather than dynamic auto-generated classes.
3. **Pacing**: Generous `pause` steps (1.5s–3s) give human viewers time to follow where the cursor moves and read the screen.
4. **Clean Session State**: If the site requires login, either pass cookies via `--auth` or script a login scene at the start of the storyboard.
