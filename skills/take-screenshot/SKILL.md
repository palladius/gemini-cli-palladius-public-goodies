---
name: take-screenshot
description: Cross-platform screenshot utility for Linux Wayland and macOS. Use when the user asks to take a screenshot of a monitor, window, or specific area so the CLI can see and analyze it.
compatibility: Gemini CLI
metadata:
  version: 1.0.0
---
# Take Screenshot Skill

This skill provides a cross-platform Python script (`take_screenshot.py`) to capture screenshots natively on both Linux Wayland (via XDG Desktop Portal) and macOS (via `screencapture`). 

## When to use
Use this skill whenever you need to:
1. "Look" at the user's screen.
2. Verify visual output of a GUI application or web page.
3. Help the user debug visual layouts or errors.

## Usage

Run the bundled Python script, providing the desired output path.

```bash
python3 <PATH_TO_SKILL>/scripts/take_screenshot.py ./tmp-screenshots/latest.png
```

To run it without prompting the user on Linux (where supported by the desktop environment), use the `--non-interactive` flag:
```bash
python3 <PATH_TO_SKILL>/scripts/take_screenshot.py ./tmp-screenshots/latest.png --non-interactive
```

If the user specifically asks to capture a particular monitor on macOS, you can pass `--mac-display <N>` (where N=1, 2, etc.):
```bash
python3 <PATH_TO_SKILL>/scripts/take_screenshot.py ./tmp-screenshots/latest.png --mac-display 1
```

## Platform Details

- **Linux (Wayland):** Invokes the official XDG Desktop Portal via D-Bus (`org.freedesktop.portal.Screenshot`). **Note:** This will natively prompt the user with a dialog box asking them what to share (entire screen, specific monitor, or window). You must tell the user to expect this prompt before executing the script!
- **macOS:** Uses the built-in `screencapture` CLI utility. This is silent. It captures the main display by default, or specific monitors via the `--mac-display` argument.
- **Linux (X11 Fallback):** Attempts to use `import -window root` from ImageMagick if the portal is unavailable.

## Workflow Example
1. You determine a screenshot is needed to fulfill the user's request.
2. Tell the user: *"I'm going to trigger a screenshot. If you are on Linux, please look out for a permission dialog on your screen and select the monitor/window you want me to see."*
3. Execute the script: `python3 <PATH_TO_SKILL>/scripts/take_screenshot.py ./tmp-screenshots/capture.png`
4. Once the command completes successfully, use the read_file tool or analyze the resulting image at `./tmp-screenshots/capture.png` to answer the user's original query.
