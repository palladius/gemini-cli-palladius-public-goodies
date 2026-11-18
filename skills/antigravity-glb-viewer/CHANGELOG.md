# CHANGELOG for antigravity-glb-viewer

## 0.1.0 (2026-11-06)
- Initial release of `antigravity-glb-viewer` (`sidecars/glb-viewer/` + `skills/antigravity-glb-viewer/`), modelled on `antigravity-pdf-viewer`.
- Node.js `sidecar_sdk` server serving the page, `/api/info`, `/raw` (extension-whitelisted `.glb` / `.gltf` + sibling buffers/textures) and vendored three.js r170 modules (no CDN).
- Three.js viewer: GLTFLoader + OrbitControls (azimuth + polar + zoom + pan), bounding-box auto-framing, hemisphere + directional lights, default ±40° / 6 s yaw oscillation pausing on drag and resuming after 2 s, toolbar with triangle count, auto-rotate / wireframe toggles and reset view.
- `install_glb_sidecar.sh` installer and `test_glb_viewer.sh` curl smoke test.
