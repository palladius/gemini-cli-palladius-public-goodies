---
name: presentation-that-riccardo-likes
description: >-
  (💛) Use when creating, styling, auditing, or refactoring Marp, Reveal.js, Slidev, or Google Slides
  presentations for Riccardo — enforces minimal-text editorial flow, Tri-Engine diagram routing,
  light-yellow A/B option pills, 100%-fit rounded visuals without dead frames or FIG pills,
  tabulated clickable brand icons, whisper-thin footers, QR 1/4-slide sizing, and live PNG verification.
compatibility: "gemini-cli, antigravity, openclaudio"
metadata:
  version: "1.4.0"
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

---

## 9. 🧊 Multi-Event Presentations: Crystallize Past Events & Bump Future Targets (`+0.01`)

When a presentation deck serves multiple conferences/events (e.g., `warsaw` vs `milan`, or `modena` vs `campobasso`):
1. **Never Modify a Past Event's Deck**: Once a conference has taken place, its compiled deck MUST be crystallized and archived (`slides/archive/<event>-vX.Y.Z.en.md`) without further modifications.
2. **Scope New Slides to Future Targets Only**: Add new slides using target-specific suffixes (e.g., `195_key_takeaways.milan.md`) and increment the future target's version badge by `+0.01`.

---

## 10. 🎨 Harmonized Image Captions & Syntax-Highlighted Inline JSON

1. **Image Caption & Acrostic Boxes (No "Christmas Tree" Colors)**:
   - Omit decorative emojis inside compact caption boxes.
   - Use a 3-tone harmonized palette (`#facc15` warm gold accents, `#94a3b8` muted slate connectors, `#f8fafc` crisp white keywords) with `white-space: nowrap` to prevent orphan wraps.
2. **Single-Line Syntax-Highlighted JSON Snippets**:
   - Strip redundant keys, use native JSON floats/booleans, and colorize tokens on a single `nowrap` line.

---

## 11. ✨ Clean Editorial Slide Flow (Anti-Tax-Form Contract)

Rigid multi-box templates with double horizontal black rules, numbered prefixes, and dead empty gaps kill visual flow. Every content slide follows this 3-zone layout contract:

1. **Header Zone**:
   - Single-line assertive `H1` title (`22pt` bold sans-serif, zero leading decorative emojis on content slides).
   - Separated from the body by **one** whisper-faint `#e2e8f0` hairline (`0.6pt`) — never double black bars or floating top-right clock boxes (`09:10`, `11:18`).
2. **Cohesive Editorial Copy Column (`35–40%` width)**:
   - **1 to 2 (rarely 3) crisp statements** (`<= 10–20` words total) grouped near the optical vertical center (`line-height: 1.28`), with a subtle `3pt` `#1a73e8` vertical accent pill beside the architectural takeaway.
   - **Zero `01 /` or `02 /` prefixes**: Never prepend `01 /`, `02 /`, or numbered tracking tags to slide callouts.
   - **Zero invented ALL-CAPS sub-titles**: Never manufacture arbitrary uppercase headers (`ONE CONCRETE STORY`, `ENGINEERING & PASSIONS`) above single-sentence thoughts — less is more; let the prose speak directly.
   - **Zero vertical dead chasms**: Group related statements cleanly rather than stranding short sentences at the top and bottom of an empty column.
3. **Protagonist Visual Column (`60–65%` width)**:
   - **100%-Fit Cover Crop (`object-fit: cover`) + 4 Smooth Rounded Corners (`border-radius: 16px`)**: Scenic photos and illustrations fill 100% of their visual box (crop laterally or vertically to match the target ratio) with anti-aliased rounded corners — **never** float a smaller image inside a dark `#0f172a` or grey dead-space frame!
   - **Edge-Safe Diagrams**: Architecture SVGs and terminal diagrams that contain text near their borders keep their native aspect ratio directly on the clean `#fafafa` slide canvas with rounded corners and zero outer coffin box (`font-size >= 18px` inside all SVGs).
   - **Zero Visible `FIG XX` Badges**: Never display `FIG 01` / `FIG 42` pills on slides. Store unique figure IDs invisibly in code or filenames (`data-fig-id="fig_01_020"`, `slides/images/figs/fig_01_020_*.svg`) for multi-agent pinpointing, and render at most a single whisper-quiet italic caption (`7.5pt`, `#94a3b8`, right-aligned) below the image.

| Common Agent Rationalization | Why It Fails Riccardo's Bar | Required Fix |
|---|---|---|
| *"Adding `01 / PROBLEM` and `02 / FIX` gives structure"* | Turns a 12-word slide into a rigid tax form that doesn't flow | Remove numbered kickers and arbitrary ALL-CAPS headers; use natural bold lead-ins + a subtle `3pt` vertical accent bar |
| *"Containing a `1:1` or `16:9` photo inside a `#0f172a` frame avoids cropping"* | Leaves ugly dead dark/grey bars around the image | Crop scenic photos (`object-fit: cover` / `ImageOps.fit`) to 100% of the visual box and round all 4 corners |
| *"Visible `FIG 03` pills help reference figures"* | Visual clutter for a live audience | Hide `fig_XX_YYY` in filenames / `data-fig-id` attributes; show only the clean caption text |

---

## 12. 🧑‍💻 "Who Am I" / Speaker Bio Slide Contract

1. **Authentic Location Photo (Right Column, 100% Cover-Fit + 4 Rounded Corners)**:
   - Use a real, high-resolution personal photo contextualized to the region/audience (e.g., cycling in front of a local landmark), cropped edge-to-edge with 4 smooth rounded corners — no overlapping stickers or dark frames.
2. **Clean 2-Paragraph Bio (Top-Left, Zero Headers, Zero Emoji Soup)**:
   - Two concise, human paragraphs (`11.2pt–12pt`, `line-height: 1.22`) without `ENGINEERING & PASSIONS` headers or inline emoji clutter (`🥑`, `🎹`, `🏊🏻🏃🚴🏿`).
3. **3-Column Tabulated Social Grid (Bottom-Left, Vector Brand Icons + Real Hyperlinks)**:
   - Below a faint `#e2e8f0` separator line, align social profiles in a strict 3-column grid:
     - **Col 1 (`18pt × 18pt`)**: Official vector brand icon (`LinkedIn`, `GitHub`, `X`, `Globe`) — never cartoon emojis (`🐦`, `🐙`, `💼`, `🌐`).
     - **Col 2 (`10.5pt`, `#64748b`)**: Clean platform label (`LinkedIn`, `GitHub`, `X / Twitter`, `Web & Blog`).
     - **Col 3 (`10.5pt` bold `#1a73e8`, single line, no underline)**: Real clickable hyperlink (`linkedin.com/in/riccardocarlesso`, `github.com/palladius`, `@SREccardo`, `ricc.rocks`) attached to **both** the text and the brand icon.

---

## 13. 🪶 Whisper-Thin Proportional Footer & In-Place Google Slides Comments

1. **Whisper-Thin Footer (`DD Mon YYYY, Venue  |  XX/YY`)**:
   - Right-hand metadata includes date, venue, and compact `XX/YY` slide counter: `27 Nov 2026, Rotkreuz  |  02/51`.
   - Styled in **proportional sans-serif (`Google Sans` / `Inter` — NEVER monospaced!)**, ultra-small (`7.0pt`), thin/regular weight (`bold: false`), muted slate (`#94a3b8`) so it stays virtually invisible on stage unless inspected or printed.
2. **Actioning Google Slides Comments In-Place**:
   - When a stakeholder leaves comments directly on Google Slides, read comments with `includeComments: true` and **never** run destructive slide-replacement (`deleteObject` on slide pages), which orphans comment threads.
   - Patch shapes and images **in-place** (`deleteText` + `insertText` + `updateTextStyle` + `updatePageElementTransform` + `replaceImage`, or set `NOT_RENDERED` on retired shapes holding comment anchors), visually verify rendered `LARGE` PNG thumbnails, and reply directly to each comment thread.

---

## 14. 🧭 Tri-Engine Slide Diagram Routing (`slide-diagram-router`)

**REQUIRED SUB-SKILL:** Load `slide-diagram-router` whenever building or replacing technical diagrams on slides. Route each visual to the engine that matches its cognitive job:

1. **Engine 1 — Generative "Physical Lego" (`gemini-3-pro-image` + `N >= 4` tournament)**:
   - Use for **cloud architecture pipelines & data flows** that fuse physical metaphors (`PDF` pages inside a bucket, stacked tables + green `ACL` padlock, `GPU` chip, `[1][2]` answer bubble) with cloud blocks on a pure `#FFFFFF` canvas *(default until `CloudArchDraw` MCP is in production)*.
2. **Engine 2 — Deterministic `2x` Retina Topological SVG (`render_slide_diagram.py --mode bipartite`)**:
   - Use for **many-icon / many-arrow connector graphs** (non-network topologies like `Before/After MCP: M × N = 16 spaghetti vs M + N = 8 hub`) requiring exact connector counts and authentic vector brand logos.
3. **Engine 3 — Custom HiDPI Multi-Tab Contrast Cards (`render_slide_diagram.py --mode multitab`)**:
   - Use for **side-by-side `1..4` column comparisons** containing verbatim monospace `SYSTEM PROMPT`s, code, or JSON (`{"name": "get_weather", "args": {"city": "ZRH"}}`), micro-step vertical arrows (`↓`), and bottom verdict pills (`font-size >= 18px`, `0` DOM overflow warnings).

---

## 15. 🟨 "Creation Is Expensive, Destruction Takes 2 Seconds" — Light-Yellow A/B Option Pills & Slide Graveyard

High-craft visuals take real effort to create; killing a weaker slide in Google Slides takes 2 seconds. Whenever proposing an alternative visual or layout for an existing slide:

1. **NEVER overwrite, delete, or pre-emptively `skip` a strong existing visual!** Do not decide unilaterally for the speaker.
2. **Duplicate Side-by-Side with Light-Yellow Highlighter Badges (`#FEF9C3` / `#F59E0B`)**:
   - Keep **both** candidate slides active next to each other and place a soft light-yellow highlighter pill (`fill: #FEF9C3`, `border: 1.5pt solid #F59E0B`, text `#78350F` bold `10pt`) in the top-right margin:
     - Slide 1: `Option 1: <short desc>`
     - Slide 2: `Option 2: <short desc>`
3. **Park Runner-Ups in `skip: true` or a Slide Graveyard**:
   - Let Riccardo choose visually in 2 seconds. Good runner-up slides are parked with `skip: true` (`slideProperties.isSkipped: true`) or moved to an end-of-deck **Slide Graveyard / Appendix** for future reuse; only genuinely broken drafts are permanently deleted.


