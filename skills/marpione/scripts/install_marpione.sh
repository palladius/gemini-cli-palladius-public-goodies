#!/usr/bin/env bash
set -euo pipefail

# Resolve physical directory of this script (even when invoked through a symlink)
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -P "$SCRIPT_DIR/.." && pwd)"
SIDECAR_DEST="${HOME}/.gemini/config/sidecars/marpione"
BIN_DEST="${HOME}/.local/bin"
SKILLS_DEST="${HOME}/.gemini/config/skills"

if [[ ! -f "$SCRIPT_DIR/main.mjs" || ! -f "$SCRIPT_DIR/sidecar.json" || ! -f "$SCRIPT_DIR/marpione.py" ]]; then
  echo "❌ Error: main.mjs, sidecar.json, or marpione.py not found in $SCRIPT_DIR" >&2
  exit 1
fi

chmod +x "$SCRIPT_DIR/marpione.py"

# 1. Install Antigravity UI Sidecar into ~/.gemini/config/sidecars/marpione
# Note: Antigravity's Go sidecar scanner uses os.ReadDir, which skips directory symlinks.
# Always create a real directory and hardlink files inside it.
if [[ -L "$SIDECAR_DEST" ]]; then
  rm -f "$SIDECAR_DEST"
fi
mkdir -p "$SIDECAR_DEST"

ln -f "$SCRIPT_DIR/sidecar.json" "$SIDECAR_DEST/sidecar.json"
ln -f "$SCRIPT_DIR/main.mjs" "$SIDECAR_DEST/main.mjs"
ln -f "$SCRIPT_DIR/marpione.py" "$SIDECAR_DEST/marpione.py"

# 2. Install CLI commands `marpione` and `marpi1` into ~/.local/bin
mkdir -p "$BIN_DEST"
ln -sfn "$SCRIPT_DIR/marpione.py" "$BIN_DEST/marpione"
ln -sfn "$SCRIPT_DIR/marpione.py" "$BIN_DEST/marpi1"

# 3. Link skills into ~/.gemini/config/skills/ for immediate slash-command discovery
mkdir -p "$SKILLS_DEST"
ln -sfn "$SKILL_DIR" "$SKILLS_DEST/marpione"
if [[ -d "$SKILL_DIR/../marpi1" ]]; then
  ln -sfn "$(cd -P "$SKILL_DIR/../marpi1" && pwd)" "$SKILLS_DEST/marpi1"
fi

echo "✅ Installed Marpione (marpi1) everywhere on $(hostname -s)!"
echo "   🎭 Sidecar:  $SIDECAR_DEST/{main.mjs,sidecar.json,marpione.py}"
echo "   💻 CLI:      $BIN_DEST/marpione & $BIN_DEST/marpi1"
echo "   🧠 Skills:   $SKILLS_DEST/marpione & $SKILLS_DEST/marpi1"
echo ""
echo "👉 Usage in Antigravity chat: type /marpione or /marpi1 <path/to/slides.md>"
echo "👉 Usage in terminal:         marpione <path/to/slides.md>"
