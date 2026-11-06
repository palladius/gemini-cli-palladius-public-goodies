# Changelog — `marpione` (`marpi1`)

## [0.1.0] - 2026-11-06
### Added
- Initial release of **Marpione** (`marpi1`) interactive Marp inline slide viewer (`<agent-embed>`) and Antigravity Aux Pane UI Sidecar (`~/.gemini/config/sidecars/marpione`).
- Added `$SKILL_DIR/scripts/marpione.py` with built-in `@import` manifest compiler, SHA-256 cached `@marp-team/marp-cli` PNG rendering, WebP/PNG data URL encoding, speaker notes extraction, **`📋 Copy PNG`** (`ClipboardItem`), and **`💬 Paste to Conversation`** via Sidecar bridge.
- Added `$SKILL_DIR/scripts/main.mjs`, `sidecar.json`, and `install_marpione.sh` for 1-command installation across macOS and Linux (`derek`).
