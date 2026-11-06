---
name: marpione
description: >-
  (💛) Interactive Marp Inline Slide Deck Widget (<agent-embed>) and UI Sidecar
  (codename "marpione" / "marpi1") for Google Antigravity. Renders any Marp markdown
  deck (single-file or @import manifest) inline in chat with left/right slide cursors,
  color-coded chapter scrubber, speaker notes drawer, 1-click Copy PNG to clipboard,
  and Paste to Conversation via the Antigravity Sidecar bridge. Use when the user
  invokes /marpione or /marpi1, or asks to view, scrub, or paste Marp slides inline.
compatibility: Antigravity, Gemini CLI, Claude
metadata:
  version: "0.1.0"
  author: "Riccardo Carlesso"
  tags: "marpione, marpi1, marp, slides, presentation, antigravity_sidecar, generative_ui"
---

# 🎭 Marpione (`/marpione` & `/marpi1`) — Inline Marp Slide Viewer & Sidecar

**Marpione** (`marpi1`) turns any Marp presentation (single `.md` file or multi-file `@import "..."` manifest deck) into a rich, interactive **Generative UI inline widget (`<agent-embed>`)** and dockable **Antigravity Aux Pane Sidecar**.

---

## Bundled Files (`$SKILL_DIR/scripts/`)

All code is 100% self-contained inside `$SKILL_DIR/scripts/`:
- `$SKILL_DIR/scripts/marpione.py`: Zero-dependency Python 3 CLI & `<agent-embed>` HTML builder (resolves `@import` manifests, renders high-DPI PNGs via `@marp-team/marp-cli` with SHA-256 caching in `/tmp/marpione_cache/`, encodes inline WebP/PNG data URLs, and injects the live Sidecar bridge config).
- `$SKILL_DIR/scripts/main.mjs`: Node.js `sidecar_sdk` server providing both the Aux Pane UI (`/view.html`) and the local CORS bridge (`/api/bridge-config`, `/_sidecar/send-message`) so **💬 Paste to Conversation** works on every machine (`derek`, macOS, Linux).
- `$SKILL_DIR/scripts/sidecar.json`: Antigravity UI Sidecar manifest (`SIDECAR_UI_ENTRYPOINT_AUX_PANE`).
- `$SKILL_DIR/scripts/install_marpione.sh`: One-command installer for any workstation (`derek`, macOS, Linux) that hardlinks the sidecar into `~/.gemini/config/sidecars/marpione/`, symlinks `marpione` and `marpi1` into `~/.local/bin/`, and links the skills into `~/.gemini/config/skills/`.

---

## Execution Runbook (When `/marpione` or `/marpi1` is Invoked)

When the user asks to view a Marp presentation inline in chat (or invokes `/marpione` / `/marpi1`):

### Step 1: Register the HTML Artifact in the Conversation Brain Directory
Use `write_file` (or `write_to_file`) to create the placeholder artifact `<appDataDir>/brain/<conversation-id>/marpione-<slug>.html` with `ArtifactMetadata` (`UserFacing: true`, `RequestFeedback: false`).

### Step 2: Run `marpione.py` to Compile & Populate the Widget
Run `$SKILL_DIR/scripts/marpione.py` against the target `.md` deck (passing `--session-id <conversation-id>` and `-o <appDataDir>/brain/<conversation-id>/marpione-<slug>.html`):

```bash
UV_INDEX_URL="https://pypi.org/simple" uv run --with pillow python3 "$SKILL_DIR/scripts/marpione.py" \
  /path/to/slides.md \
  --session-id "<conversation-id>" \
  -o "<appDataDir>/brain/<conversation-id>/marpione-<slug>.html"
```
*(Note: If `uv` or `Pillow` is unavailable, plain `python3 "$SKILL_DIR/scripts/marpione.py" ...` works automatically using `cwebp` or PNG fallback.)*

### Step 3: Embed Inline in Chat (`<agent-embed>`)
Include the `<agent-embed>` tag (and optional Aux Pane sidecar pill) in your response:

```markdown
<agent-embed src="file:///<appDataDir>/brain/<conversation-id>/marpione-<slug>.html"></agent-embed>

[Marpione Slides 🎭](sidecar://marpione/view.html?file=/path/to/slides.md)
```

---

## Widget Controls & Capabilities
- **Left / Right Cursors (`◀` / `▶`)**: Floating overlay cursors on the slide stage + bottom bar (`⏮`, `◀ Prev`, `1 / N`, `Next ▶`, `⏭`) + keyboard shortcuts (`←` / `→`, `Space`, `J` / `K`, `Home` / `End`).
- **Chapter Scrubber & Slide Selector**: Color-coded interactive progress bar (`Part 1` Sky, `Part 2` Indigo, `Part 3` Amber, `Part 4` Emerald) and grouped `<select>` dropdown showing `#N · Title (filename.md)`.
- **Speaker Notes Drawer (`📝 Notes` / `N`)**: Inspects HTML comment speaker notes (`<!-- ... -->`) and displays the source `.md` file path.
- **`📋 Copy PNG`**: Renders the active slide at `1280×720` onto an offscreen `<canvas>` and writes a true `image/png` `Blob` to the system clipboard (`ClipboardItem`) so pressing `⌘V` / `Ctrl+V` in the chat box attaches the rendered slide PNG.
- **`💬 Paste to Conversation`**: Sends the rendered PNG artifact (`![Slide N](...)`), clickable `file://` link to the source `.md` slide, and any optional comment typed in the widget input directly into the active Antigravity conversation via the Sidecar bridge (`/_sidecar/send-message`).

---

## Installation on Any Machine (`derek`, macOS, Linux)

Run the bundled installer script:

```bash
bash "$SKILL_DIR/scripts/install_marpione.sh"
```
