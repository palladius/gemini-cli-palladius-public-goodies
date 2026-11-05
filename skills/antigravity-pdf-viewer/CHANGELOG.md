# CHANGELOG for antigravity-pdf-viewer

## 0.1.3 (2026-11-05)
- Added cross-platform Poppler binary discovery (`findPopplerBin`) in `scripts/main.mjs` supporting macOS Homebrew (`/opt/homebrew/bin`, `/usr/local/bin`) alongside Linux `/usr/bin` for `pdftoppm`, `pdfinfo`, and `pdftotext`.

## 0.1.2 (2026-11-04)
- Bundled a self-contained `scripts/xdg-open-as` helper (with built-in Python `Local State` `--profile-directory` resolver + `chrome-for-identity` delegation) and added native `--profile-directory` fallback in `scripts/main.mjs`.
- Standardized all documentation and paths around `$SKILL_DIR/scripts/`.

## 0.1.1 (2026-11-04)
- Bundled `main.mjs` and `sidecar.json` directly inside `skills/antigravity-pdf-viewer/scripts/` alongside `install_pdf_sidecar.sh` so the skill is 100% self-contained without relying on external parent paths.

## 0.1.0 (2026-11-03)
- Initial release of `antigravity-pdf-viewer` (`sidecars/pdf-viewer/` + `skills/antigravity-pdf-viewer/`).
- Intercepts `.pdf` files in Antigravity's right-hand Aux Pane via `file_extensions: [".pdf"]`.
- Added high-DPI `pdftoppm` page rendering, giant `◀ Prev` / `▶ Next` floating page navigation buttons, Single-Page (`📖 Singola`) vs. Continuous Scroll (`📜 Continuo`) modes, keyboard arrow navigation, and `💬 Invia a Chat`.
- Added `🖨️ Apri in Chrome per Stampa` button with dynamic Chrome profile discovery (`~/.config/google-chrome/Local State`) and `xdg-open-as` integration.
