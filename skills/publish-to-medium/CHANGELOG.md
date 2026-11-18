# Changelog — `publish-to-medium`

## [0.4.0] - 2026-11-17
### Fixed & Hardened (Production Multi-Profile Verification)
- **Zero OS Window Focus-Stealing (`Emulation.setFocusEmulationEnabled`) + HHGTTG Desktop Toasts**: Removed all `Page.bringToFront` calls in `scripts/cdp_medium_draft.py` and switched to Chromium's `Emulation.setFocusEmulationEnabled({enabled: true})`, preventing background staging from raising Chrome under the user's fingers and capturing live keystrokes. Added cross-platform OS desktop notifications (`notify-send` / `osascript`, `--no-notify` to disable) warning the user not to touch the target Chrome window during copy/paste and releasing control with a Don't Panic / SEP-field completion toast.
- **Eliminated `1*b31hiO4ynbDLRrXWEFF4aQ.png` White Skeleton Race + Added `--prefer-local-files`**: Excluded Medium's `700x400` white loading skeleton (`1*b31hiO4ynbDLRrXWEFF4aQ.png`) from upload-completion polling so remote paste uploads never abort early, and added `--prefer-local-files` to upload all compiled local images/GIFs directly from `out/medium/` via `DOM.setFileInputFiles`.
- **Eliminated Raw DOM `p.remove()` Graf Model Corruption**: Replaced direct `.remove()` mutations inside Medium's contenteditable editor with native `Range` selection + `Backspace` (`p.graf--empty.is-selected`) across a 4-phase commit pipeline.
- **Post-Upload `<figcaption>` Hydration (`populate_all_figure_captions`)**: Automatically clicks every uploaded `<figure>` and populates `<figcaption class="imageCaption">` after async image uploads finish re-mounting `<figure>` widgets.
- **Multi-Account Safety & Complete `/settings` Automation**: Added `--expect-account <handle>`, `--delete-first <story_id>`, automatic Topics (`<= 5`), SEO Title (`<= 75` chars), SEO Description (`<= 155` chars), and 2-step `Edit canonical link` -> `Save canonical link` unlocking.

## [0.3.0] - 2026-11-16
### Added
- Added `scripts/render_blocks.py` to locally rasterize ```` ```mermaid ```` diagrams (3x Retina PNG via headless Chrome + locally cached `mermaid.min.js`) and LaTeX math (`$$...$$` display and genuine `$...$` inline formulas via 300-DPI `pdflatex` + `pdftoppm` with KaTeX fallback), never sending source text to external APIs.
- Added direct local disk upload (`upload_queued_local_assets` via CDP `Page.setInterceptFileChooserDialog` + `DOM.setFileInputFiles`) in `scripts/cdp_medium_draft.py` so newly rasterized Mermaid/Math PNGs and un-deployed local GIFs upload straight into Medium drafts during staging without requiring a prior blog deploy.
- Added `wait_for_medium_images_and_save()` + post-reload verification in `scripts/cdp_medium_draft.py` so every uploaded image's `data-image-id` is persisted to Medium's backend before navigating away.

## [0.2.0] - 2026-11-16
### Added
- Live-verified single-connection WebSocket CDP stager (`scripts/cdp_medium_draft.py`) attaching directly to authenticated Chrome via `DevToolsActivePort` (`paste-html`, `import-url`, `ab-experiment`, `cleanup-test-drafts`, `delete-story`).
- Native Blink Range `Copy` + `Paste` pipeline for Method B (`/new-story`) that triggers automatic Medium server-side image ingestion onto `cdn-images-1.medium.com` while pre-filtering HTTP `404` images into visible TODO placeholders.
- Remote HTTP status checks (`--check-remote`) for `<img src>` and `<a href>` in `scripts/preflight_article.py`.
- Documented 7 empirically verified Medium editor & DOM quirks in `references/medium.md` (including why synthetic `ClipboardEvent('paste')` causes `"Something is wrong and we cannot save your story"`, HTML `<table>` → 19 `<blockquote>`s conversion, `/p/import` `div.js-importUrl` vs. navbar Search bar, and `/p/<id>/settings` `button` selector for `Advanced Settings`).

## [0.1.0] - 2026-11-13
### Added
- Initial skill scaffold (`SKILL.md`, `references/medium.md`, `references/linkedin.md`, `scripts/preflight_article.py`) with strict Draft-Only (`NEVER PUBLISH`) HITL guardrails.
