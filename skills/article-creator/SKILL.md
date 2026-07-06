---
name: article-creator
description: (🥑) Expert guide for authoring, building, testing, and publishing technical articles to ricc.rocks and Medium.
version: 1.0
tags: devrel, article, publishing, ricc.rocks, medium
---

# 🥑 Article Creator & Publisher Workflow

This skill guides the preparation, compilation, validation, and post-publication steps for articles targeted to **ricc.rocks** and **Medium**.

> [!NOTE]
> For **Riccardo**, new articles and drafts should always be initialized and managed under the root articles directory: [work/articles/](file:///usr/local/google/home/ricc/git/ricclife-with-gemini-pvt/work/articles/) (which is the parent folder relative to individual article projects).

## 📐 Authoring & Pipeline Rules

1.  **Source of Truth**: Always edit `ARTICLE.md` only. Never manually edit files inside the generated `out/` or `ricc.rocks/` directories, as they are overwritten by `build.py`.
2.  **Image Notation**: Write standard Markdown images: `![Caption](local-image.png)`. The build script translates these to Hugo image shortcodes for `ricc.rocks` and absolute URLs for Medium.
3.  **Cross-Article Links**: Write cross-article links using their full `https://ricc.rocks/...` absolute URLs in `ARTICLE.md`. The build script translates them to root-relative paths for `ricc.rocks` while preserving absolute links for Medium.

## 🚀 Publishing Checklist & Steps

### Step 1: Pre-Publishing Compilation & Review
Before finalizing, compile the article assets and check for spelling/readability:
1.  **Readability & Slop Check**: Run `speedgrapher` linter checks on `ARTICLE.md`:
    *   Target Gunning Fog Index: **12.0 - 15.0** (Optimal).
    *   Target Slop Score: **< 40%** (Low lexical slop/AI clichés).
2.  **Spelling Whitelist**: Ensure any technical terms, names, or jargon are whitelisted in `speedgrapher.json`.
3.  **Run Build**: Compile Dot diagrams and target formats:
    ```bash
    just build
    ```

### Step 2: Local Staging & Testing
Verify that generated HTML builds correctly and links are functional:
1.  Run the tests to check for broken links and metadata errors:
    ```bash
    just test-ricc-rocks-articles
    ```
2.  Inspect output folder contents:
    *   `out/ricc.rocks/index.md` (Hugo compatible output).
    *   `out/medium/article.md` (Clean Markdown copy for Medium).
    *   `out/apps-portfolio/` (Copy of index & assets for the portfolio).

### Step 3: Medium Manual Upload (One-time)
1.  Open the Medium editor and paste the clean markdown from `out/medium/article.md`.
2.  **CRITICAL SEO STEP**: Open Medium Story Settings -> Advanced Settings -> **Canonical URL**.
    *   Set the Canonical URL to: `https://ricc.rocks/en/posts/technology/<SLUG>/`
3.  Publish the article on Medium.
4.  Copy the final published Medium URL.

### Step 4: Post-Publishing Canonical Sync
1.  Update the frontmatter of `ARTICLE.md` by setting `canonicalURL: <Medium_URL>`.
2.  Re-run `just build`. This auto-appends the italic *Originally published at...* footer to the `ricc.rocks` output file.
3.  Commit and push to `ricc.rocks` repository to trigger deployment.

### Step 5: Portfolio & Social Promotion
1.  Run the `add-to-portfolio-app` skill to register this new post in `~/git/vibecoding/apps-portfolio`.
2.  Update the `my-sessions-and-bio` repository listings.
3.  Draft and schedule social announcements on LinkedIn, Bluesky, and Twitter using Buffer.
