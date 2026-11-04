---
name: antigravity-pdf-viewer
description: >-
  (💛) High-DPI interactive PDF Viewer UI Sidecar for Google Antigravity's right-hand
  Aux Pane (file_extensions: [".pdf"]). Replaces broken raw binary %PDF-1.x previews
  with crisp pdftoppm rendering, giant Prev/Next page buttons, Single-Page vs Continuous
  Scroll modes, extracted text inspection, 1-click Chat Context injection, and
  multi-profile "Open in Chrome for Printing" via xdg-open-as.
compatibility: Antigravity, Gemini CLI
metadata:
  version: 0.1.1
---
# Antigravity Inline PDF Viewer Sidecar (`antigravity-pdf-viewer`)

## Problem Solved
By default, clicking a `[file.pdf](file:///path/to/file.pdf)` link in Google Antigravity opens the raw `%PDF-1.4` binary stream as garbled text in the right-hand `fileView` pane whenever the internal `pdfViewer` flag is disabled.

However, Antigravity's `fileView` component checks `o4(".pdf")` for any running **UI Sidecar** declaring `"entrypoint": "SIDECAR_UI_ENTRYPOINT_AUX_PANE"` and `"file_extensions": [".pdf"]` in its `sidecar.json`!

This skill bundles a self-contained, zero-NPM-dependency Node.js `sidecar_sdk` PDF viewer directly inside `scripts/` (`scripts/main.mjs` + `scripts/sidecar.json`), powered by Poppler (`pdftoppm`, `pdfinfo`, `pdftotext`).

---

## Bundled Files (`$SKILL_DIR/scripts/`)
- `scripts/main.mjs`: Complete Node.js `sidecar_sdk` server + HTML/CSS/JS Aux Pane UI.
- `scripts/sidecar.json`: Antigravity UI Sidecar manifest registering `file_extensions: [".pdf"]`.
- `scripts/install_pdf_sidecar.sh`: Self-contained installer that links `scripts/main.mjs` and `scripts/sidecar.json` into `~/.gemini/config/sidecars/pdf-viewer/`.

---

## Features
- **Automatic `.pdf` Interception:** Clicking any `[*.pdf](file:///...)` link in chat or the file explorer automatically opens the rendered PDF in the right-hand Aux Pane.
- **2 Giant Prev/Next Page Buttons (`◀ Prev` / `▶ Next`):** Floating side navigation buttons + top bar page counter (`1 / 26`) + keyboard navigation (`ArrowLeft` / `ArrowRight`, `PageUp` / `PageDown`).
- **Single-Page (`📖 Singola`) vs. Continuous Scroll (`📜 Continuo`):** Toggle between single-page presentation mode and smooth scroll-spy mode.
- **🖨️ Apri in Chrome per Stampa (`xdg-open-as`):** Dynamically detects local Chrome profiles from `~/.config/google-chrome/Local State` (prioritizing the user's primary corporate/hosted-domain profile for printing permissions, or `$PDF_VIEWER_PRINT_IDENTITY`) and opens the PDF in the exact Chrome profile via `xdg-open-as <email> <path>`.
- **💬 Invia a Chat & 📝 Testo:** 1-click injection of the PDF path and extracted text into the active Antigravity chat via `window.antigravity.sendPrompt()`.

---

## Installation & Activation

### Prerequisites
Ensure `poppler-utils` is installed (`/usr/bin/pdftoppm`, `/usr/bin/pdfinfo`, `/usr/bin/pdftotext`):
```bash
# Debian / Ubuntu
sudo apt-get install -y poppler-utils
```

### Install the Sidecar into `~/.gemini/config/sidecars/pdf-viewer`
Because Antigravity's Go sidecar scanner uses `os.ReadDir` (which requires `~/.gemini/config/sidecars/pdf-viewer` to be a real directory rather than a directory symlink), run the bundled installer script from `$SKILL_DIR`:

```bash
bash "$SKILL_DIR/scripts/install_pdf_sidecar.sh"
```

### Environment Variables (Optional)
- `PDF_VIEWER_PRINT_IDENTITY`: Override the default email identity passed to `xdg-open-as` when clicking **🖨️ Apri in Chrome per Stampa**.
- `XDG_OPEN_AS_BIN`: Custom path to the `xdg-open-as` executable (auto-detected in `$GIC/bin/xdg-open-as`, `~/bin/xdg-open-as`, `~/.local/bin/xdg-open-as`, or `$PATH`).
