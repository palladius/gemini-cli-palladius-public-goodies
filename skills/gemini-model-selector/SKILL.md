---
name: gemini-model-selector
description: >-
  💛 Provides current recommendations for Gemini, Nano Banana, Omni, Veo, and Lyria model selection, Twitter-sized capability descriptions, deprecation alerts, and migration paths. Updated November 2026.
compatibility: Antigravity / Gemini CLI
metadata:
  version: 0.3.0
  tags: gemini, models, argon, nano-banana, omni, veo, lyria
---

# 💛 Gemini Model Selector (November 2026)

This skill provides current, recommended model IDs for **Gemini 4**, **Nano Banana 2.1**, **Omni 1.1 Flash**, **Veo**, and **Lyria 3.5**, along with punchy Twitter-sized descriptions of what each model actually does, API endpoint requirements (`client.interactions` vs `generateContent`), and deprecation alerts.

*Last Updated: 05 November 2026*

## Recommended Models & What They Actually Do

| Task Type | Recommended Model | 📅 Released | 🐦 What It Actually Does (`<=280B` Twitter Description) |
| :--- | :--- | :---: | :--- |
| **Complex Reasoning / Coding / Research (Flagship)** | `gemini-4-argon` | `2026-10-13` | Flagship 1M-ctx reasoning, coding & research powerhouse (65k out). Replaces `3.1-pro` for complex architecture, STEM, and multi-step agentic workflows. |
| **Balanced Agentic & Multimodal (Default)** | `gemini-3.8-flash` | `2026-09-02` | Default 1M-ctx fast workhorse (65k out) balancing thinking, multimodal understanding, and low-latency agentic tool calling. |
| **High-Throughput / Low-Cost** | `gemini-3.5-flash-lite` | `2026-07-21` | Fastest, lowest-cost 1M-ctx 3.5 model for high-throughput batch classification, extraction & routing (`gemini-3.1-flash-lite` for ultra-lightweight). |
| **Image Generation & Editing (Default)** | `gemini-nano-banana-2.1` | `2026-10-06` | **Nano Banana 2.1**: flagship high-efficiency 1K/2K/4K image generator & conversational editor supporting multi-image fusion with up to 14 reference images. |
| **Image Generation (Pro / Lite)** | `gemini-3-pro-image` / `gemini-3.1-flash-lite-image` | `2026-05-28` / `2026-06-30` | **Nano Banana Pro** (studio photorealism & typography) and **Nano Banana 2 Lite** (ultra-fast general image generation & editing). |
| **Video Generation, Editing & 40s Extension** | `gemini-omni-1.1-flash` | `2026-08-27` | **Omni Flash** video+audio generator & editor: text/image-to-video, first/last frame transitions, object add/remove, AR zoom & 40s extensions via `client.interactions` API. |
| **Studio Text-to-Speech & Voice Design** | `gemini-3.8-flash-tts` | `2026-09-22` | Expressive studio TTS: Voice Design from text prompts, Voice Replication, dual-speaker podcasts, backchanneling (`\|mhm\|`, `\|yeah\|`) & vocal bursts (`<laugh>`, `<gasp>`). |
| **High-Volume Fast TTS** | `gemini-3.8-flash-lite-tts` | `2026-09-22` | Ultra-fast, low-cost TTS for high-volume voice agents, article reading, IVR, global dubbing, and accessibility screen readers. |
| **Speech-to-Text (Static / Live)** | `gemini-3.5-transcribe` / `gemini-3.5-transcribe-live` | `2026-08-26` | Dedicated high-speed ASR with smart/verbatim modes (`3.5-transcribe`) and real-time streaming speech translation (`3.5-transcribe-live`). |
| **Live Bidi Audio & Video** | `gemini-3.8-live` / `gemini-3.8-live-extended-thinking` | `2026-09-15` | Low-latency Live API (`bidiGenerateContent`) conversation (`3.8-live`) and "Thinker-Talker" Live model for complex reasoning + multi-step tool use (`extended-thinking`). |
| **Music Generation (30s Clips vs 2–3m Songs)** | `lyria-3.5` (`lyria-3-clip-preview` / `lyria-3-pro-preview`) | `2026-09-03` | **Lyria** music & vocals family: `lyria-3-clip-preview` generates **30s clips**, while `lyria-3-pro-preview` / `lyria-3.5` generate **full 2–3 min songs** with lyrics & vocals. |
| **Multimodal & Text Embeddings** | `gemini-embedding-2` / `gemini-embedding-001` | `2026-04-22` | `gemini-embedding-2` maps text, images, video, audio & PDFs into one shared vector space; `gemini-embedding-001` is text-only. |
| **Managed Agents (`client.interactions`)** | `antigravity-preview-09-2026` / `deep-research-preview-04-2026` | `2026-09-17` / `2026-04-21` | Managed sandboxed Linux coding agent (`antigravity-preview-09-2026`) and autonomous web synthesis agent (`deep-research-*`) via `client.interactions.create()`. |
| **Open Weights (Gemma 4)** | `gemma-4-31b-it` / `gemma-4-26b-a4b-it` | `2026-04-02` | Gemma 4 31B Dense and 26B Mixture-of-Experts (only 4B active parameters per token). |

## Source of Truth YAML & Live Discovery CLI

All release dates and `<280B` `twitter_description` entries live in the public YAML catalog:
- **YAML Catalog**: `~/git/gemini-tools/etc/gemini_models.yaml` (`github.com/palladius/gemini-tools`)
- **CLI**: `~/git/gemini-tools/bin/list-gemini-models.py` (symlinked at `~/git/gic/bin/gemini-list-models.py`)

```bash
# Show the 10 newest models with release dates and Twitter descriptions
gemini-list-models.py --full --by-date -n 10

# Show AI self-healing instructions for populating UNKNOWN (*) models in etc/gemini_models.yaml
gemini-list-models.py --ai-help
```

## Deprecation Alerts (Action Required)

- **Legacy Gemini 2.5 / 2.0 / 1.5**: Models like `gemini-2.5-*`, `gemini-2.0-*`, and `gemini-1.5-*` are **legacy and deprecated**. Replace with `gemini-3.8-flash` (or `gemini-4-argon` for complex reasoning).
- **Legacy Image Models (`gemini-3.1-flash-image`, `gemini-3.1-flash-image-preview`, `gemini-2.5-flash-image`)**: Replaced by `gemini-nano-banana-2.1` and `gemini-3.1-flash-lite-image`.
- **Veo 2 & Veo 3 (`veo-2.0-generate-001`, `veo-3.0-generate-001`, `veo-3.0-fast-generate-001`)**: Deprecated (cutoff June 30, 2026). Migrate to `gemini-omni-1.1-flash` or `veo-3.1-lite-generate-preview`.
