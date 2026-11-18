---
name: focusless-browser
description: >-
  (💛) Drive a real, authenticated Chrome browser from `/browser` or CDP workflows without stealing
  the human's OS window focus, keyboard input, or mouse — using CDP focus emulation with
  HHGTTG OS toast alerts (Level 1), visible nested `Xephyr` PiP X11 displays on Linux (Level 2),
  or `Xvfb` screencast isolation (Level 3).
compatibility: Gemini CLI, Antigravity, Jetski
metadata:
  version: 0.1.0
  author: palladius
  tags: browser, browser-use, cdp, focusless, xephyr, xvfb, linux, automation, devx
---

# 🖥️ Focusless Browser Use (`focusless-browser`)

Control a real, OAuth-authenticated desktop browser **without interrupting the user**: no raised Chrome windows under their fingers, no hijacked keystrokes, and no `--enable-automation` bot-detection flags.

---

## 🌍 OS Support Matrix

| Mode | 🐧 Linux (X11 / Wayland+XWayland) | 🍎 macOS |
| :--- | :--- | :--- |
| **Level 1**: Same-Chrome CDP (`Emulation.setFocusEmulationEnabled`) + OS Toast | ✅ Supported (`notify-send`) | ❓ Untested (`osascript` should work; unverified) |
| **Level 2**: Visible Picture-in-Picture (`Xephyr :99 -no-host-grab`) | ✅ Supported (requires `Xephyr`) | ❓ Untested / Unknown |
| **Level 3**: Headless Real Display (`Xvfb :99` + CDP `Page.startScreencast`) | ✅ Supported (requires `Xvfb`) | ❓ Untested / Unknown |

> **Scope Note**: Windows is intentionally omitted / unsupported. macOS support carries a **?** until verified on real Darwin hardware.

---

## 🎯 Choosing the Right Level

### Level 1 — Focusless Same-Chrome CDP + OS Toast *(Lowest Setup, Both Personal & Existing Profiles)*
Use when you **must** reuse cookies/profiles inside the user's running Chrome (`DevToolsActivePort`):

1. **NEVER call `Page.bringToFront`** — raising the OS window steals keyboard/mouse focus while the human types in another app.
2. **Emulate tab focus in Blink instead**:
   ```json
   { "method": "Emulation.setFocusEmulationEnabled", "params": { "enabled": true } }
   ```
   Open new tabs in the background (`Target.createTarget` with `background: true`).
3. **Wrap the session with OS Start / Done desktop toasts** via `$SKILL_DIR/scripts/focusless_notify.py` so the user knows clipboard/copy-paste might briefly touch the target tab and gets an explicit *"Don't Panic — SEP field off, over to you"* handoff when done:
   ```bash
   python3 "$SKILL_DIR/scripts/focusless_notify.py" start \
     --identity "me@example.com" \
     --task "Staging blog draft" \
     --url "https://example.com/editor"

   # ... perform focusless CDP automation ...

   python3 "$SKILL_DIR/scripts/focusless_notify.py" done \
     --identity "me@example.com" \
     --url "https://example.com/draft/123"
   ```

---

### Level 2 — Visible `Xephyr` Nested Display *(🐧 Linux Only — Zero Focus/Clipboard Interference!)*
Use when you want a **live, watchable** Chrome window (great for long `/browser` article drafting, form filling, or one-time Google OAuth login) that is **physically isolated** from your `:0` keyboard, window manager, and clipboard:

```bash
# Starts Xephyr (:99, -no-host-grab) + real Chrome (NO --enable-automation!) on CDP port 9222
bash "$SKILL_DIR/scripts/start-focusless-chrome.sh" --mode xephyr --display :99 --port 9222

# Stop cleanly when finished (preserves login cookies in ~/.config/chrome-focusless-agent)
bash "$SKILL_DIR/scripts/start-focusless-chrome.sh" --stop --display :99 --port 9222
```

**Why Level 2 wins on Linux**:
- **Zero OS focus stealing**: Even if an automation library calls `Page.bringToFront`, it only raises the window inside virtual display `:99`.
- **Zero clipboard collision**: `:99` has its own X11 `CLIPBOARD` selection, completely separate from `:0`.
- **Zero `--enable-automation`**: Uses a clean custom `--user-data-dir`, avoiding `navigator.webdriver = true` blocks and skipping Chrome 136+ `DevToolsActivePort` confirmation popups because Chrome explicitly trusts `--remote-debugging-port=9222` on non-default profile directories.

---

### Level 3 — Silent `Xvfb :99` Virtual Display *(🐧 Linux Only)*
Identical to Level 2 (full non-headless Chrome desktop build with GPU/fonts, not `--headless`), but runs inside invisible `Xvfb :99` instead of opening a Picture-in-Picture window:

```bash
bash "$SKILL_DIR/scripts/start-focusless-chrome.sh" --mode xvfb --display :99 --port 9222
```
Connect over `http://127.0.0.1:9222/json/version` (or WebSocket) and stream frames via CDP `Page.startScreencast` if a UI sidecar needs live previews.
