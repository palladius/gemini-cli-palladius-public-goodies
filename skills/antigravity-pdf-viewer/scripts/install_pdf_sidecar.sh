#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SRC_DIR="$REPO_ROOT/sidecars/pdf-viewer"
DEST_DIR="${HOME}/.gemini/config/sidecars/pdf-viewer"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "❌ Error: Sidecar source directory not found at $SRC_DIR" >&2
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

ln -f "$SRC_DIR/sidecar.json" "$DEST_DIR/sidecar.json"
ln -f "$SRC_DIR/main.mjs" "$DEST_DIR/main.mjs"

mkdir -p "${HOME}/.gemini/config/skills"
ln -sfn "$REPO_ROOT/skills/antigravity-pdf-viewer" "${HOME}/.gemini/config/skills/antigravity-pdf-viewer"

if [[ -f "${HOME}/.gemini/config/config.json" ]] && command -v python3 >/dev/null 2>&1; then
  python3 -c '
import json, uuid, pathlib
p = pathlib.Path("~/.gemini/config/config.json").expanduser()
data = json.loads(p.read_text())
sidecars = data.setdefault("sidecars", {})
entry = sidecars.get("pdf-viewer", {})
entry["enabled"] = True
entry.setdefault("projectId", str(uuid.uuid4()))
entry.setdefault("resolvedPermissions", None)
entry.setdefault("schemaVersion", 1)
sidecars["pdf-viewer"] = entry
p.write_text(json.dumps(data, indent=2) + "\n")
'
fi

echo "✅ Installed & enabled Antigravity PDF Viewer sidecar at $DEST_DIR"
echo "👉 Open the Sidecars panel in Antigravity (or restart the pdf-viewer sidecar) and click any .pdf file link!"
