---
name: marp-slides
description: Best practices for authoring, editing, testing layout bounds, and rendering previews of Marp Markdown presentations. Use when creating or editing Marp slides, testing for vertical/visual overflow, or generating slide preview artifacts.
compatibility: Gemini CLI, Antigravity
metadata:
  version: 1.0.0
---

# Marp Slides Skill 📊

This skill provides directives, testing methodologies, and automation tools for authoring and maintaining presentations built with [Marp (Markdown Presentation Ecosystem)](https://marp.app/).

---

## 🎯 Core Directives

### 1. Ensure Content Fits Within Slide Boundaries (No Visual Overflow)
In 16:9 Marp presentations (`1280x720px`), content that overflows vertically (`scrollHeight > clientHeight`) will be clipped or cause ugly scrolling.

#### Authoring Rules to Avoid Overflow:
- **Font & Padding Hierarchy**: Use concise headings and keep paragraph line heights compact (`line-height: 1.35`).
- **Two-Column Flex Layouts**: When combining images/QR codes with bullet lists, use flexboxes instead of stacking vertically:
  ```html
  <div style="display: flex; gap: 24px; align-items: flex-start;">
    <div style="flex: 1;">
      <!-- Content / Bullets -->
    </div>
    <div style="text-align: center;">
      <!-- QR code or image -->
    </div>
  </div>
  ```
- **Image Dimension Constraints**: Always constrain image heights (e.g. `max-height: 280px;` or `width: 190px; height: 190px;`).
- **Callout Boxes**: Ensure callouts/highlights at the bottom have small fonts (`font-size: 0.8em;`) and minimal margins.

#### How to Test for Overflow:
1. **Visual Image Export Check**:
   Export all slides to PNG:
   ```bash
   marp <path-to-markdown> --images png --image-scale 1 --allow-local-files --html -o /tmp/slide.png
   ```
   Inspect the bottom margin of the generated `slide.XXX.png` files. If the slide number footer or callout box touches or exceeds the bottom edge, it is overflowing.
2. **Automated Headless DOM Check** (Selenium / Puppeteer):
   Measure each `<section>` in the compiled HTML:
   ```javascript
   const overflows = (sec.scrollHeight > sec.clientHeight + 2);
   ```

---

### 2. User Delight: Always Show Slide Preview Artifacts 🖼️
> 💡 **Riccardo's Law of Slides**: Whenever you create or modify Slide $N$ (e.g., Slide 3, Slide 13, etc.), **always render and present the resulting slide visual directly in an Artifact**!

Do not make the user open their browser or hunt for the file on disk. Provide immediate visual confirmation!

#### Step-by-Step Preview Flow:
1. **Render the Target Slide**:
   Use the bundled script in `$SKILL_DIR/scripts/preview_slide.sh`:
   ```bash
   $SKILL_DIR/scripts/preview_slide.sh <path-to-markdown> <slide-number> <destination-png>
   ```
   *Example:*
   ```bash
   $SKILL_DIR/scripts/preview_slide.sh slides/index.md 3 /tmp/slide-3.png
   ```

2. **Copy to Artifacts Directory**:
   Copy the rendered image into the current conversation's artifact directory:
   ```bash
   cp /tmp/slide-3.png <ARTIFACT_DIR>/slide_3_preview.png
   ```

3. **Publish the Artifact**:
   Create or update a markdown artifact (e.g. `slide_preview.md`) referencing the image:
   ```markdown
   # Slide 3 Preview

   ![Slide 3 Preview](<ARTIFACT_DIR>/slide_3_preview.png)
   ```

---

## 🛠️ CLI Flags Reference

When running `marp` directly via CLI:
- `--allow-local-files`: **Mandatory** when slides reference local assets (`images/*.png`, `.svg`). Without this flag, Marp CLI blocks local file access.
- `--html`: Enables HTML tags (`<div>`, `<style>`, `<img>`, etc.) inside the markdown document.
- `--images png`: Renders each slide into a standalone numbered image (`<name>.001.png`, `<name>.002.png`, ...).

---

## 🐛 HTML Rendering Gotchas (hard-won, Oct 2026)

These bugs were discovered the hard way during the Modena deck. Don't repeat them.

### ❌ HTML comments before block tags → Marp code-block leak

```markdown
<!-- My comment -->
<div style="...">content</div>
```

**Bug**: Marp treats `<!-- comment -->` immediately before a `<div>` as a fenced code block delimiter. The entire following HTML is rendered as escaped text (`&lt;div&gt;`) instead of HTML.

**Fix**: Remove ALL inline HTML comments from the slide body. Only the final `<!-- speaker notes -->` at the very end of the slide is safe (Marp treats it as notes).

---

### ❌ `<pre>` + `<span>` → spans leak out of the pre block

```markdown
<pre style="background:#0f172a;">
<span style="color:red;">text</span>
</pre>
```

**Bug**: Marp's Markdown parser breaks `<span>` tags inside `<pre>`, rendering them as escaped text or leaking them outside the block.

**Fix**: Use `<div>` with `font-family: monospace` + `<br/>` line breaks instead of `<pre>`. No spans needed if you set `color` on the div.

---

### ❌ `color` on `<div>` / `<p>` → Marp theme overrides it

```html
<div style="color: white;">text here</div>
```

**Bug**: Marp wraps plain text in `<p>` tags and applies its theme color (dark), overriding the parent `div`'s `color`.

**Fix**: Use `<table><tr><td style="color: white;">text</td></tr></table>`. Marp does NOT override `<td>` colors.

---

### ❌ `background: transparent` on `<td>` → inherits Marp theme white

```html
<td style="background: transparent;">...</td>
```

**Bug**: `transparent` on `<td>` inherits the Marp theme's white table background, not the parent table's dark background.

**Fix**: Use an explicit color: `background: #0f172a;` (or whatever your dark color is).

---

### ❌ `border: none` on `<td>` — Marp OVERRIDES it

**Bug**: Even `border: none !important` on `<td>` is overridden by the Marp theme's table CSS. Grey dividing lines between rows persist regardless.

**Fix**: Use the **camouflage trick** — set the border to the same color as the background:

```html
<td style="border: 2px solid #0f172a;">...</td>
```

The border exists but is invisible because it matches the dark bg. Marp cannot override a color it doesn't know about.

---

### ❌ Too much row spacing — Marp table default padding is loose

**Bug**: Default `<td>` padding in Marp tables is several pixels, making rows look spread out, not like a terminal.

**Fix**: Set `padding: 0` on every `<td>` and add `line-height: 1.5` on the `<table>`:

```html
<table style="line-height: 1.5; ...">
<tr><td style="padding: 0; ...">line 1</td></tr>
<tr><td style="padding: 0; ...">line 2</td></tr>
</table>
```

---

### ✅ Safe HTML pattern for dark code blocks in Marp (FINAL)

```html
<table style="background: #0f172a; border-radius: 10px; padding: 10px 18px;
              font-family: 'JetBrains Mono', monospace; font-size: 0.62em;
              line-height: 1.5; width: 100%; border-collapse: collapse;
              border: 1px solid #1e293b;">
<tr><td style="color: #475569; padding: 0; background: #0f172a; border: 2px solid #0f172a;"># comment</td></tr>
<tr><td style="color: #7dd3fc; padding: 0; background: #0f172a; border: 2px solid #0f172a;">KEY=<span style="color:#86efac;">value</span></td></tr>
</table>
```

✅ `border: 2px solid <same-as-bg>` (not `none`), `padding: 0`, `line-height: 1.5`, explicit bg on td, no HTML comments.

---

## 🔍 Debugging: Export a Single Slide to PNG

To visually verify a single slide without opening a browser:

```bash
cd slides/   # where node_modules/@marp-team lives
npx @marp-team/marp-cli@latest path/to/slide.md \
  --allow-local-files --html --images png --image-scale 2 \
  -o /tmp/slide_preview.png
```

Then open `/tmp/slide_preview.001.png` to see the rendered output.

> **Note**: Local images (`src="images/foo.png"`) may not resolve unless the slide is compiled from inside the `slides/` directory where relative paths match. Use this for layout/color checks, not full media checks.
