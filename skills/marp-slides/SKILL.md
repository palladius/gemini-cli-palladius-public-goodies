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
