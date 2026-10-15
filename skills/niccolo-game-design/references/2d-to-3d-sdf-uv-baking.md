# 2D-to-3D Local GLB Reconstruction & Portrait Face-Grafting (Zero-GPU Recipe)

When building a 3D web game (Three.js, Babylon.js, Godot, Unity), you often have **gorgeous 2D character portraits or turnaround sheets** (e.g., generated with Nano Banana / Gemini Image), while your 3D `.glb` pipeline hits one of two classic walls:

1. **The "Snowman Primitives" Wall (Missing 3D Generator / Quota Exhausted)**: Cloud 3D generators (`TRELLIS.2`, `Hunyuan3D`, `TripoSR` on Hugging Face ZeroGPU) are rate-limited or offline, and procedural fallback scripts built from spheres/cylinders look like untextured toys.
2. **The "Uncanny Face" Wall (AI 3D Hallucinated the Face)**: You *do* have a full 3D `.glb` from `TRELLIS.2` with a great crown, cape, and body, **but** because the 3D generator was fed a `3/4` angle or hallucinated the far side of the face, the 3D face doesn't look like the real person at all.

This reference documents **two deterministic, CPU-only Python recipes** (`numpy`, `scipy`, `scikit-image`, `trimesh`, `rembg`, `Pillow`) that solve both problems in ~15 seconds on any laptop/workstation without a GPU.

---

## Mode A vs. Mode B: Which One Do You Need?

| Question | **Mode A: Full 2D→3D SDF Sculpting + UV Baking** | **Mode B: 2D Portrait Face-Grafting onto Existing 3D `.glb`** |
|---|---|---|
| **Starting point** | Only a 2D image (either a `0° Front + 90° Side` turnaround sheet, or a single front/`3/4` portrait). Current `.glb` is a terrible procedural placeholder. | An existing 3D `.glb` (e.g. from `TRELLIS.2`) whose 3D body/crown/clothes are good, **but whose 3D face/texture looks wrong**. |
| **What it modifies** | **Both 3D Geometry AND Texture**: carves a brand-new 3D mesh from the 2D silhouettes + luminance relief and bakes a `1024×1024` UV texture from the 2D art. | **Texture / Face UV Region (preserving 3D body geometry)**: keeps the existing `.glb` mesh, crown, and body, and projects/blends the real 2D face onto the 3D head. |
| **Best targets** | Classic Knight (`knight-classic-cavallo.glb`), Swamp characters (`Ciuchino`, `Orco`, `Orchessa`, `Gatto`, `Zenzy`) when replacing untextured procedural meshes. | Carlesso Family portraits (`Papino / King Riccardo`, etc.) where `TRELLIS.2` distorted the facial likeness. |

---

## Mode A: Full 2D→3D SDF Visual-Hull + Relief Sculpting & Seamless UV Baking

### 1. Neural Foreground Segmentation & Halo-Free RGB Dilation
Never map raw un-dilated image pixels onto a 3D mesh: any triangle near the silhouette boundary will sample dark studio background pixels, creating ugly black fringes (e.g., under a horse's chin or between a donkey's ears).

```python
# 1. Segment foreground with rembg (u2net)
rgba = np.asarray(rembg.remove(pil_img), dtype=np.float32) / 255.0
mask = ndimage.binary_fill_holes(rgba[:, :, 3] > 0.52)

# 2. Erode 2px + reject dark studio halo pixels along the boundary
interior = ndimage.binary_erosion(mask, iterations=2)
luma = 0.299 * rgba[:, :, 0] + 0.587 * rgba[:, :, 1] + 0.114 * rgba[:, :, 2]
clean_valid = interior & (luma > 0.22)

# 3. Dilate valid foreground RGB outward 36 iterations so UV borders never bleed dark background
rgb_dilated = dilate_rgb_outside_mask(rgba[:, :, :3], clean_valid, iters=36)
```

### 2. 3D Signed Distance Field (SDF) Carving + Photo-Relief Embossing
- **When you have Dual Views (`0° Front` + `90° Side`)**:
  - For the turned pedestal (`y <= y_pedestal`), revolve the average radial profile `r(y)` with pure axial symmetry.
  - Above the pedestal (`y > y_pedestal`), intersect the Front signed distance field `front_sdf(x, y)`, the Side signed distance field `side_sdf(z, y)`, and an elliptical cross-section envelope `local_half_w(y, z) - |x|`.
- **When you have a Single View (`Front / 3/4 Portrait`)**:
  - Compute the 2D Euclidean Distance Transform `d(x, y) = edt(mask)` inside the character silhouette.
  - Inflate a rounded 3D thickness profile along `Z`:
    $$z_{\text{half}}(x, y) = \min\left(w_{\max}(y),\; c \cdot d(x, y)^{0.58}\right)$$
  - **Photo-Relief Embossing**: High-contrast details in the 2D art (a 40-tooth grin, golden bridle straps, eyes, buttons, crown gems) should physically protrude in 3D:
    ```python
    relief = (luma - ndimage.gaussian_filter(luma, sigma=5.0)) * 0.008
    sdf_vol += relief
    ```

### 3. Budget-Controlled Marching Cubes + Taubin Fairing
- Downsample the SDF volume to `~54 × 74 × 54` before `skimage.measure.marching_cubes(vol, level=0.0)` so the triangle count lands inside `15,000–24,000` triangles (`<= 25,000` web/mobile budget) while keeping the colour maps at full `1024×1024` resolution.
- Run 8–10 iterations of volume-preserving **Taubin smoothing** (`trimesh.smoothing.filter_taubin(mesh, lamb=0.5, nu=-0.53, iterations=10)`).
- Ground strictly at `min.y = 0.0`, scale `max.y` to the canonical piece height (e.g., `1.35m` Knight, `1.80m` King), and flatten the bottom base disc (`y < 0.018m`).

### 4. Boundary-Matched Seamless `1024×1024` UV Atlas
When combining a Front UV panel (`u in [0.5..1.0]`) and a Side UV panel (`u in [0.0..0.5]`):
- Assign the pedestal, neck, sides, and back continuously to the Side panel so no seam ever crosses the base or neck.
- Pre-blend the lateral edges of the Front panel into the Side panel's front-cheek color (`w_edge = clip((|x| - x_inner) / x_feather, 0, 1)`) right inside the texture image itself. At the triangle boundary where the mesh switches from `u_front` to `u_side`, **both panels have identical RGB values — zero visible seam!**

---

## Mode B: 2D Portrait Face-Grafting & Adversarial Biometric Likeness Loop (`graft_papino_face_3d.py` + `adversarial_riccardo_likeness.py`)

When an existing `.glb` (from `TRELLIS.2` or `Hunyuan3D`) has great 3D geometry for the crown, body, and cape, but the face looks distorted or generic:

### 1. Ground-Truth Photo-Anchored Template Seeding (Never Trust Pure Text/Prompt Identity Alone)
- Even when given 5 reference photos, an image generator editing a clean-shaven dark-haired cartoon figurine will either preserve the wrong underlying face geometry or over-apply a thick Santa beard.
- **Solution (`build_photo_seeded_template`)**: Composite the real person's frontal photo (`riccardosouthafrica.png` from `nano-banana-ricc`) directly into the head oval of the figurine template (`rows 212..476`), aligned at the eyes (`row=305..320`), nose bridge (`col=514.5..518.5`), and mouth (`row=418..425`). Pass this photo-seeded composite + the 5 ground-truth reference photos to `gemini-3-pro-image-preview` to studio-harmonize the lighting and temple hair while locking the crown (`y <= 212`) and collar (`y >= 490`) to the original figurine.
- **Anti-Pattern (Do NOT Average Two Portrait Images)**: Never alpha-blend `raw_gen` with the raw photo composite (`blend_real_photo_biometrics`) — even a 5px shift between landmarks creates double-exposure ghosting on the eyes, eyebrows, and mouth. Keep 100% of the harmonized photo-seeded portrait inside the face oval!

### 2. Piecewise-Linear 3D Facial Landmark Calibration (`scale_y_upper` vs. `scale_y_lower`)
- A 3D bobblehead mesh from `TRELLIS.2` rarely has the same upper-to-lower vertical facial ratio as a 2D portrait:
  - Example (`king-riccardo.glb`): above the eye line (`Y_eye = +0.1928m <-> row = 320`), the crown rim sits at `Y = +0.2750m <-> row = 218` (`1240 px/m`), whereas below the eye line the nose tip (`Y = +0.1350m <-> row = 371.6`), mouth (`Y = +0.0750m <-> row = 425`), and chin tip (`Y = +0.0050m <-> row = 487.5`) follow `892 px/m`.
- Using a single uniform `scale_y` either crushes the forehead into the eyes or pushes the chin stubble off the bottom of the 3D jaw onto the neck.
- **Solution**: Map `row_2d(y)` piecewise-linearly around `Y_eye`:
  ```python
  dy_3d = pos[:, 1] - params.y_eye_3d
  row_2d = np.where(
      dy_3d >= 0.0,
      params.row_eye_2d - dy_3d * params.scale_y_upper,  # 1240.0 px/m (eye -> crown rim)
      params.row_eye_2d - dy_3d * params.scale_y_lower,  #  892.0 px/m (eye -> nose -> mouth -> chin)
  )
  ```

### 3. Stripping 2D Sideburns & Mirroring Clean Temple Skin (`prepare_clean_front_face`)
- Because a 3D bobblehead's cheeks (`|X| = 0.088m`) are wider than the 2D head (`cols 430..602`), keeping 2D sideburns or dark outer-eye shadows at the edge of the 2D crop causes `dilate_rgb_outside_mask` to smear dark horizontal/vertical streaks across the 3D cheeks.
- **Solution**: Restrict the 2D face oval to the inner facial skin (`cols 428..604`, inside the 2D sideburns), mirror clean warm left-cheek skin onto `col >= 593` (just past the outer corner of the right eye/eyebrow), and dilate clean cheek skin outward 95 iterations.

### 4. Dual-Chart `2048×1024` Atlas + Zero-Bleed Barycentric Hair Recoloring
- Pack the original `1024×1024` `xatlas` texture into the left half (`u in [0.0, 0.5]`) and the high-resolution `1024×1024` Front Face Chart into the right half (`u in [0.5, 1.0]`), splitting the mesh at the front facial shell (`y in [0.002, 0.278]`, `z > 0.040`).
- **Zero-Bleed `xatlas` Hair Recoloring (`recolor_strict_hair_texels_zero_bleed`)**: Because `xatlas` packs crown, neck, ear, and hair UV islands only 1–2 pixels apart, **never** expand triangle bounding boxes (`pad > 0`) or apply Gaussian blur in `xatlas` UV space, and always sample `base_chart_rgb` from the untouched original texture before recoloring hair texels inside exact barycentric triangle masks (`w0, w1, w2 >= -0.04`, `lum < 0.50`, `r - b < 0.105`).

### 5. Multimodal Adversarial Biometric Critic Loop (`adversarial_riccardo_likeness.py`)
- Pair the 2D+3D generator with an uncompromising VLM Critic (`gemini-3.1-pro-preview` + subagent `riccardo-likeness-critic`) that inspects a 6-panel biometric sheet (**Panel 1**: 5 ground-truth photos; **Panel 2**: 2D `front.png`; **Panels 3–6**: 3D GLB renders at `0°`, `+32°`, `+72°`, and full-body `0°`) and returns structured JSON scores (`0..10`) across 6 biometric axes plus bounded parameter updates until likeness converges (`>= 8.5/10`).

---

## Verification & Cache-Busting Checklist

- [ ] **Automated Contract Check**: `min.y == 0.0` (`±0.01m`), `max.y == target_height_m` (`±0.03m`), `500 <= faces <= 25000`, valid `TEXCOORD_0` and embedded PNG `baseColorTexture`.
- [ ] **4-Angle Per-Pixel Turntable + 360° Rotating GIF**: Always render both a 4-angle (`0°`, `32°/38°`, `72°/90°`, `180°`) per-pixel UV+Gouraud contact strip AND a 24-frame 360° rotating `.gif` so the human reviewer can verify the 3D volume in motion.
- [ ] **Browser & Service Worker Cache Busting**: Append `?v=<VERSION>` to `.glb` URLs in showcase/game manifests and increment `CACHE_NAME` in `sw.js` — otherwise `GLTFLoader` and the Service Worker will silently serve the old cached `.glb`.
