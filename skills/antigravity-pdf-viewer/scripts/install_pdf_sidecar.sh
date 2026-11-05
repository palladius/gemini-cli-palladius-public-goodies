#!/usr/bin/env bash
set -euo pipefail

# Resolve physical directory of this script (even when invoked through a symlink)
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${HOME}/.gemini/config/sidecars/pdf-viewer"

if [[ ! -f "$SCRIPT_DIR/main.mjs" || ! -f "$SCRIPT_DIR/sidecar.json" ]]; then
  echo "❌ Error: main.mjs or sidecar.json not found in $SCRIPT_DIR" >&2
  exit 1
fi

for bin in pdftoppm pdfinfo pdftotext; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "⚠️ Warning: '$bin' not found in PATH. Install poppler-utils (e.g. sudo apt install poppler-utils)." >&2
  fi
done

if [[ -L "$DEST_DIR" ]]; then
  rm -f "$DEST_DIR"
fi
mkdir -p "$DEST_DIR"

ln -f "$SCRIPT_DIR/sidecar.json" "$DEST_DIR/sidecar.json"
ln -f "$SCRIPT_DIR/main.mjs" "$DEST_DIR/main.mjs"
if [[ -f "$SCRIPT_DIR/xdg-open-as" ]]; then
  chmod +x "$SCRIPT_DIR/xdg-open-as"
  ln -f "$SCRIPT_DIR/xdg-open-as" "$DEST_DIR/xdg-open-as"
fi

echo "✅ Installed Antigravity PDF Viewer sidecar to $DEST_DIR"
echo "   - $DEST_DIR/main.mjs"
echo "   - $DEST_DIR/sidecar.json"
echo "   - $DEST_DIR/xdg-open-as"
echo "👉 Open the Sidecars panel in Antigravity (or restart the pdf-viewer sidecar) and click any .pdf file link!"
