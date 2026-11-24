---
name: presentation-that-riccardo-likes
description: >-
  (💛) Use when creating, styling, auditing, or refactoring Marp, Reveal.js, Slidev, or Google Slides
  presentations for Riccardo — enforces canonical 1..N+1 deck spine (incl. hidden noir Slides Cemetery),
  native multi-shape Google Slides composability over monolithic flat images, Tri-Engine diagram routing,
  bright cutie-cartoon metaphors with floating 1-punchline text (banning 50% dark glass-capsule cards),
  garish neon-yellow (#FFFF00) A/B option pills, minimal-text editorial flow, QR 1/4-slide sizing, and PNG verification.
compatibility: "gemini-cli, antigravity, openclaudio"
metadata:
  version: "1.7.0"
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

## 15. 🟨 "Creation Is Expensive, Destruction Takes 2 Seconds" — Super-Ugly Neon-Yellow (`#FFFF00`) A/B Option Pills & Slide Graveyard

High-craft visuals take real effort to create; killing a weaker slide in Google Slides takes 2 seconds. Whenever proposing an alternative visual or layout for an existing slide:

1. **NEVER overwrite, delete, or pre-emptively `skip` a strong existing visual!** Do not decide unilaterally for the speaker.
2. **Duplicate Side-by-Side with Intentionally Garish Pure Neon-Yellow Highlighter Badges (`#FFFF00` + `#000000`)**:
   - Keep **both** candidate slides active next to each other and place an **intentionally super-ugly, unmistakable pure neon-yellow highlighter pill** (`fill: #FFFF00` / `rgb(255, 255, 0)`, `border: 1.5pt solid #000000`, text `#000000` bold `10pt`) in the top-right margin so it screams visually during review and can never be forgotten on stage:
     - Slide 1: `Option 1: <short desc>`
     - Slide 2: `Option 2: <short desc>`
3. **Park Runner-Ups in `skip: true` or the `N+1` Slides Cemetery**:
   - Let Riccardo choose visually in 2 seconds. Good runner-up slides are parked with `skip: true` (`slideProperties.isSkipped: true`) behind the end-of-deck **Slides Cemetery (`N+1`)** for future reuse; only genuinely broken drafts are permanently deleted.

---

## 16. 🏛️🪦 Canonical `1 .. N+1` Deck Spine & The Noir "Slides Cemetery"

Every presentation created for Riccardo MUST follow this deterministic slide spine:

| Slide Index | Mandatory Role | Required Elements |
|---|---|---|
| **Page `1`** | **Hero Cover** | Talk title + subtitle + colorful **`Riccardo Carlesso — Developer Advocate`** speaker tab/badge (signature style) + venue/date badge |
| **Page `2`** | **About Me (`Who Am I`)** | Authentic regional/contextual photo (100%-fit, 4 rounded corners) + clean 2-paragraph bio + 3-column tabulated social grid (vector brand icons + clickable links) |
| **Pages `3 .. N-2`** | **Core Story Slides** | Structured into clean Google-colored Chapter Break dividers (`<= 10–20` body words per content slide, rich Speaker Notes) |
| **Page `N-1`** | **Resources & Links** | Curated takeaway links paired with a **giant `>= 1/4` slide-surface QR code** (~390–420px square) pointing to the canonical resources/repo page |
| **Page `N`** | **Thank You & Q&A** | Clickable **LinkedIn, Blog (`ricc.rocks`), GitHub, X/Twitter** handles + an optional **session Feedback QR code** |
| **Page `N+1` (`hidden`)** | **🪦 Slides Cemetery** (`skip: true` / `isSkipped: true`) | **Pitch-black canvas & thick black border (`#09090B`)** + a **very dark, noir Halloween-humorous NanoBanana illustration of "dead `16:9` slides resting as tombstones in a misty gothic cemetery"** (`R.I.P.`). All parked/skipped backup slides (`N+2 .. M`, all `isSkipped: true`) live immediately after this gate! |

---

## 17. 🧩 Native Google Slides Composability ("`N` Native Pieces > `1` Monolithic Image")

### 💡 The Trap of Lazy Monolithic PNGs
Baking an entire multi-card comparison, board-game progression, or bar chart into **one single NanoBanana or rasterized PNG** looks pretty on first render, **but locks the human speaker out of editing**: clicking the slide in Google Slides only lets Riccardo edit the `H1` title — changing a single year, fixing a `10^k` exponent, or adding a 4th column becomes impossible!

### 🚀 The Iron Rule: Compose from `N` Native Google Slides Elements
Whenever targeting **Google Slides**, **ALWAYS prefer `N` native editable shapes over 1 monolithic image**:
1. **Cards, Badges, Bullets, Code Blocks & Bar Charts = 100% Native Shapes & Text**:
   - Build cards as `ROUND_RECTANGLE` shapes, year/category pills as native shapes, body text/captions/code as native `TEXT_BOX` elements (`Roboto` / `Roboto Mono`), connector arrows as native `LINE`s (`END_ARROW`), and quantitative comparison bars (e.g., aligned `~10^5`, `~10^20`, `~10^47`, `~10^170` log bars) as native colored `ROUND_RECTANGLE` bars + editable `TEXT_BOX` labels!
2. **Isolate Raster / NanoBanana Images Strictly to Pure Visual Art**:
   - Use images **only** for the irreducible visual illustrations inside each native card (e.g., 4 separate small square PNGs for the Tic-Tac-Toe grid, Checkers board, Chess board, and Go board — surrounded by native editable Google Slides cards, headers, captions, and bars).
3. **Exception Check**:
   - Only embed a full-width rendered diagram PNG when exact topological Bezier routing (`M × N` 16-arrow spaghetti) or pixel-locked multi-pane diagramming genuinely cannot be expressed cleanly with native Google Slides shapes — and even then, keep surrounding callouts, titles, and annotations native whenever possible.

---

## 18. 🚫🖤➡️🧸✨ Anti-Pattern Ban: No "50% Dark Glass-Capsule" Over Moody Sci-Fi Stock — Use Bright Cutie-Cartoon Metaphors + Floating 1-Punchline

### 💀 The Banned Anti-Pattern (`GLASS_CAPSULE` + Dark Stock Art)
Never build "WOW / Hook / Intuition" slides using a **dark, moody, generic sci-fi image** covered on the left half by a **50%-width translucent dark rounded rectangle (`GLASS_CAPSULE`)** stuffed with 4 stacked text layers (`ALL-CAPS OVER-TITLE` + `H1 Title` + `Paragraph` + `Colored Footer Chip`):
1. **Why Dark Sci-Fi Art Fails**: 90% of dark abstract renders (glowing glass shards, cybernetic corridors, neon brains) are dreary and **literally disconnected from the spoken metaphor** (e.g., shattered glass with a key tells the audience zero about *agent harnesses* or *context rot*).
2. **Why the 50% Dark Card Fails**: It blocks half of the artwork, wastes massive vertical space inside a heavy dark box, and forces the audience's eye through 4 competing text styles that become nearly unreadable from row 5.

### 🚀 The Required Replacement: Bright Cutie-Cartoon Metaphor + Floating 1-Punchline
1. **Bright, Cutie, Cartoony Literal Metaphor (`Right 55-60%`, Seamless Warm/Light Canvas)**:
   - Illustrate the **exact concrete concept being spoken** in a bright, warm, joyful 3D/editorial cartoon style on a seamless cream/pastel/sky background (`#FAF8F5` / `#F6FAFF`) whose left `40-45%` is naturally open and uncluttered:
     - *Talking about harnesses & context rot?* Show a cute robot **literally wearing a yellow climbing/toolbelt harness** dizzy behind a mountain of paper scrolls with a golden key buried in the middle, next to its happy twin holding 3 tidy cards!
     - *Talking about cutoff & hallucination?* Show a cute robot student at a school desk with a **padlocked policy book + calendar** painting a rainbow unicorn castle mirage in its speech bubble!
     - *Talking about 5:00 AM memory dreaming?* Show a sleeping robot in a nightcap at Alpine dawn while tiny helper-sprites sweep crumpled log papers with brooms into clean color-coded wiki binders!
2. **Zero 50% Card Box — Float Text Directly Over the Image**:
   - Place **1 bold punchline (`"frase ad effetto"`, `24-28pt` bold `#0F172A`, e.g., `"A harness is only as good as its own context"`)** and **AT MOST 1 short supporting sentence (`12.5-14pt` `#334155`, `<= 14` words)** floating directly over the clean open zone of the image — **ZERO `GLASS_CAPSULE` rectangle, ZERO `ALL-CAPS` eyebrow, ZERO bottom colored chip!**
   - *(Even on intentional dark-sky or retro-CRT slides like a 1983 Cart-Pole GIF, float ONLY the crisp white punchline + 1 short sentence directly on the background — never wrap them in a 50% card box!)*
3. **Need to Open a New Section? Use a Real Chapter Divider**:
   - Never overload a hook slide with section-header eyebrows (`CHAPTER 3 | ...`). If a new chapter is starting, insert a dedicated full-color **Chapter Break** slide beforehand.

---

## 19. 🚦🧩👵 Anti-Wall-of-Tabs, Semantic Traffic-Light Colors & "70-Year-Old Mom" Clarity

### 1. Split Dense Tab Grids (`6-8` Boxes -> `1/N .. N/N` Card + Visual Series)
- **Never cram 6 to 8 text boxes or 2 to 3 text-only columns onto one slide.** When an audience faces an 8-box grid of buzzwords, comprehension drops to zero.
- **Split into a uniform `1/2..2/2` or `1/3..3/3` sequence**: Every slide in a multi-part mini-series MUST share the exact same clean two-column geometry (`1 semantic-colored card with <= 3 short points` + `1 concrete visual, UI mockup, or real-world table`), e.g.:
  - Instead of an abstract *"AI Inventory"* box, show a **real, native-editable 4-row Enterprise AI Inventory table** (`Gemini`, `OpenAI`, `Apertus` open weights, `Gemma 4`) with concrete columns (`Model | Use Case | Human Owner | Safety Gate`).

### 2. Semantic Traffic-Light Color Law (Never Cycle Colors Arbitrarily!)
Never rotate `[Blue, Red, Yellow, Green]` mechanically across neutral tabs (which accidentally colors positive governance controls Red or colors a *"Green Zone"* Blue!):
- **Red (`#DC2626` / `#FEF2F2`)** = **BAD / DANGER / BROKEN / ATTACK / FORBIDDEN / RED ZONE** *(plus literal flag colors such as the Swiss flag)*. Never use Red for neutral or positive governance steps, and ALWAYS color the *"broken / attack / anti-pattern"* card Red!
- **Green (`#16A34A` / `#F0FDF4`)** = **GOOD / SAFE / THE FIX / AIR-GAPPED / GREEN ZONE**. Always color the *"safe / cured / target"* card Green!
- **Amber / Yellow (`#D97706` / `#FFFBEB`)** = **CAUTION / REGULATED / HIGH-RISK / YELLOW ZONE**.
- **Blue / Teal (`#1A73E8` / `#0D9488`)** = **NEUTRAL CLOUD ARCHITECTURE / REFERENCE PILLARS**.

### 3. Plain-English "70-Year-Old Mom" Test, Acronym Hygiene & `Roboto Mono` Pills
1. **Zero Unexplained 3-Letter Acronyms on Screen**:
   - Never drop opaque acronyms (`ZDR`, `CMEK`, `EFZ`, `FH`, `VES`) without immediate plain-English meaning on first sight (e.g., **`Zero Data Retention (ZDR)`** = *"zero logs saved to disk; wiped from RAM right after reply"*). Move regional or niche acronyms strictly to a **Speaker Notes Glossary**.
2. **Explain Regulation by Human Consequence (`Month + Year` Only)**:
   - Frame legal rules so a smart non-engineer (like your 70-year-old mom!) gets them in 10 seconds: *"Brussels baptized life-changing AI decisions — job CVs, bank loans, health/life insurance, school grades — as High-Risk -> allowed ONLY with bias audits and human sign-off."*
   - Use **`Month + Year`** (`Feb 2025`, `Aug 2026`, `Dec 2027`) on slides — strip noisy ISO day strings (`2025-02-02`) — and attach clickable primary links to every statutory rule, RFC (`RFC 8693`), and cloud product (`Google Gemini Enterprise`, `Microsoft 365 Copilot`, `Amazon Q Business`).
3. **Monospace Code Pills for "Robot Words"**:
   - Format technical tokens, token claims, CLI paths, API flags, and math formulas (`sub=alice`, `act=claims-bot`, `~/.config`, `thinking_level`, `if/else`, `0.95^20`) in **`Roboto Mono` with a subtle pill background** so code identifiers stand out cleanly from English prose.
4. **Always Current Model Names (`Gemma 4`, Never `Gemma 3`)**:
   - Audit slides and Speaker Notes so deprecated open-weight generations (`Gemma 3`) never appear when teaching modern 2026 stacks (`Gemma 4`, `Apertus`).





