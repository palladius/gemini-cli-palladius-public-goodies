# CHANGELOG for antigravity-pdf-viewer

## 0.1.0 (2026-11-03)
- Initial release of `antigravity-pdf-viewer` (`sidecars/pdf-viewer/` + `skills/antigravity-pdf-viewer/`).
- Intercepts `.pdf` files in Antigravity's right-hand Aux Pane via `file_extensions: [".pdf"]`.
- Added high-DPI `pdftoppm` page rendering, giant `◀ Prev` / `▶ Next` floating page navigation buttons, Single-Page (`📖 Singola`) vs. Continuous Scroll (`📜 Continuo`) modes, keyboard arrow navigation, and `💬 Invia a Chat`.
- Added `🖨️ Apri in Chrome per Stampa` button with dynamic Chrome profile discovery (`~/.config/google-chrome/Local State`) and `xdg-open-as` integration.
