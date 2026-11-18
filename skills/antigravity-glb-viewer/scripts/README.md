# GLB Viewer 🧊 — Antigravity / Jetski UI Sidecar

Interactive 3D viewer for local **`.glb` / `.gltf`** models rendered in the
right-hand Aux Pane. Built on the Node.js `sidecar_sdk` with a **locally
vendored Three.js r170** (no CDN at runtime). Modelled on the `pdf-viewer`
sidecar that lives next to it.

## Features

- 📂 Opens any local model via `?path=/abs/file.glb` (also accepts `?file=`
  and `file://` URLs). Only files that exist **and** end in `.glb` / `.gltf`
  are served; anything else → `404`.
- 🎯 Auto-framing: bounding box → camera distance, model centred on the pivot.
- 💡 Hemisphere + key + fill directional lights, ACES tone mapping, shadows.
- 🔄 **Auto-rotate by default**: slow yaw oscillation left↔right (±40°, 6 s
  period). Pauses while you drag; resumes ~2 s after you let go.
- 🖱️ `OrbitControls`: orbit in both azimuth and polar, wheel zoom, right-drag
  pan.
- 🧰 Toolbar: filename, triangle / mesh count + size, **Auto-rotate** toggle,
  **Wireframe** toggle, **Reset view**.
- 🎨 Background and chrome follow host theme CSS variables (`--background`,
  `--card`, `--border`, `--primary`, …) with dark fallbacks.

## File tree

```
~/.gemini/config/sidecars/glb-viewer/
├── sidecar.json            # manifest: node main.mjs, AUX_PANE view, file_extensions [.glb,.gltf]
├── main.mjs                # sidecar_sdk server + embedded HTML/JS viewer
├── README.md
└── vendor/three/           # three.js r170 (MIT) — three.module.js + addons
    ├── three.module.js
    ├── LICENSE / VERSION.txt
    └── addons/{loaders/GLTFLoader.js, controls/OrbitControls.js, utils/BufferGeometryUtils.js}
```

## Enabling it

The folder sits in `~/.gemini/config/sidecars/`, which Antigravity / Jetski
scans for sidecars. After creating or changing it:

1. Restart Antigravity / Jetski (or reload the window) so the new sidecar is
   discovered.
2. In the **UI Plugins / Sidecars** tab make sure **GLB Viewer 🧊** is
   *Enabled*; the host then spawns `node main.mjs` with the right env vars.
3. Logs: `<appDataDir>/sidecar_data/glb-viewer/logs/sidecar.log`.

## Opening a model (pill link)

Emit a standard markdown link with the `sidecar://` scheme; the host turns it
into a clickable pill that opens the pane:

```markdown
[GLB Viewer 🧊](sidecar://glb-viewer/view.html?path=/abs/path/to/model.glb)
```

Both `/` and `/view.html` serve the viewer, so
`sidecar://glb-viewer/?path=/abs/path/to/model.glb` works too. Because the
manifest declares `file_extensions: [".glb", ".gltf"]`, clicking a
`[model.glb](file:///abs/path/model.glb)` link in chat also routes to this
viewer.

## HTTP endpoints

| Route | Purpose |
|---|---|
| `GET /` , `GET /view.html` | the viewer page (reads `?path=` client-side) |
| `GET /api/info?path=…` | JSON `{file, filename, sizeBytes, ext, mtime}` or `{error}` |
| `GET /raw?path=…` | raw model bytes (`model/gltf-binary` / `model/gltf+json`); for `.gltf` also serves sibling `.bin` / textures |
| `GET /vendor/three/...` | the vendored Three.js modules |

## Testing standalone (no Antigravity)

The SDK only needs three env vars and the ESM loader shim:

```bash
cd ~/.gemini/config/sidecars/glb-viewer
ANTIGRAVITY_LS_ADDRESS=127.0.0.1:1 ANTIGRAVITY_CSRF_TOKEN=test ANTIGRAVITY_SIDECAR_WEB_PORT=47321 \
  node --import ~/.gemini/antigravity/lib/node_modules/sidecar_sdk/register_loader.js main.mjs &

MODEL=/abs/path/to/model.glb
curl -s --noproxy '*' -o /dev/null -w '%{http_code} %{content_type}\n' "http://127.0.0.1:47321/?path=$MODEL"      # 200 text/html
curl -s --noproxy '*' "http://127.0.0.1:47321/api/info?path=$MODEL"                                              # JSON
curl -s --noproxy '*' -o /tmp/rt.glb -w '%{http_code} %{content_type} %{size_download}\n' "http://127.0.0.1:47321/raw?path=$MODEL"
cmp "$MODEL" /tmp/rt.glb && echo bytes-identical
curl -s --noproxy '*' -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:47321/raw?path=/etc/passwd'            # 404
```

(`--noproxy '*'` matters on machines with a corporate HTTP proxy, otherwise the
proxy answers "Direct IP access is not allowed".) Then open
`http://127.0.0.1:47321/?path=$MODEL` in a browser to eyeball the rendering.

## Tweaks

Constants at the top of the `<script type="module">` block in `main.mjs`:
`SWING_DEG` (±amplitude), `SWING_PERIOD_S`, `RESUME_AFTER_MS`.
