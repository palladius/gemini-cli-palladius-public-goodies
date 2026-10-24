---
name: add-to-portfolio-app
description: >-
  (💛) Adds or syncs Talks, Keynotes, Workshops, Articles, Codelabs, Slides, and Videos in Riccardo's personal portfolio application (apps-portfolio) and companion bio repo (my-sessions-and-bio), including SQLite sync, TDD checks, default speaker images, and automated Cloud Run deployment.
compatibility: Gemini CLI, Antigravity
metadata:
  version: "0.2.0"
---
# Add to Portfolio App Skill (`apps-portfolio`)

Use this skill whenever Riccardo wants to add, update, or audit **Talks, Keynotes, Workshops, Articles, Codelabs, Slides, or Videos** in his portfolio application (`~/git/vibecoding/apps-portfolio`) and companion sessions repository (`~/git/my-sessions-and-bio`).

---

## 1. Architecture & Data Sources (`~/git/vibecoding/apps-portfolio`)

1. **Primary YAML Sources**:
   - **`etc/data.yaml`**: Single source of truth for `about_me`, `talks`, and `articles` (including `resource_type`: `article`, `codelab`, `slides`, `video`).
   - **`etc/videos.yaml`**: Additional video entries that `scripts/import-yaml.ts` merges into the `Article` table (`resource_type: 'video'`).
2. **Database (`db/portfolio.sqlite3`)**:
   - The SQLite database **is tracked in git** and baked into the Docker image during Cloud Build.
   - **CRITICAL**: Editing `etc/data.yaml` or `etc/videos.yaml` alone is not enough for local dev—always run `just import` (or `DATABASE_URL="file:./db/portfolio.sqlite3" npx tsx scripts/import-yaml.ts`) so `db/portfolio.sqlite3` is updated before committing.
3. **Dynamic Date Rendering (`/next-talks`, `/talks`, `/`)**:
   - `src/app/next-talks/page.tsx`, `src/app/talks/page.tsx`, and `src/app/page.tsx` must keep `export const dynamic = "force-dynamic";` so Next.js evaluates `new Date()` per-request rather than freezing the Past/Future split at Docker build time.
   - A talk appears in `/next-talks` iff `talk.date >= today (YYYY-MM-DD)` AND `talk.status !== 'delivered'`.

---

## 2. Schema & Image Conventions

### Talk Entry (`etc/data.yaml` under `talks:`)
Keep `talks:` sorted in **reverse chronological order** (`date: 'YYYY-MM-DD'` descending):

```yaml
  - title: 'Talk Title (prefix with Keynote: or [Workshop] when applicable)'
    event: Conference or Event Name
    date: '2026-10-30'
    location: City, Country
    country_code: cz # 2-letter ISO lowercase (it, ch, pl, cz, de, gb, us...) or 'remote'
    status: confirmed # 'cfp_applied' | 'confirmed' | 'delivered'
    event_url: https://example.com/
    session_url: https://sessionize.com/...
    slides_url: https://...
    video: https://www.youtube.com/watch?v=... # optional
    event_description: 'Short description of the conference/event.'
    talk_description: 'Abstract or summary of the session.'
    tags:
      - AI
      - Gemini
      - SRE
    image: /images/events/riccardo-stage-default.png
```

### On-Stage Speaker & Event Images (`public/images/events/`)
Every talk in `etc/data.yaml` **must** have a non-empty `image:` field (enforced by `scripts/import.integration.test.ts`).
- If you have an official event speaker card or banner, save it under `public/images/events/<event-slug>.png` (or `.jpg`).
- If an event does not have a dedicated poster yet, use one of Riccardo's curated on-stage speaker photos instead of borrowing another conference's banner:
  - `/images/events/riccardo-stage-default.png` *(Default fallback: canary-yellow t-shirt with centered tone-on-tone Google logo, Noogler propeller hat, slim swimmer build)*
  - `/images/events/riccardo-stage-canary-tshirt-1.png` .. `/images/events/riccardo-stage-canary-tshirt-4.png` *(Canary-yellow t-shirt variants on stage)*
  - `/images/events/riccardo-stage-yellow-blazer.png` *(Yellow blazer over blue collared shirt + Noogler cap — great for keynotes or university guest lectures)*
  - `/images/events/riccardo-stage-yellow-blazer-2k.png` *(2K hi-res yellow blazer over black t-shirt)*
  - `/images/events/riccardo-stage-white-shirt-italian.png` *(White collared shirt with Italian hand gesture `🤌`)*

### Article / Codelab / Slide Deck / Video Entry (`etc/data.yaml` under `articles:`)
```yaml
  - title: 'Resource Title'
    url: https://...
    publish_date: '2026-10-03'
    resource_type: article # 'article' | 'codelab' | 'slides' | 'video'
    relevance: 9 # 1..10
    description: 'Markdown-enabled summary (**bold**, *italics*, `code`).'
    cta:
      text: '🚀 Read the Article'
      url: https://...
    tags:
      - AI
      - Antigravity
      - highlight # Include 'highlight' to feature on the home page
    image: /images/articles/example.png
```

---

## 3. Step-by-Step Workflow to Add or Update Entries

1. **Edit `etc/data.yaml` (and/or `etc/videos.yaml`)**:
   - Insert new talks in `YYYY-MM-DD` descending order.
   - Mark past talks whose date has passed as `status: delivered`.
2. **Import into SQLite (`db/portfolio.sqlite3`)**:
   ```bash
   just import
   # or: DATABASE_URL="file:./db/portfolio.sqlite3" npx tsx scripts/import-yaml.ts
   ```
3. **Run Unit & Integration Tests + Linter**:
   ```bash
   DATABASE_URL="file:$(pwd)/db/portfolio.sqlite3" npx vitest run src/
   npm run lint
   ```
4. **Bump `VERSION` and `CHANGELOG.md`**:
   - Increment the patch/minor version in `apps-portfolio/VERSION` and document the additions at the top of `apps-portfolio/CHANGELOG.md`.
5. **Sync Companion Bio Repo (`~/git/my-sessions-and-bio/`)**:
   - Update `README.md`, `talks.md`, `workshops.md`, or `code-projects.md` in `~/git/my-sessions-and-bio/` so Riccardo's public Markdown session list stays aligned.
6. **Commit & Push (Auto-Deploy to Cloud Run)**:
   - Pushing changes under `apps-portfolio/**` to `main` automatically triggers `.github/workflows/apps-portfolio-deploy.yml` (Keyless Workload Identity Federation ➔ `gcloud builds submit`), which rebuilds the SQLite DB, runs Vitest + ESLint, builds `portfolio-app:v<VERSION>` + `portfolio-app:latest`, and deploys to Cloud Run (`https://portfolio-app-272932496670.europe-west1.run.app`).
   - Monitor the deployment with:
     ```bash
     gh run list --limit 3
     curl -s https://portfolio-app-272932496670.europe-west1.run.app/api/config
     ```

---

## 4. Resources

- Portfolio App Repository: `~/git/vibecoding/apps-portfolio/` (read `GEMINI.md` and `AI_REASONING.md` first)
- Live Cloud Run URL: `https://portfolio-app-272932496670.europe-west1.run.app`
- Companion Sessions & Bio Repo: `~/git/my-sessions-and-bio/`
