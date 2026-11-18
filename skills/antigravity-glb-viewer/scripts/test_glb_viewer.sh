#!/usr/bin/env bash
# Standalone smoke test for the glb-viewer sidecar (no Antigravity needed).
# Usage: bash test_glb_viewer.sh [/abs/path/to/model.glb]
set -euo pipefail
SIDECAR_DIR="$HOME/.gemini/config/sidecars/glb-viewer"
SDK_DIR="$HOME/.gemini/antigravity/lib/node_modules/sidecar_sdk"
MODEL="${1:-$HOME/git/carchess3d/assets/models/king-riccardo.glb}"
PORT="${PORT:-47321}"
NODE_BIN="${NODE_BIN:-$(command -v node || ls "$HOME"/.nvm/versions/node/*/bin/node | tail -1)}"

cd "$SIDECAR_DIR"
ANTIGRAVITY_LS_ADDRESS=127.0.0.1:1 ANTIGRAVITY_CSRF_TOKEN=test ANTIGRAVITY_SIDECAR_WEB_PORT="$PORT" \
  "$NODE_BIN" --import "$SDK_DIR/register_loader.js" main.mjs > /tmp/glb-viewer-test.log 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 1.5

echo "== server log"; cat /tmp/glb-viewer-test.log
echo "== GET / (page)"
curl -s --noproxy "*" -o /dev/null -w "HTTP %{http_code} %{content_type} %{size_download}B\n" "http://127.0.0.1:$PORT/?path=$MODEL"
echo "== GET /api/info"
curl -s --noproxy "*" "http://127.0.0.1:$PORT/api/info?path=$MODEL"; echo
echo "== GET /raw (bytes)"
curl -s --noproxy "*" -o /tmp/glb-viewer-roundtrip.glb -w "HTTP %{http_code} %{content_type} %{size_download}B\n" "http://127.0.0.1:$PORT/raw?path=$MODEL"
cmp "$MODEL" /tmp/glb-viewer-roundtrip.glb && echo "bytes identical ✅"
head -c 4 /tmp/glb-viewer-roundtrip.glb; echo "  <- magic (expect glTF)"
echo "== vendor modules"
for f in /vendor/three/three.module.js /vendor/three/addons/loaders/GLTFLoader.js /vendor/three/addons/controls/OrbitControls.js /vendor/three/addons/utils/BufferGeometryUtils.js; do
  curl -s --noproxy "*" -o /dev/null -w "$f HTTP %{http_code} %{size_download}B\n" "http://127.0.0.1:$PORT$f"
done
echo "== negative: non-glb path should be rejected"
curl -s --noproxy "*" -o /dev/null -w "/raw?path=/etc/passwd -> HTTP %{http_code}\n" "http://127.0.0.1:$PORT/raw?path=/etc/passwd"
curl -s --noproxy "*" "http://127.0.0.1:$PORT/api/info?path=/etc/passwd"; echo
