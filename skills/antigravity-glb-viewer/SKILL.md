---
name: antigravity-glb-viewer
description: >-
  (💛) Interactive 3D GLB / glTF model viewer UI Sidecar for Google Antigravity's
  right-hand Aux Pane (file_extensions: [".glb", ".gltf"]). Vendored Three.js
  (no CDN) with GLTFLoader + OrbitControls, auto-framing, hemisphere + directional
  lighting, slow left↔right auto-rotation that pauses while you drag, wireframe
  toggle and triangle count. Use whenever an agent produces or references a .glb
  file and wants the user to actually SEE it: emit a
  `sidecar://glb-viewer/view.html?path=/abs/model.glb` pill link.
compatibility: Antigravity, Gemini CLI
metadata:
  version: 0.1.0
---
# Antigravity Inline GLB Viewer Sidecar (`antigravity-glb-viewer`)

## Problem Solved
Agents frequently generate or touch 3D assets (`.glb` / `.gltf`: game pieces,
product mock-ups, scans, AI-generated meshes) but can only describe them in
text. Clicking a `.glb` link in Antigravity shows a binary blob.

Antigravity's `fileView` routes any file extension declared by a running **UI
Sidecar** (`"entrypoint": "SIDECAR_UI_ENTRYPOINT_AUX_PANE"` +
`"file_extensions": [".glb", ".gltf"]`) to that sidecar. This skill bundles a
self-contained, zero-NPM-dependency Node.js `sidecar_sdk` viewer with a
**locally vendored Three.js r170** so it also works offline.

---

## Bundled Files (`$SKILL_DIR/scripts/`)
- `main.mjs` — complete `sidecar_sdk` server + embedded HTML/CSS/JS Three.js viewer.
- `sidecar.json` — manifest registering the Aux Pane view at `/view.html` and `file_extensions: [".glb", ".gltf"]`.
- `vendor/three/` — `three.module.js`, `addons/loaders/GLTFLoader.js`, `addons/controls/OrbitControls.js`, `addons/utils/BufferGeometryUtils.js` (MIT, see `LICENSE` / `VERSION.txt`).
- `install_glb_sidecar.sh` — installs everything into `~/.gemini/config/sidecars/glb-viewer/`.
- `test_glb_viewer.sh` — standalone curl smoke test (no Antigravity needed).
- `README.md` — end-user docs for the installed sidecar (endpoints, tweaks).

---

## Features
- **Open by path:** `?path=/abs/model.glb` (also `?file=` or a `file://` URL). The server only serves files that exist **and** end in `.glb` / `.gltf`; for `.gltf` it also serves sibling `.bin` / textures.
- **Auto-framing:** bounding box → camera distance; model centred on a pivot.
- **Lighting:** hemisphere + key + fill directional lights, ACES tone mapping, shadows.
- **🔄 Auto-rotate (default ON):** slow yaw oscillation left↔right, ±40° with a 6 s period. Pauses while the user drags, resumes ~2 s after release.
- **Mouse:** `OrbitControls` with full azimuth + polar orbit, wheel zoom, right-drag pan.
- **Toolbar:** filename · triangle/mesh count + size · 🔄 Auto-rotate · 🕸️ Wireframe · 🎯 Reset view.
- **Theming:** uses host CSS vars (`--background`, `--card`, `--border`, `--primary`, …) with dark fallbacks.

---

## How an agent should surface a GLB to the user
1. Make sure the file is a local absolute path ending in `.glb` or `.gltf`.
2. Emit a markdown pill link using the `sidecar://` scheme (the host renders it as a clickable pill that opens the Aux Pane):

```markdown
[👑 king-riccardo.glb — open in GLB Viewer 🧊](sidecar://glb-viewer/view.html?path=/abs/path/to/king-riccardo.glb)
```

   `sidecar://glb-viewer/?path=…` works too (both `/` and `/view.html` serve the viewer). URL-encode the path if it contains spaces or `&`.
3. Optionally also give the plain file link `[king-riccardo.glb](file:///abs/path/to/king-riccardo.glb)`; thanks to `file_extensions` it opens in the same viewer.
4. Only emit the pill when the sidecar is installed and enabled/running (see below); otherwise install it first.

---

## Installation & Activation

### Install the Sidecar into `~/.gemini/config/sidecars/glb-viewer`
The sidecar scanner requires a real directory (not a symlink), so run the bundled installer:

```bash
bash "$SKILL_DIR/scripts/install_glb_sidecar.sh"
```

Then **restart Antigravity** (or reload the window) and make sure **GLB Viewer 🧊** is *Enabled* in the Sidecars / UI Plugins panel. Runtime logs land in `<appDataDir>/sidecar_data/glb-viewer/logs/sidecar.log`.

### Prerequisites
- Node.js ≥ 18 (the Antigravity sidecar runner ships its own `sidecar_sdk`; no `npm install` needed).
- WebGL-capable Aux Pane (default in Antigravity).

---

## Testing without Antigravity

```bash
bash "$SKILL_DIR/scripts/test_glb_viewer.sh" /abs/path/to/model.glb
```

It starts `main.mjs` on port 47321 with the three env vars the SDK expects
(`ANTIGRAVITY_LS_ADDRESS`, `ANTIGRAVITY_CSRF_TOKEN`, `ANTIGRAVITY_SIDECAR_WEB_PORT`)
and checks: `GET /?path=…` → 200 HTML; `GET /api/info?path=…` → JSON;
`GET /raw?path=…` → byte-identical model (`glTF` magic); vendor modules → 200;
`/raw?path=/etc/passwd` → 404. Use `curl --noproxy '*'` behind corporate proxies.

---

## Tweaks
Edit the constants at the top of the `<script type="module">` in `main.mjs`:
`SWING_DEG` (±amplitude, default 40), `SWING_PERIOD_S` (default 6), `RESUME_AFTER_MS` (default 2000).

## Related
- `antigravity-pdf-viewer` — same pattern for PDFs; this skill was modelled on it.
