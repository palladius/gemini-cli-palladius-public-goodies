# 🔵 LinkedIn Articles Cross-Posting Playbook (`references/linkedin.md`)

Operational reference for staging long-form technical posts as **LinkedIn Articles** (`https://www.linkedin.com/article/new/`) alongside companion LinkedIn feed announcements.

> [!CAUTION]
> **DRAFT-ONLY HITL GATE**: Never click **"Next" → "Publish"** on a LinkedIn Article or **"Post"** on a LinkedIn feed update. Always stop once the LinkedIn Article header shows **`Saved`**, capture a verification screenshot, and hand off the draft URL to the human author!

---

## 1. LinkedIn Article Editor (`linkedin.com/article/new/`) Constraints

| Element | LinkedIn Article Behavior | Best Practice |
| :--- | :--- | :--- |
| **Cover Image** | Dedicated top banner slot (recommended **`1920 x 1080 px`**, 16:9). | Upload local `hero.jpg` / `hero.png` via `upload_file` on the cover dropzone + set Cover Caption below it. |
| **Headline (Title)** | Plain text `textarea` (max ~100–150 chars visible cleanly). | Strip Markdown formatting; prefix `[TEST - DELETE ME]` only if testing in a throwaway draft. |
| **Body Paste (`#medium-story-body`)** | ProseMirror/Quill-based rich editor: preserves `<h2>`, `<h3>`, `<strong>`, `<em>`, `<a>`, `<ul>`, `<ol>`, `<blockquote>`, and `<pre><code>`. | Paste from `#medium-story-body` (excluding `<h1>` title and `<aside>` metadata banner). |
| **Mermaid / LaTeX / `<table>`** | **Not supported** — raw Mermaid text or flattened table cells appear. | Pre-render diagrams and tables to `.png` images before pasting. |
| **Videos & GIFs** | Supports YouTube/Vimeo embeds via `+` media menu -> *Video* -> URL; inline GIFs supported via image upload. | Replace `.mp4` references with YouTube links or uploaded GIFs. |
| **Canonical Link** | LinkedIn Articles do **not** expose a custom `<link rel="canonical">` field! | Append an explicit italic attribution line at the very top or bottom: *Originally published at [example.com/posts/slug/](https://example.com/posts/slug/).* |

---

## 2. Companion LinkedIn Feed Announcement Rules

When drafting the short promotional feed post that introduces the article:

1. **Single-Row Mentions (No Vertical `cc:` Lists)**:
   - List credited collaborators on **one single space-separated line** right after hashtags:
     `[Alice](https://linkedin.com/in/alice) [Bob](https://linkedin.com/in/bob)`
   - Never format mentions as vertical bulleted `cc:` lists.
2. **UTM Attribution**:
   - Tag outbound product/blog links with `utm_source=linkedin&utm_medium=social` (plus campaign ID if applicable), while keeping `github.com` and `medium.com` URLs clean of UTMs unless specifically desired.

---

## 3. Planned `/learn` Discovery Checklist (Phase 2)

During our first live `/browser` run on `https://www.linkedin.com/article/new/`, verify and document:
- Exact DOM selectors / `uid` patterns for Cover Image upload, Headline field, Body ProseMirror root, and the **`Saved`** status badge.
- Whether `ClipboardEvent('paste')` with `text/html` automatically fetches remote `<img src="https://...">` URLs into LinkedIn's CDN or requires explicit image upload.
- Exact steps to delete a `[TEST - DELETE ME]` draft via *Manage → Drafts → Delete*.
