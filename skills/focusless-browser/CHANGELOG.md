# Changelog — `focusless-browser`

## [0.1.0] - 2026-11-17
### Added
- Initial release born from `/browser` long-form article authoring workflows requiring real authenticated Chrome without OS focus hijacking.
- Added `scripts/focusless_notify.py` for non-intrusive Level-1 start/done OS desktop notifications (`notify-send` on Linux, experimental `osascript` on macOS) featuring explicit HHGTTG *"Don't Panic / SEP field"* handoff semantics.
- Added `scripts/start-focusless-chrome.sh` for Level-2 (`Xephyr :99 -no-host-grab`) and Level-3 (`Xvfb :99`) isolated desktop Chrome sessions on Linux (`--remote-debugging-port=9222`, persistent non-default `--user-data-dir`, zero `--enable-automation`).
- Documented OS support matrix (`Linux ✅`, `macOS ❓`, Windows omitted).
