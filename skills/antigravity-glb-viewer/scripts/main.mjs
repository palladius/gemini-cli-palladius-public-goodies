/**
 * Antigravity / Jetski GLB 3D Model Viewer Sidecar 🧊
 *
 * Renders local .glb / .gltf files in the right-hand Aux Pane with Three.js
 * (vendored locally, no CDN). Modelled on the pdf-viewer sidecar.
 *
 * Open with:  sidecar://glb-viewer/?path=/abs/path/to/model.glb
 */
import { existsSync, readFileSync, statSync } from 'node:fs';
import { basename, dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SidecarApp, Response } from 'sidecar_sdk';

const app = new SidecarApp();
const CURRENT_DIR = dirname(fileURLToPath(import.meta.url));
const VENDOR_DIR = join(CURRENT_DIR, 'vendor');
const ALLOWED_EXT = new Set(['.glb', '.gltf']);

/** Resolve + validate a user-supplied model path (must exist, must be .glb/.gltf). */
function normalizeModelPath(rawPath) {
  if (!rawPath || typeof rawPath !== 'string') return null;
  let p = rawPath.trim();
  if (p.startsWith('file://')) {
    try {
      p = fileURLToPath(p);
    } catch {
      p = decodeURIComponent(p.replace(/^file:\/\//, ''));
    }
  }
  p = resolve(p);
  if (!ALLOWED_EXT.has(extname(p).toLowerCase())) return null;
  if (!existsSync(p)) return null;
  try {
    if (!statSync(p).isFile()) return null;
  } catch {
    return null;
  }
  return p;
}

function modelInfo(filePath) {
  const stat = statSync(filePath);
  return {
    file: filePath,
    filename: basename(filePath),
    sizeBytes: stat.size,
    ext: extname(filePath).toLowerCase(),
    mtime: stat.mtime.toISOString(),
  };
}

/** Vendored Three.js files served as ES modules (exact-path routes; the SDK has no wildcard). */
const VENDOR_FILES = [
  '/vendor/three/three.module.js',
  '/vendor/three/addons/loaders/GLTFLoader.js',
  '/vendor/three/addons/controls/OrbitControls.js',
  '/vendor/three/addons/utils/BufferGeometryUtils.js',
];

const VIEW_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>GLB Viewer 🧊</title>
<script src="/preload.js"></script>
<script type="importmap">
{ "imports": { "three": "/vendor/three/three.module.js" } }
</script>
<style>
  :root {
    --bg: var(--background, #141416);
    --fg: var(--foreground, #ececf1);
    --card: var(--card, #1e1f23);
    --border: var(--border, #2e3038);
    --muted: var(--muted-foreground, #9ca3af);
    --accent: var(--primary, #60a5fa);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; }
  body {
    background: var(--bg);
    color: var(--fg);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 12px;
    background: var(--card);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
    flex-wrap: wrap;
    z-index: 20;
  }
  .file-meta { display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1; }
  .file-title {
    font-size: 13px; font-weight: 600;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .badge {
    font-size: 11px; color: var(--muted);
    background: rgba(128,128,128,0.15);
    padding: 2px 7px; border-radius: 999px; white-space: nowrap;
    font-variant-numeric: tabular-nums;
  }
  .toolbar { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
  button {
    background: rgba(128,128,128,0.14);
    color: var(--fg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.12s ease;
    display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;
  }
  button:hover:not(:disabled) { background: rgba(128,128,128,0.26); border-color: var(--accent); }
  button.active { background: var(--accent); color: #000; border-color: var(--accent); font-weight: 600; }
  main { flex: 1; position: relative; overflow: hidden; min-height: 0; }
  canvas { display: block; width: 100%; height: 100%; outline: none; touch-action: none; }
  .status-box {
    position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    text-align: center; color: var(--muted); font-size: 13px; line-height: 1.5;
    padding: 24px; pointer-events: none;
  }
  .status-box.hidden { display: none; }
  .status-box b { color: var(--fg); }
  .hint {
    position: absolute; left: 10px; bottom: 8px;
    font-size: 10.5px; color: var(--muted); opacity: 0.75; pointer-events: none;
  }
  footer {
    flex-shrink: 0; padding: 5px 12px; background: var(--card);
    border-top: 1px solid var(--border); text-align: center;
    font-size: 11.5px; font-style: italic; color: var(--muted); z-index: 20;
  }
  footer a { color: var(--accent); text-decoration: none; font-weight: 500; }
  footer a:hover { text-decoration: underline; }
</style>
</head>
<body>
  <header>
    <div class="file-meta">
      <span>🧊</span>
      <span class="file-title" id="filename">Loading model...</span>
      <span class="badge" id="tri-badge" title="Triangles / meshes / size">–</span>
    </div>
    <div class="toolbar">
      <button id="btn-rotate" class="active" title="Toggle slow left↔right auto-rotation">🔄 Auto-rotate</button>
      <button id="btn-wire" title="Toggle wireframe">🕸️ Wireframe</button>
      <button id="btn-reset" title="Re-frame the model and reset the camera">🎯 Reset view</button>
    </div>
  </header>

  <main id="stage">
    <canvas id="c"></canvas>
    <div class="status-box" id="status">Loading 3D model...</div>
    <div class="hint">drag: orbit · wheel: zoom · right-drag: pan</div>
  </main>

  <footer>
    Made by 💛 <a href="https://www.linkedin.com/in/riccardocarlesso/" target="_blank" rel="noopener noreferrer">Riccardo</a> with <a href="https://antigravity.google/" target="_blank" rel="noopener noreferrer">Antigravity</a> · three.js
  </footer>

<script type="module">
  import * as THREE from 'three';
  import { GLTFLoader } from '/vendor/three/addons/loaders/GLTFLoader.js';
  import { OrbitControls } from '/vendor/three/addons/controls/OrbitControls.js';

  // ---- config -------------------------------------------------------------
  const SWING_DEG = 40;          // yaw oscillation amplitude (±)
  const SWING_PERIOD_S = 6;      // full left→right→left period
  const RESUME_AFTER_MS = 2000;  // resume auto-rotate this long after the user lets go

  const params = new URLSearchParams(window.location.search);
  const modelPath = params.get('path') || params.get('file') || '';

  const statusEl = document.getElementById('status');
  const filenameEl = document.getElementById('filename');
  const triBadge = document.getElementById('tri-badge');
  const btnRotate = document.getElementById('btn-rotate');
  const btnWire = document.getElementById('btn-wire');
  const btnReset = document.getElementById('btn-reset');
  const stage = document.getElementById('stage');
  const canvas = document.getElementById('c');

  function setStatus(html, show = true) {
    statusEl.innerHTML = html;
    statusEl.classList.toggle('hidden', !show);
  }
  function formatBytes(b) {
    if (!b) return '';
    if (b < 1024) return b + ' B';
    if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
    return (b / (1024 * 1024)).toFixed(2) + ' MB';
  }
  function cssColor(varName, fallback) {
    const v = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
    if (!v) return fallback;
    try { return new THREE.Color(v); } catch { return fallback; }
  }

  // ---- renderer / scene ---------------------------------------------------
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;

  const scene = new THREE.Scene();
  function applyThemeBackground() {
    const bg = cssColor('--background', new THREE.Color(0x141416));
    scene.background = bg;
  }
  applyThemeBackground();
  // Host theme changes land as CSS var updates on <html>; re-read lazily.
  new MutationObserver(applyThemeBackground).observe(document.documentElement, { attributes: true, attributeFilter: ['style', 'class'] });

  const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 1000);
  camera.position.set(0, 1, 3);

  const hemi = new THREE.HemisphereLight(0xffffff, 0x334455, 1.4);
  scene.add(hemi);
  const dir = new THREE.DirectionalLight(0xffffff, 2.2);
  dir.position.set(3, 6, 4);
  dir.castShadow = true;
  dir.shadow.mapSize.set(1024, 1024);
  scene.add(dir);
  const fill = new THREE.DirectionalLight(0xbfd4ff, 0.6);
  fill.position.set(-4, 2, -3);
  scene.add(fill);

  // Pivot group: auto-rotation yaws this, OrbitControls moves the camera.
  const pivot = new THREE.Group();
  scene.add(pivot);

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = true;
  controls.enableZoom = true;
  controls.enableRotate = true;          // both azimuth + polar
  controls.minPolarAngle = 0;
  controls.maxPolarAngle = Math.PI;      // full polar freedom
  controls.screenSpacePanning = true;

  // ---- state --------------------------------------------------------------
  let model = null;
  let autoRotate = true;
  let wireframe = false;
  let userInteracting = false;
  let resumeTimer = null;
  let swingT = 0;                 // seconds accumulated while swinging
  let homeCam = { pos: new THREE.Vector3(0, 1, 3), target: new THREE.Vector3() };
  const clock = new THREE.Clock();

  controls.addEventListener('start', () => {
    userInteracting = true;
    if (resumeTimer) { clearTimeout(resumeTimer); resumeTimer = null; }
  });
  controls.addEventListener('end', () => {
    resumeTimer = setTimeout(() => { userInteracting = false; resumeTimer = null; }, RESUME_AFTER_MS);
  });

  function setAutoRotate(on) {
    autoRotate = on;
    btnRotate.classList.toggle('active', on);
  }
  btnRotate.addEventListener('click', () => setAutoRotate(!autoRotate));

  btnWire.addEventListener('click', () => {
    wireframe = !wireframe;
    btnWire.classList.toggle('active', wireframe);
    if (!model) return;
    model.traverse((o) => {
      if (o.isMesh && o.material) {
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        mats.forEach((m) => { m.wireframe = wireframe; m.needsUpdate = true; });
      }
    });
  });

  btnReset.addEventListener('click', () => {
    pivot.rotation.y = 0;
    swingT = 0;
    camera.position.copy(homeCam.pos);
    controls.target.copy(homeCam.target);
    controls.update();
  });

  // ---- framing ------------------------------------------------------------
  function frameModel(obj) {
    const box = new THREE.Box3().setFromObject(obj);
    if (box.isEmpty()) return;
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    // Center the model at the pivot origin so yaw rotates around its own axis.
    obj.position.sub(center);

    const maxDim = Math.max(size.x, size.y, size.z) || 1;
    const fov = THREE.MathUtils.degToRad(camera.fov);
    let dist = (maxDim / 2) / Math.tan(fov / 2);
    dist *= 1.35; // breathing room
    camera.near = Math.max(dist / 1000, 0.001);
    camera.far = dist * 100;
    camera.updateProjectionMatrix();

    const pos = new THREE.Vector3(dist * 0.55, dist * 0.45, dist * 0.8);
    camera.position.copy(pos);
    controls.target.set(0, 0, 0);
    controls.minDistance = dist * 0.05;
    controls.maxDistance = dist * 10;
    controls.update();

    homeCam = { pos: pos.clone(), target: new THREE.Vector3() };
  }

  function countTriangles(obj) {
    let tris = 0, meshes = 0;
    obj.traverse((o) => {
      if (!o.isMesh || !o.geometry) return;
      meshes++;
      const g = o.geometry;
      const n = g.index ? g.index.count : (g.attributes.position ? g.attributes.position.count : 0);
      tris += Math.floor(n / 3);
    });
    return { tris, meshes };
  }

  // ---- load ---------------------------------------------------------------
  async function load() {
    if (!modelPath) {
      filenameEl.textContent = 'GLB Viewer 🧊';
      setStatus('🧊 <b>GLB Viewer active!</b><br><br>Open with <code>sidecar://glb-viewer/?path=/abs/model.glb</code><br>or click a <code>.glb</code> / <code>.gltf</code> file.');
      return;
    }
    const q = new URLSearchParams();
    q.set('path', modelPath);

    let info;
    try {
      const res = await fetch('/api/info?' + q.toString());
      info = await res.json();
      if (info.error) { setStatus('⚠️ ' + info.error); filenameEl.textContent = 'GLB Viewer 🧊'; return; }
    } catch (e) {
      setStatus('⚠️ Cannot reach sidecar: ' + e.message); return;
    }
    filenameEl.textContent = info.filename;
    filenameEl.title = info.file;
    document.title = info.filename + ' · GLB Viewer 🧊';

    setStatus('Loading <b>' + info.filename + '</b> (' + formatBytes(info.sizeBytes) + ')...');
    const loader = new GLTFLoader();
    // Resource base: for .gltf with external buffers/textures, siblings are fetched via /raw?path=<sibling>.
    const baseDir = info.file.slice(0, info.file.lastIndexOf('/') + 1);
    loader.manager.setURLModifier((url) => {
      if (url.startsWith('/raw') || url.startsWith('blob:') || url.startsWith('data:')) return url;
      const abs = url.startsWith('/') ? url : baseDir + url;
      return '/raw?path=' + encodeURIComponent(abs);
    });

    loader.load(
      '/raw?path=' + encodeURIComponent(info.file),
      (gltf) => {
        model = gltf.scene || gltf.scenes[0];
        model.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
        pivot.add(model);
        frameModel(model);
        const { tris, meshes } = countTriangles(model);
        triBadge.textContent = tris.toLocaleString() + ' tris · ' + meshes + ' mesh' + (meshes === 1 ? '' : 'es') + ' · ' + formatBytes(info.sizeBytes);
        setStatus('', false);
      },
      (ev) => {
        if (ev.total) setStatus('Loading <b>' + info.filename + '</b> ' + Math.round(100 * ev.loaded / ev.total) + '%');
      },
      (err) => {
        console.error(err);
        setStatus('⚠️ Failed to parse model: ' + (err?.message || err));
      }
    );
  }

  // ---- resize / loop ------------------------------------------------------
  function resize() {
    const w = stage.clientWidth || 1, h = stage.clientHeight || 1;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stage);
  resize();

  const SWING_RAD = THREE.MathUtils.degToRad(SWING_DEG);
  function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.1);
    if (autoRotate && !userInteracting && model) {
      swingT += dt;
      // Smooth left↔right oscillation: yaw = A * sin(2π t / T)
      pivot.rotation.y = SWING_RAD * Math.sin((2 * Math.PI * swingT) / SWING_PERIOD_S);
    }
    controls.update();
    renderer.render(scene, camera);
  }
  animate();
  load();
</script>
</body>
</html>`;

app.page('/', () => VIEW_HTML);
app.page('/view.html', () => VIEW_HTML);

// Vendored three.js modules (GET → no auth required by the SDK).
for (const route of VENDOR_FILES) {
  const diskPath = join(CURRENT_DIR, route);
  app.api(route, () => {
    if (!existsSync(diskPath)) {
      return new Response('vendor file missing: ' + route, { status: 404, contentType: 'text/plain' });
    }
    return new Response(readFileSync(diskPath), {
      status: 200,
      contentType: 'application/javascript; charset=utf-8',
      headers: { 'Cache-Control': 'private, max-age=3600' },
    });
  }, 'GET');
}

app.api('/api/info', (data) => {
  const raw = data.path || data.file;
  const filePath = normalizeModelPath(raw);
  if (!filePath) {
    return { error: `Model not found or not a .glb/.gltf: ${raw || '(no path given)'}` };
  }
  return modelInfo(filePath);
}, 'GET');

/** Raw bytes of the model (or, for .gltf, its sibling .bin / texture referenced relatively). */
app.api('/raw', (data) => {
  const raw = data.path || data.file;
  let filePath = normalizeModelPath(raw);
  let contentType = 'model/gltf-binary';
  if (!filePath) {
    // Allow .gltf sibling resources (buffers / textures) living next to a .gltf.
    const p = raw ? resolve(String(raw)) : '';
    const ext = extname(p).toLowerCase();
    const siblingTypes = {
      '.bin': 'application/octet-stream',
      '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
      '.webp': 'image/webp', '.ktx2': 'image/ktx2',
    };
    if (p && siblingTypes[ext] && existsSync(p) && statSync(p).isFile()) {
      filePath = p;
      contentType = siblingTypes[ext];
    }
  } else if (filePath.toLowerCase().endsWith('.gltf')) {
    contentType = 'model/gltf+json';
  }
  if (!filePath) {
    return new Response('File not found or extension not allowed', { status: 404, contentType: 'text/plain' });
  }
  return new Response(readFileSync(filePath), {
    status: 200,
    contentType,
    headers: {
      'Content-Disposition': `inline; filename="${basename(filePath)}"`,
      'Cache-Control': 'private, max-age=60',
    },
  });
}, 'GET');

app.run();
