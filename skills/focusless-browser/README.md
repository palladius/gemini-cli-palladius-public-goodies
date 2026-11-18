# 🖥️ Focusless Browser Use (`focusless-browser`)

> **Why we built this skill**: This skill was born while learning how to **create and stage rich long-form articles directly from `/browser` workflows** inside an already-authenticated Chrome session — without the agent constantly raising Chrome windows under the author's fingers, hijacking live keystrokes in other apps, clobbering clipboard contents silently, or tripping anti-bot / OAuth gates with `--enable-automation`.

Instead of forcing a binary choice between *"broken headless automation"* and *"intrusive live window hijacking"*, `focusless-browser` provides a **3-level progressive isolation ladder**:

| Level | Mechanism | Window Visible? | Steals Focus / Keys? | Platform Support |
| :--- | :--- | :---: | :---: | :--- |
| **Level 1** | CDP `Emulation.setFocusEmulationEnabled` + HHGTTG `notify-send` Start/End alerts (strictly zero `Page.bringToFront`) | Background tab | ❌ Never raises window *(tiny clipboard care during native paste)* | 🐧 Linux ✅ · 🍎 macOS ❓ |
| **Level 2** | Nested `Xephyr :99 -no-host-grab` PiP window + clean Chrome (`--remote-debugging-port=9222`, no `--enable-automation`) | 👀 Yes (watch-only PiP) | ❌ Physically impossible (isolated X11 display & clipboard) | 🐧 Linux ✅ · 🍎 macOS ❓ |
| **Level 3** | `Xvfb :99` real Chrome + CDP `Page.startScreencast` | Optional sidecar | ❌ Physically impossible | 🐧 Linux ✅ · 🍎 macOS ❓ |

> Windows is outside scope for this toolkit. macOS (`❓`) has not been verified on hardware yet.

---

## ⚡ Quick Start

### 1. Wrap an Existing Browser Session with Level-1 Start/Done OS Notifications
```bash
python3 "$SKILL_DIR/scripts/focusless_notify.py" start \
  --identity "user@example.com" \
  --task "Draft article via /browser" \
  --url "https://example.com/editor"

# ... run your focusless CDP automation ...

python3 "$SKILL_DIR/scripts/focusless_notify.py" done \
  --identity "user@example.com" \
  --url "https://example.com/draft/42"
```

### 2. Launch a Watchable Focusless Chrome on Linux (`Xephyr`)
Requires `Xephyr` (`sudo apt install xserver-xephyr` on Debian/Ubuntu):
```bash
bash "$SKILL_DIR/scripts/start-focusless-chrome.sh" --mode xephyr --display :99 --port 9222
```
Log into your target websites once inside the PiP window; your session cookies persist in `~/.config/chrome-focusless-agent` while every future `/browser` or CDP run operates silently at `127.0.0.1:9222`.

### 3. Clean Shutdown
```bash
bash "$SKILL_DIR/scripts/start-focusless-chrome.sh" --stop --display :99 --port 9222
```
