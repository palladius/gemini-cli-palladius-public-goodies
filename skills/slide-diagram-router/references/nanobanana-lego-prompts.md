# Engine 1 Reference: "Physical Lego" Cloud Architecture Prompts & Tournament Rubric

Use **Engine 1** (`gemini-3-pro-image` / `imagen` with adversarial selection) when a slide needs an architecture pipeline that fuses **tangible physical objects** (PDF sheets in a storage bucket, stacked database tables, green ACL padlock, GPU chip, cited answer bubble) with cloud blocks on a pure `#FFFFFF` slide canvas.

---

## 1. Proven Prompt Template (`~16:9` / `~2.2:1` Clean White Strip)

```text
Clean flat vector-style cloud architecture infographic on a pure solid white (#FFFFFF) background,
designed for an executive keynote slide. No outer border, no dark frame, no drop-shadow card.

Single left-to-right horizontal pipeline with 6 crisp visual stages connected by short bold black arrows:
1. "GCS Bucket": blue cloud storage bucket overflowing with tilted red-and-white "PDF" document pages.
2. "Cloud Run OCR": blue double-chevron compute icon splitting scanned pages into clean text sheets.
3. "Embeddings": neural dot-matrix funnel turning text into 4 colorful horizontal vector bars.
4. "AlloyDB ScaNN + ACL Table": stacked colorful vector index tables above a blue "SQL" cube plus a green table stamped with a white padlock icon.
5. "GPU Reranker": grey silicon microchip labeled "GPU" with pins on all four sides.
6. "Gemini Answer": clean light-grey chat bubble with a 4-point blue-pink sparkle and "[1] [2]" citation tags.

Typography rules: crisp sans-serif dark-slate (#0F172A) two-line labels centered below each stage,
large legible lettering, zero paragraphs, zero filler badges, generous white margin around the strip.
```

---

## 2. Mandatory Multi-Candidate Tournament (`N >= 4`) & Vision Judge

Single-shot image generation routinely introduces subtle spelling errors (`ScaNN` -> `ScaMN`, `AlloyDB` -> `AlloyBD`) or grey vignettes. Always generate **at least 4 candidates** (`N = 4..8`, or `N = 20` for flagship hero diagrams) into `/tmp/` and inspect every candidate with a multimodal vision pass against these 5 gates:

| Gate | Pass Criterion | Instant Reject Trigger |
|---|---|---|
| **1. Pure `#FFFFFF` Canvas** | Seamless `#FFFFFF` background that melts into a light slide | Grey/cream box, `#0F172A` dark frame, or fake slide chrome |
| **2. Exact Label Spelling** | Every technical noun (`OCR`, `ScaNN`, `ACL`, `GPU`, `[1] [2]`) is 100% letter-accurate | Any garbled glyph, duplicate word, or gibberish micro-text |
| **3. Physical + Lego Fusion** | Tangible objects (PDFs, lock, chip) visually explain *what happens* at each hop | Generic identical blue rectangles with text labels only |
| **4. Monotonic Arrow Flow** | Short, unmistakable left-to-right (`→`) progression | Backwards, disconnected, or spaghetti arrows |
| **5. Projector Legibility** | Compact horizontal band (`~2.2:1`), 5–7 stages max, large labels | Tiny 8pt sub-captions or >9 cramped stages |
