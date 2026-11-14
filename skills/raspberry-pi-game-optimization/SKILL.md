---
name: raspberry-pi-game-optimization
description: "(💛🍓) Optimize Web, Flutter/CanvasKit, HTML5 Canvas2D, and Three.js/WebGL games for Raspberry Pi 400 ('Sguisatazzo') and low-end ARM64 SBCs. Covers Broadcom BCM2711 Cortex-A72 (1 MB L2 cache) & VideoCore VI (V3D 4.2) hardware constraints, WebKit2GTK DMA-BUF & ImageDecoder fixes, Flutter targetWidth texture downscaling, RepaintBoundary isolation, and zero-idle-CPU ticker design."
---

# 🍓🐧 Raspberry Pi 400 ("Sguisatazzo") Game Optimization Guide

Use this skill whenever building, auditing, or optimizing web games (Flutter Web / CanvasKit, HTML5 Canvas 2D, Three.js / WebGL, or WebAssembly TUIs) so they are **Raspberry-Compliant** and run at 30–60 FPS with **0% idle CPU** on a **Raspberry Pi 400** (or Raspberry Pi 4 / 5).

---

## 1. Know the Hardware Bottlenecks (Raspberry Pi 400 / BCM2711)

Before optimizing, understand **why** desktop web games crawl on a Raspberry Pi 400 (`sguisatazzo`):

| Component | Spec on Raspberry Pi 400 | Why Naive Games Freeze |
| :--- | :--- | :--- |
| **CPU** | Broadcom BCM2711, 4× ARM Cortex-A72 @ 1.8 GHz | Out-of-order 2015 core; single-thread JS/WASM throughput is ~1/6th of desktop x86/M-series. |
| **L2 Cache** | **1 MB shared L2 cache** across all 4 cores | Any per-frame RGBA buffer or texture blitz > 1 MB evicts the entire L2 cache to LPDDR4 RAM. |
| **GPU** | Broadcom **VideoCore VI (V3D 4.2)** @ 500 MHz | OpenGL ES 3.1 / Vulkan 1.0 tile-based renderer. **Fragment-fillrate bound** at 1080p (`1920×1080`). Gaussian blurs (`MaskFilter.blur` / CSS `backdrop-filter`) and multi-pass `saveLayer` offscreen FBOs destroy frame times. |
| **Display / Wayland** | `labwc` (wlroots Wayland) @ `1920×1080` | WebKit2GTK 2.50+ DMA-BUF sharing fails on V3D + `labwc` unless `WEBKIT_DISABLE_DMABUF_RENDERER=1` is set. |

---

## 2. Auto-Detection Pattern (`PerformanceConfig` & JS Bridge)

Every Raspberry-Compliant game MUST auto-detect Raspberry Pi / Linux ARM64 / low-DPR runners at startup **and** provide URL query overrides (`?rpi=1`, `?sguisatazzo=1`, `?lowperf=1`) plus an in-game `🍓 RPi Turbo` toggle.

### Early `index.html` Detection Snippet
Place this in `<head>` **before** loading any game bundle or `flutter_bootstrap.js`:

```html
<script>
  (function() {
    var params = new URLSearchParams(window.location.search);
    var ua = navigator.userAgent || '';
    var plat = navigator.platform || '';
    var isArmLinux = /Linux/i.test(ua + ' ' + plat) && /(aarch64|arm64|armv7|armv8|raspbian|crKey)/i.test(ua + ' ' + plat);
    var isLowDpr = (window.devicePixelRatio && window.devicePixelRatio <= 0.85); // sguisa-game-runner sets 0.75
    var forceRpi = params.get('rpi') === '1' || params.get('sguisatazzo') === '1' || params.get('lowperf') === '1' || params.get('lite') === '1';
    var disableRpi = params.get('rpi') === '0' || params.get('highperf') === '1';
    window._rpiTurboMode = disableRpi ? false : (forceRpi || isArmLinux || isLowDpr);

    if (window._rpiTurboMode) {
      document.documentElement.classList.add('rpi-mode');
    }

    // CRITICAL FIX for Flutter CanvasKit on WebKit2GTK 2.54+ (Raspberry Pi OS Trixie):
    // When WebGL is disabled or running in software CanvasKit mode, WebKit's browser
    // ImageDecoder API hangs or fails to decode PNGs. Deleting window.ImageDecoder
    // forces CanvasKit to use its internal WASM Skia codec (MakeAnimatedImageFromEncoded).
    var isWebKitGtk = /AppleWebKit/i.test(ua) && !/Chrome|Chromium|CriOS|Edg/i.test(ua) && /Linux/i.test(ua + ' ' + plat);
    if (isWebKitGtk || params.get('skia_codec') === '1') {
      try { delete window.ImageDecoder; } catch (_) {}
    }
  })();
</script>
```

---

## 3. The 7 Golden Rules for Flutter Web / CanvasKit Games (e.g., `tubature`)

When optimizing a Flutter Web game for Raspberry Pi 400 (`tubature` v2.13.0 case study):

### Rule 1: Downscale Textures at Decode Time (`targetWidth` / `targetHeight`)
* **Problem**: 22 PNG sprites at `1024×1024` decode into `22 × 4 MB = 88 MB` of raw RGBA textures, thrashing the BCM2711's 1 MB L2 cache on every draw call.
* **Fix**: Always pass `targetWidth` and `targetHeight` to `ui.instantiateImageCodec`:
  ```dart
  final targetSize = PerformanceConfig.instance.goodieImageTargetSize; // 128 on RPi, 256 on Desktop
  final codec = await ui.instantiateImageCodec(
    bytes,
    targetWidth: targetSize,
    targetHeight: targetSize,
  );
  ```
* **Impact**: Cuts texture RAM by **98%** (`88 MB` -> `1.4 MB`), fitting all active sprites inside the CPU L2 cache.

### Rule 2: Wrap Every Interactive Grid Cell in `RepaintBoundary`
* **Problem**: Without `RepaintBoundary`, rotating a single tile or animating water flood in one pipe invalidates and repaints the **entire N×N board** (`64 tiles` on an 8×8 grid).
* **Fix**: Wrap each `TileWidget` and the parent `GridWidget` in `RepaintBoundary`:
  ```dart
  return RepaintBoundary(
    child: CustomPaint(
      painter: PipePainter(...),
    ),
  );
  ```

### Rule 3: Zero Idle Ticker Rule (0% CPU at Rest)
* **Problem**: Continuous `AnimationController(...)..repeat()` loops (water shimmer on every connected tile, hidden avatar blink timers, background floating particles, video listener `setState(() {})` calls) burn 100% of a Cortex-A72 core even when the player is just thinking!
* **Fix**:
  1. Never run `..repeat()` on N tiles simultaneously in `rpiMode` — animate only during active water flow (`waterFill < 1.0`), then settle to a static paint (`0% idle CPU`).
  2. Stop hidden widget timers (`_blinkController.stop()`) whenever `_isVisible == false`.
  3. Never call `setState(() {})` inside a `VideoPlayerController.addListener` unless a boolean state (`_hasError`, `_isFinished`) actually changed.

### Rule 4: Ban `canvas.saveLayer` and `MaskFilter.blur` in CustomPainters
* **Problem**: `canvas.saveLayer()` allocates an offscreen framebuffer per widget per frame; `MaskFilter.blur(BlurStyle.normal, sigma)` executes a multi-pass Gaussian convolution shader that stalls VideoCore VI.
* **Fix**:
  * Replace `canvas.saveLayer` + `BlendMode.dstOut` fog reveals with a simple radial gradient or direct alpha fill in `rpiMode`.
  * Replace `MaskFilter.blur` glows with a slightly wider semi-transparent stroke (`color.withValues(alpha: 0.25)`, `strokeWidth + 4`) and `BlurStyle.solid` or no blur at all.

### Rule 5: Replace Trigonometric Wave Loops on Settled Elements
* **Problem**: Computing 39-point `math.sin` / `math.cos` `Path` polygons + rising bubble circles on 20 settled sidebar potions (`ampolle`) every frame wastes thousands of FP ops per second.
* **Fix**: Once `fillProgress >= 1.0` (or when `enableCauldronMasterEffects == false`), draw a single flat `Rect` + highlight bar inside `canvas.clipPath(flaskPath)`.

### Rule 6: Ban CSS / Flutter `BackdropFilter` (`ImageFilter.blur`)
* **Problem**: Full-screen frosted glass modals (`BackdropFilter(filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8))`) force a full-screen readback + blur pass on every frame of modal entry/confetti animation.
* **Fix**: Gate `BackdropFilter` on `PerformanceConfig.instance.enableBackdropBlur` and fall back to a crisp translucent `ColoredBox(color: Color(0xCC1A0E2E))`.

### Rule 7: Skip 1080p MP4 Autoplay in RPi Mode
* **Problem**: Software-decoding a 1080p H.264 MP4 background while simultaneously compiling shaders and decoding 22 PNGs freezes startup for 4–6 seconds.
* **Fix**: In `rpiMode`, skip background video autoplay and show a lightweight `"🍓 RPi Turbo • Play Intro Video 🔊"` button so the user can play it on demand.

---

## 4. Rules for Three.js / WebGL & HTML5 Canvas 2D Games

1. **Cap Pixel Ratio to `0.75`–`1.0`**:
   ```js
   renderer.setPixelRatio(window._rpiTurboMode ? 0.75 : Math.min(window.devicePixelRatio, 2));
   ```
   Dropping pixelRatio from `1.0` to `0.75` at `1920×1080` reduces fragment shader invocations by **44%** (`2.07M` -> `1.16M` pixels).
2. **Disable Expensive Post-Processing & Shadow Maps**:
   * Disable `UnrealBloomPass`, `SSAOPass`, and `renderer.shadowMap.enabled` in `_rpiTurboMode`.
   * Prefer `MeshLambertMaterial` or `MeshToonMaterial` over multi-light `MeshStandardMaterial` / `MeshPhysicalMaterial`.
3. **Avoid Canvas 2D `ctx.shadowBlur`**:
   * In HTML5 Canvas 2D (`dots-and-lines`, `smurfs-and-dragons`, `demo-snake`), `ctx.shadowBlur > 0` triggers software Gaussian blur on every stroke. In `_rpiTurboMode`, set `ctx.shadowBlur = 0` and draw a second wider stroke with `globalAlpha = 0.25`.

---

## 5. Native Raspberry Pi Launcher (`sguisa-game-runner` / WebKit2GTK)

On Raspberry Pi OS Trixie (`aarch64`, `labwc`), launching full Chromium (~450 MB RAM) for every local game is unnecessary when serving static bundles from `http://127.0.0.1:8765/<game>/`.
A lightweight 80-line C launcher (`sguisa-game-runner`) using `webkit2gtk-4.1` starts in **0.4 seconds** and uses **95 MB RAM**:

* Always set `setenv("WEBKIT_DISABLE_DMABUF_RENDERER", "1", 0);` before `gtk_init()` to avoid blank windows on VideoCore VI + `labwc`.
* Inject `Object.defineProperty(window, 'devicePixelRatio', {get: function(){return 0.75;}});` at `WEBKIT_USER_SCRIPT_INJECT_AT_DOCUMENT_START` so both WebGL/Canvas and Flutter automatically detect low-DPR mode and render at 75% resolution.

---

## 6. Verification Checklist for `#raspberry-optimized` Badge in Vetrina

Before adding `raspberry_optimized: true` and `- raspberry-optimized` in `vetrina/data/games.yaml`:

- [ ] **Auto-Detection**: Game detects `Linux aarch64` / `devicePixelRatio <= 0.85` / `?rpi=1` automatically.
- [ ] **Manual Toggle**: User can toggle `🍓 RPi Turbo` on/off in the UI (or via `?rpi=1` / `?rpi=0`).
- [ ] **0% Idle CPU**: When no user input or transition is happening, no `requestAnimationFrame` or Flutter `Ticker` repaints the board.
- [ ] **Bounded Textures**: Decoded image textures stay under 10 MB total (`targetWidth <= 256`).
- [ ] **No Gaussian Blurs in RPi Mode**: `BackdropFilter`, `MaskFilter.blur`, and `ctx.shadowBlur` are bypassed.
- [ ] **Offline / Local Server Ready**: Game runs cleanly from `http://127.0.0.1:8765/<game>/` on `sguisatazzo`.
