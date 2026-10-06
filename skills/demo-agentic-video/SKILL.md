---
name: demo-agentic-video
description: Record automated video demos for browsers (shot-scraper) and terminals (Charm VHS .tape scripts) with frame verification and agent delivery.
compatibility: Antigravity, Gemini CLI, Claude, Hermes
metadata:
  version: 1.1.0
  author: Riccardo Carlesso & Ermete Bottazzi
  license: MIT
---

# Agentic Demo Video Recording 🎥🚛📼

Autonomous recording of deterministic video demos (MP4/GIF) for **Web Browsers** and **CLI Terminals**, featuring automated quality verification and chat delivery.

---

## 🧭 Decision Matrix

Choose the appropriate engine based on your target interface:

| Target | Tool | Config Format | Details |
|---|---|---|---|
| 🌐 **Web Apps & Browser** | Simon Willison's [`shot-scraper video`](https://github.com/simonw/shot-scraper) | YAML Storyboard (`storyboard.yml`) | See [references/browser_recording.md](references/browser_recording.md) |
| 💻 **Terminal & TUI** | Charm [`vhs`](https://github.com/charmbracelet/vhs) | Tape Script (`demo.tape`) | See [references/terminal_recording.md](references/terminal_recording.md) |

---

## ⚡ Quick Start

### 🌐 Track 1: Browser Demos (`shot-scraper`)
```bash
# Prerequisites
uv tool install shot-scraper && shot-scraper install

# Record from storyboard
shot-scraper video storyboard.yml --mp4
```
👉 *Full documentation and YAML syntax:* [references/browser_recording.md](references/browser_recording.md)  
👉 *Example storyboard:* [examples/browser_storyboard.yml](examples/browser_storyboard.yml)

### 💻 Track 2: Terminal Demos (`vhs`)
```bash
# Prerequisites (macOS)
brew install vhs ffmpeg

# Record from .tape file
vhs demo.tape
```
👉 *Full documentation, quoting rules, and sleep timings:* [references/terminal_recording.md](references/terminal_recording.md)  
👉 *Example tape file:* [examples/terminal_richard_console.tape](examples/terminal_richard_console.tape)

---

## 🔍 Quality Verification Loop (`ffmpeg`)

Before publishing or delivering a video, run an automated frame check:

```bash
# Extract 1 frame per second to a temporary directory
mkdir -p /tmp/demo_frames
ffmpeg -i demo.mp4 -vf "fps=1" /tmp/demo_frames/frame_%03d.png -y

# Check frame count (= duration in seconds)
ls /tmp/demo_frames/*.png | wc -l
```

### Verification Checklist:
1. **Initial Frames (001–005)**: Confirm clean launch without `LoadError`, missing API keys, or stacktraces.
2. **Key Moments**: Check that expected UI states, model streaming outputs, or simulated clicks rendered properly.
3. **Terminal Prompts**: Ensure commands didn't pile up due to insufficient `Sleep` time.
4. **Clean Exit**: Verify the application exited gracefully.

---

## 📱 Agent Delivery Protocol (The Ermete Protocol 🚛)

When AI agents (Hermes, OpenClaw, Antigravity) generate video demos in response to user requests:

1. **Always Target MP4**: WebM files often fail to render inline in mobile messaging clients.
2. **File Size Optimization**: Keep files under **2MB** to ensure single-packet, zero-timeout uploads.
3. **Immediate Inline Dispatch**: Deliver the asset directly to the conversation channel using `send_message`:
   ```python
   # Example Hermes/Telegram dispatch
   from hermes_tools import send_message
   send_message(action="send", target="telegram", message="MEDIA:/path/to/demo.mp4")
   ```
