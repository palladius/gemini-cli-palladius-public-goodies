---
name: publish-to-medium
description: >-
  (💛) Deterministically validate, stage, and cross-post technical blog articles to Medium and
  LinkedIn Articles as unpublished drafts via Chrome DevTools Protocol (CDP) or /browser, preserving
  canonical SEO links, auto-uploaded CDN images, and multi-line code blocks while enforcing a strict
  Human-in-the-Loop (HITL) Draft-Only gate.
compatibility: Gemini CLI, Antigravity, Jetski
metadata:
  version: 0.3.0
  author: palladius
  tags: medium, linkedin, blogging, cross-posting, seo, canonical-url, chrome-devtools, cdp, mermaid, latex
---

# 📰 Publish to Medium & LinkedIn Articles (`publish-to-medium`)

Automates the pre-flight audit and browser-assisted staging of technical articles from a primary static blog (e.g., Hugo, Astro, Jekyll) to **Medium** (`medium.com`) and **LinkedIn Articles** (`linkedin.com/article/new/`).

---

## 🛑 NON-NEGOTIABLE HITL RULE: DRAFT-ONLY (`NEVER PUBLISH`)

> **CRITICAL RED LINE**: Publishing triggers follower emails, social notifications, and public syndication.
>
> 1. **NEVER** click the final **"Publish"**, **"Publish now"**, **"Submit"**, or **"Schedule"** confirmation button on Medium or LinkedIn under any circumstances.
> 2. **ALWAYS** stop as soon as the draft status shows **`Saved`**, capture verification screenshots, and return the private draft edit URL (e.g., `https://medium.com/p/<id>/edit`) to the human author.
> 3. **Sandbox Iteration (`[TEST - DELETE ME]`)**: When testing formatting on a secondary/sandbox account, prefix the draft title with `[TEST - DELETE ME] ` and run `cleanup-test-drafts` once verification finishes.

---

## 🧭 Platform References & Bundled Scripts

Load the target platform reference before interacting with the browser:

- **Medium Stories (`medium.com`)**: Read [references/medium.md](references/medium.md) for the battle-tested single-connection CDP workflow (`cdp_medium_draft.py`), Method B native Blink Copy+Paste (auto-uploading `200 OK` images to `cdn-images-1.medium.com`) vs. Method A (`/p/import`), exact DOM selectors, Canonical URL settings, and 5-topic tagging.
- **LinkedIn Articles (`linkedin.com/article/new/`)**: Read [references/linkedin.md](references/linkedin.md) for LinkedIn's rich-text article editor, 1920x1080 cover banner requirements, code/diagram workarounds, and companion feed-post single-row `@mention` rules.
- **Zero-Dependency Scripts (`$SKILL_DIR/scripts/`)**:
  - `preflight_article.py`: Pure Python 3 stdlib pre-flight validator checking localhost/relative assets, corrupted `<pre><code>`, Mermaid/table/video/LaTeX warnings, and live HTTP `404` checks on `<img src>` and `<a href>`.
  - `render_blocks.py`: Offline-cached local rasterizer turning ```` ```mermaid ```` diagrams (3x Retina via headless Chrome + cached `mermaid.min.js`) and LaTeX math (`$$...$$` / `$...$` via 300-DPI `pdflatex` + `pdftoppm` or KaTeX) into crisp PNGs with zero external data exfiltration.
  - `cdp_medium_draft.py`: Pure Python 3 stdlib RFC 6455 WebSocket CDP stager connecting directly to the user's authenticated Chrome via `DevToolsActivePort` over a single persistent WebSocket session — auto-uploading `200 OK` remote images on paste, uploading local/un-deployed PNGs & GIFs directly via `Page.setInterceptFileChooserDialog` + `DOM.setFileInputFiles`, polling until every `data-image-id` commits to `Saved`, and verifying persistence after a full server reload.

---

## 🚦 Step 1: Deterministic Pre-Flight Gate (Before Opening Browser)

Always run the zero-dependency pre-flight validator **before** launching browser automation:

```bash
python3 "$SKILL_DIR/scripts/preflight_article.py" \
  --html path/to/out/medium/index.html \
  --canonical-url "https://example.com/posts/my-article/" \
  --platform medium \
  --check-remote
```

Add `--json` when extracting structured metadata (`title`, `canonical_url`, `topics`, `blockers`, `warnings`).

### Blocker Gates (`❌` — Fix Before Staging)
- **Zero `localhost` / `127.0.0.1` URLs** in `<img src>` or `<a href>`.
- **Zero relative `<img src>` paths** or **HTTP `404` remote images** (Medium's editor auto-uploads `200 OK` HTTPS images onto `cdn-images-1.medium.com`, whereas a single `404` image triggers `"Uh oh! Something went wrong uploading the image"`).
- **Zero unstripped placeholders** (`TODO_MEDIUM_URL`, `Note for Medium:`, leaked HTML comments, or private/internal URLs).
- **Zero corrupted `<pre><code>` tags** (e.g., Markdown italic `*` or link `[]` regexes accidentally producing `<em>` or `<a href>` inside code blocks).

### Platform Compatibility Warnings (`⚠️` — Convert or Replace)
- **HTML `<table>` elements**: Medium has zero native `<table>` support and converts every `<th>`/`<td>` cell into disconnected `<blockquote>` blocks. Convert Markdown tables into semantic `<ul><li><strong>Key</strong> — ...</li></ul>` lists or crisp PNG cards before staging.
- **Mermaid / Graphviz code blocks**: Neither Medium nor LinkedIn Articles render `mermaid` (`graph LR`, `sequenceDiagram`, `flowchart`). Pre-render diagrams to high-DPI `.png` images with captions.
- **Raw `.mp4` / `<video>` tags**: Medium strips `<video>` tags. Upload videos to YouTube (Unlisted or Public) and place the bare `https://www.youtube.com/watch?v=...` URL on its own line for native Embedly auto-embedding (animated `.gif` files `< 25 MB` at `HTTP 200` work natively as `<img>`).
- **LaTeX math (`$...$` / `$$...$$`)**: Not rendered natively on Medium or LinkedIn Articles; use Unicode math symbols for inline expressions and rendered images for multi-term equations.

---

## 🚀 Step 2: Automated Draft Staging on Authenticated Chrome (`cdp_medium_draft.py`)

Isolated automation browsers (`--enable-automation`) are blocked by Google OAuth (*"This browser or app may not be secure"*) and Cloudflare Turnstile. Always attach to the user's **already-authenticated Chrome** (`chrome://inspect/#remote-debugging` enabled once, open a dedicated `https://medium.com` tab):

```bash
# Stage compiled HTML into a saved Medium draft + set Canonical URL (single 'Allow' prompt)
python3 "$SKILL_DIR/scripts/cdp_medium_draft.py" paste-html \
  --html path/to/out/medium/index.html \
  --url "https://example.com/posts/my-article/" \
  --title-prefix "" \
  --out-dir /tmp/medium_stage_out
```

For sandbox testing on a secondary account, keep the default `--title-prefix "[TEST - DELETE ME] "` and pass `--cleanup-after` to automatically delete temporary test drafts after screenshots and JSON reports are captured.

---

## 🔄 Step 3: Canonical SEO Architecture (Bidirectional Sync)

1. **Stage Assets on Primary Blog First**: Ensure the post and all images/GIFs (`images/`, `assets/`, `demos/`) resolve `HTTP 200` on your primary blog URL.
2. **Stage Draft & Set Canonical Link**: Run `cdp_medium_draft.py paste-html` (or `import-url`), which stages the draft and sets *Story Settings → Advanced Settings → Customize Canonical Link* to your primary blog URL.
3. **Human Reviews & Publishes**: Present the saved `/p/<id>/edit` Draft URL + screenshots (`method_b_editor.png`, `method_b_settings.png`) + suggested 5 Topics (`data-topics`) to the human author to click **Publish**.
4. **Backfill Cross-Link**: Once published, record the live Medium/LinkedIn URL in the source frontmatter so the primary blog appends a *"Read this article on Medium"* footer.
