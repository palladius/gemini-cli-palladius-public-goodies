#!/usr/bin/env bash
set -euo pipefail

# Installs the Antigravity GLB Viewer sidecar into ~/.gemini/config/sidecars/glb-viewer
# Resolve physical directory of this script (even when invoked through a symlink)
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${HOME}/.gemini/config/sidecars/glb-viewer"

if [[ ! -f "$SCRIPT_DIR/main.mjs" || ! -f "$SCRIPT_DIR/sidecar.json" || ! -d "$SCRIPT_DIR/vendor/three" ]]; then
  echo "❌ Error: main.mjs, sidecar.json or vendor/three not found in $SCRIPT_DIR" >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "⚠️ Warning: 'node' not found in PATH (the Antigravity sidecar runner provides its own, so this may be fine)." >&2
fi

# The sidecar scanner needs a real directory, not a symlink.
if [[ -L "$DEST_DIR" ]]; then
  rm -f "$DEST_DIR"
fi
mkdir -p "$DEST_DIR"

# Hard-link small files (keeps skill + sidecar in sync), copy the vendored three.js tree.
ln -f "$SCRIPT_DIR/sidecar.json" "$DEST_DIR/sidecar.json"
ln -f "$SCRIPT_DIR/main.mjs" "$DEST_DIR/main.mjs"
[[ -f "$SCRIPT_DIR/README.md" ]] && ln -f "$SCRIPT_DIR/README.md" "$DEST_DIR/README.md"
rm -rf "$DEST_DIR/vendor"
cp -r "$SCRIPT_DIR/vendor" "$DEST_DIR/vendor"

echo "✅ Installed Antigravity GLB Viewer sidecar to $DEST_DIR"
echo "   - $DEST_DIR/main.mjs"
echo "   - $DEST_DIR/sidecar.json"
echo "   - $DEST_DIR/vendor/three/ (three.js $(cat "$SCRIPT_DIR/vendor/three/VERSION.txt" 2>/dev/null | head -c 40))"
echo "👉 Restart Antigravity (or enable 'GLB Viewer 🧊' in the Sidecars/UI Plugins panel), then open:"
echo "   sidecar://glb-viewer/view.html?path=/abs/path/to/model.glb"
