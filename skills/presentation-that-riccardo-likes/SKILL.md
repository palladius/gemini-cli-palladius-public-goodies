---
name: presentation-that-riccardo-likes
description: >-
  (💛) Best practices, styling conventions, Marp configurations, QR code 1/4-slide sizing rules, and multimedia embedding patterns for high-impact presentations tailored to Riccardo's preferences.
compatibility: "gemini-cli, antigravity, openclaw"
metadata:
  version: "1.0.0"
---

# Presentations That Riccardo Likes 📽️🦖🦞

A curated guide to crafting engaging, interactive, and visually stunning slide decks using **Marp Markdown**, high-fidelity animations, and multimedia automation.

---

## 1. 🎥 Video Embedding: Eliminating Ugly Frames & Controlling Playback

### 💡 The Problem: The 0.0s White Keyframe
When embedding HTML5 `<video>` tags in Marp slides without an explicit `poster` image, modern browsers default to rendering the frame at timestamp `0.0s`. Because most screen captures, screencasts, and animations start with an initial white canvas or fade-in transition, the slide displays an ugly blank white rectangle before the user clicks play.

### 🚀 The Solution: Media Fragments URI (`#t=start[,end]`)
Append a media fragment timestamp directly to the video source path:
```html
<video src="../images/lobby_journal_sebi_molo.mp4#t=0.5" controls style="width: 100%; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.15);"></video>
```

### 🛑 Videos Should Play Only Once (No `loop`!)
- **Avoid Infinite Loops**: Never include the `loop` attribute on presentation videos unless the clip is an intentional, silent ambient background animation.
- **Presenter Focus**: Videos (especially clips with audio or punchy quotes) that loop continuously create visual and auditory distraction while the speaker is talking or answering audience questions.
- **Clean Halt**: Omit `loop` so the video plays through once and naturally halts on its final frame.
- **Time Clipping via Fragments (`#t=start,end`)**: Use HTML5 Media Fragments URI to clip playback windows (e.g. `#t=4,8` to play from 4s to 8s, or `#t=4.5` to start at 4.5s and play to the end).

---

## 2. 🎨 Visual Hierarchy & Layout Principles

### Side-by-Side Flex Layouts (Media + Key Takeaways)
Always pair visual media with punchy bullet points rather than plain walls of text:

```html
<div style="display: flex; gap: 24px; align-items: center; justify-content: center; margin-top: 10px;">
  <div style="flex: 1.2; text-align: center;">
    <video src="../images/my_animation.mp4#t=0.5" controls style="width: 100%; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.15);"></video>
  </div>
  <div style="flex: 0.8; font-size: 0.75em;">
    <ul style="line-height: 1.6;">
      <li><strong>Takeaway 1:</strong> Strong opening metric or summary.</li>
      <li><strong>Takeaway 2:</strong> Technical detail or agent workflow.</li>
      <li><strong>Takeaway 3:</strong> Production outcome.</li>
    </ul>
  </div>
</div>
```

### Dark Title & Section Breaks
- Use `<!-- _class: dark -->` on opening titles and major milestone transitions.
- Complement with subtle background radial gradients for high-contrast presentation screens.

---

## 3. ⌨️ Interactive Video Playback via SPACE Bar

### 💡 The Problem with Default Marp Key Handlers
Marp uses **Bespoke.js**, which registers a global `document.addEventListener('keydown', ...)` handler that automatically advances to the next slide on `Space` (`t.next()`). Without interception, pressing `SPACE` on a video slide immediately skips past the slide without playing the video!

### 🚀 The Solution: Global Capturing Listener in `000_header.md`
Attach a key listener in the **capture phase** (`{ capture: true }`), which fires *before* Bespoke's bubbling listener. If the active slide has a paused video, it intercepts the event and triggers playback.

### 🎮 Unified Presenter Experience:
1. **On Normal Slides**: `SPACE` advances to the next slide.
2. **On Interactive Reveal Slides** (e.g. Bananification): 1st `SPACE` triggers the reveal animation; 2nd `SPACE` advances slide.
3. **On Video Slides**: 1st `SPACE` plays the video; 2nd `SPACE` advances slide.

---

## 4. 📅 Carlessian Date & Timeline Badges (`.time-badge`)

### 💡 Purpose
For chronological stories, roadmaps, and milestone slides, anchor the narrative in time with a floating top-right badge. This gives the audience immediate temporal context without cluttering the main slide title.

### 🎨 HTML & CSS Pattern
Define the badge markup at the very top of the slide markdown (before the `h1`).
**Rule**: The badge must ONLY contain an emoji and an ISO date (or date range). No word labels, step numbers, or city names are permitted!

```html
<!-- Canonical Date Badge -->
<div class="time-badge">🦞 2026-02-14</div>

<!-- Country / Milestone Badge -->
<div class="time-badge">🇿🇦 2026-02-09</div>
<div class="time-badge">🇨🇭 2026-02-05</div>

<!-- Date Range Badge -->
<div class="time-badge">⏱️ 2026-01-27 – 2026-02-28</div>
```

---

## 5. 📸 Antigravity Visual Feedback Loop (Live Slide Image Artifacts)

### 💡 The Rule: Always Render & Inspect What You Edit
Never guess what a layout or CSS change will look like in Marp. Whenever you edit or tweak any slide file:

1. **Render the Single Slide to PNG (Blazing Fast ⚡)**:
   ```bash
   just render-single-page-as-png slides/deck-en/part1_story/080_openclaw_intro.md
   just render-png 080
   ```
2. **Inspect the Visual Output**:
   View the generated image file (`slides/out/080_openclaw_intro.png`) to immediately verify font sizes, line wrapping, element alignment, and vertical overflows beyond 720px.

---

## 6. ⏭️ Google Slides Style Slide Skipping (`skip: true`)

Place a standard YAML frontmatter block at the very top of any modular slide file (`slides/deck-en/...`):

```yaml
---
skip: true
---
```

---

## 7. 📱 QR Code Sizing & Scannability: The 1/4 Slide Surface Rule

### 📐 The Rule of Thumb: Minimum 1/4 of the Slide Surface
For a QR code to be reliably readable by audience smartphones from 10–25+ meters away:
- **Surface Area Requirement**: Primary CTA QR codes must occupy **at least 1/4 of the total slide surface** (~25% area, ~390px–420px square on a 1280×720 canvas).
- **Source Resolution**: Ensure the source image is at least **600 × 600 px** (or vector SVG) so scaling remains razor-sharp with no pixelation.

---

## 8. 🤫 The Golden Rule of Slide Text: Minimal Text, Maximum Visual Impact (Max 10 Words)

### 💡 The Core Principle: People Read or People Listen
If a slide has a lot of text, attendees will **read the text instead of listening to the speaker**!
1. **Max 10 Words per Slide**: Keep on-screen words to a strict minimum (aim for <= 10 words, excluding clean titles or concise tabular keywords).
2. **Keywords as Speaker Reminders**: Text on screen serves solely as punchy keywords for the speaker, not complete sentences.
3. **Structured Formats**: Prefer badges, metric cards, and synthetic tables over bulleted sentences.
4. **All Context Belongs in Speaker Notes**: Explanations, backstories, and technical details go into markdown speaker notes (`<!-- Speaker notes ... -->`).
