---
name: gemini-notebook-api
description: >-
  (💛) Use when creating, listing, updating, or ingesting sources (web URLs,
  YouTube links, Markdown text, or local PDFs converted via pdftotext) into
  Google NotebookLM / Gemini Notebooks programmatically via the Gemini Notebook
  API v1 (https://notebook.googleapis.com/v1 and
  https://notebook.googleapis.com/mcp) using parameterized .env configuration
  (GMAIL_ACCOUNT, QUOTA_PROJECT_ID, NOTEBOOK_CLIENT_ID_FILE).
compatibility: Antigravity / Gemini CLI / OpenClaw / Hermes Agent
metadata:
  version: "1.0.0"
  tags: "notebooklm, gemini-notebook, notebook-api, mcp, pdf, rag, gprism"
---

# (💛) Gemini Notebook API v1 & MCP Skill (`gemini-notebook-api`) 📓✨

## Overview

Provides programmatic and MCP access to the **Gemini Notebook API v1** (`https://notebook.googleapis.com/v1` and MCP server `https://notebook.googleapis.com/mcp`, official docs at `https://developers.google.com/notebook/docs`).

Because the Gemini Notebook API has strict consumer-account requirements and OAuth client restrictions that trip up almost every developer on their first try, this skill bundles:
1. A clean **`.env.dist` / `.env`** configuration pattern (compatible with **`gprism`** for Secret Manager sync).
2. A zero-dependency Python CLI (`$SKILL_DIR/scripts/notebook_cli.py`) supporting `config`, `auth`, `list`, `create`, `get`, `sources`, `add-url`, `add-md`, `add-pdf`, and `ask`.
3. A battle-tested **"What Could Possibly Go Wrong?"** troubleshooting guide.

---

## 1. Configuration (`.env.dist` -> `.env` + `gprism`) 🔐

Never hardcode personal accounts, project IDs, or OAuth client paths in committed files. Copy [`$SKILL_DIR/.env.dist`](.env.dist) to `$SKILL_DIR/.env` (which is git-ignored and listed in `.git-privatize.list` for `gprism`):

```bash
cp $SKILL_DIR/.env.dist $SKILL_DIR/.env
# Edit $SKILL_DIR/.env with your consumer @gmail.com and GCP project ID, then optionally sync via gprism:
gprism push --all
```

### Environment Variables Reference

| Variable | Example Value | Description |
| :--- | :--- | :--- |
| **`GMAIL_ACCOUNT`** | `your.name@gmail.com` | **Must be a consumer `@gmail.com` account.** Google Workspace accounts fail with `403 WORKSPACE_ACCOUNT_NOT_SUPPORTED`. |
| **`QUOTA_PROJECT_ID`** | `my-personal-gcp-project` | Personal GCP Project ID where `notebook.googleapis.com` is enabled (`x-goog-user-project` header). |
| **`NOTEBOOK_CLIENT_ID_FILE`** | `~/.config/notebook-api/client_secret.json` | Desktop App OAuth 2.0 Client JSON from `QUOTA_PROJECT_ID` (bypasses `"This app is blocked"`). |
| **`NOTEBOOK_CLOUDSDK_CONFIG`** | `~/.config/gcloud-notebook` | Isolated `CLOUDSDK_CONFIG` directory so your `@gmail.com` token never overwrites your default `~/.config/gcloud` credentials. |
| **`GEMINI_API_KEY`** | `AIzaSy...` *(optional)* | Used by `notebook_cli.py ask` to run grounded Q&A over cached notebook sources. |

The CLI loads variables in this precedence order:
1. Process environment variables (`export QUOTA_PROJECT_ID=...`)
2. `$SKILL_DIR/.env`
3. Current working directory `.env`
4. `~/git/gic/.env.gprism` (if present)

---

## 2. Quick Reference & Bundled CLI (`notebook_cli.py`) 🚀

```bash
# 0. Inspect resolved configuration (GMAIL_ACCOUNT, QUOTA_PROJECT_ID, ADC path)
python3 $SKILL_DIR/scripts/notebook_cli.py config

# 1. One-time OAuth login in isolated CLOUDSDK_CONFIG (opens browser for GMAIL_ACCOUNT)
python3 $SKILL_DIR/scripts/notebook_cli.py auth

# 2. List your Gemini Notebooks
python3 $SKILL_DIR/scripts/notebook_cli.py list

# 3. Create a new Gemini Notebook
python3 $SKILL_DIR/scripts/notebook_cli.py create "My Research Notebook"

# 4. Inspect notebook metadata and list its sources
python3 $SKILL_DIR/scripts/notebook_cli.py get <notebook_id>
python3 $SKILL_DIR/scripts/notebook_cli.py sources <notebook_id>

# 5. Add a Web URL or YouTube video source
python3 $SKILL_DIR/scripts/notebook_cli.py add-url <notebook_id> "https://developers.google.com/notebook/docs" --title "Notebook API Docs"

# 6. Add a Markdown or plain-text file
python3 $SKILL_DIR/scripts/notebook_cli.py add-md <notebook_id> /path/to/notes.md --title "Meeting Notes"

# 7. Add one or more PDF files (auto-extracts via pdftotext -> Markdown, throttles at 20 RPM, polls until ACTIVE)
python3 $SKILL_DIR/scripts/notebook_cli.py add-pdf <notebook_id> /path/to/doc1.pdf /path/to/doc2.pdf

# 8. Ask a programmatic question grounded on the notebook's sources
python3 $SKILL_DIR/scripts/notebook_cli.py ask <notebook_id> "Summarize the key points and cite the sources."
```

---

## 3. What Could Possibly Go Wrong? (Troubleshooting & Caveats) ⚠️💥

Here are the 6 real-world traps you will hit with the Gemini Notebook API v1 and how to fix each one:

### Trap 1: `403 PERMISSION_DENIED` — `WORKSPACE_ACCOUNT_NOT_SUPPORTED`
- **What happens**: You run `gcloud auth` with your work/corporate Google Workspace account (`user@company.com`) and every call returns:
  `"Gemini Notebook API is not supported for Google Workspace accounts."` (`reason: WORKSPACE_ACCOUNT_NOT_SUPPORTED`).
- **Why**: The Consumer Gemini Notebook API (`notebook.googleapis.com`) only supports personal `@gmail.com` accounts (Workspace customers must use Vertex AI / Google Agentspace Enterprise).
- **The Fix**: Set `GMAIL_ACCOUNT="your.personal@gmail.com"` and `NOTEBOOK_CLOUDSDK_CONFIG="~/.config/gcloud-notebook"` in `.env`. Using an isolated `CLOUDSDK_CONFIG` keeps your personal OAuth token completely separate from your work `~/.config/gcloud` setup.

### Trap 2: Browser Error `"This app is blocked"` (`API is blocked`) During `gcloud auth`
- **What happens**: You run:
  `gcloud auth application-default login --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/notebook"`
  and Google Sign-In immediately blocks you with *"This app is blocked — This app tried to access sensitive info in your Google Account"*.
- **Why**: `gcloud`'s built-in shared OAuth Client ID (`764086051850-...`) is **not** allowlisted to request the sensitive `https://www.googleapis.com/auth/notebook` scope.
- **The Fix**:
  1. In your personal GCP project (`QUOTA_PROJECT_ID`), go to **APIs & Services -> OAuth consent screen** and add your `GMAIL_ACCOUNT` under **Test users**.
  2. Go to **APIs & Services -> Credentials -> Create Credentials -> OAuth client ID**, choose **Desktop app**, and download the JSON file to `NOTEBOOK_CLIENT_ID_FILE` (e.g., `~/.config/notebook-api/client_secret.json`).
  3. Pass `--client-id-file="$NOTEBOOK_CLIENT_ID_FILE"` when logging in (handled automatically by `notebook_cli.py auth`).

### Trap 3: `403 SERVICE_DISABLED` or Missing `x-goog-user-project` Header
- **What happens**: You get a valid token, call `GET /v1/notebooks`, and receive `403 PERMISSION_DENIED: Gemini Notebook API has not been used in project ... before or it is disabled`.
- **Why**: Application Default Credentials require an explicit quota project header (`x-goog-user-project`), and `notebook.googleapis.com` must be enabled on that project.
- **The Fix**:
  ```bash
  gcloud services enable notebook.googleapis.com --project="$QUOTA_PROJECT_ID"
  ```
  And ensure `QUOTA_PROJECT_ID` is set in `.env` so `notebook_cli.py` sends `-H "x-goog-user-project: $QUOTA_PROJECT_ID"` on every request.

### Trap 4: Uploading Binary `.pdf` Files Directly Fails
- **What happens**: You try to upload raw PDF bytes to `POST /v1/notebooks/{id}/sources` and find no binary upload field.
- **Why**: In v1, `create_source` only supports `web_content` (`{"url": "https://..."}` for web pages or YouTube videos) and `text_content` (`{"content": "...", "mime_type": "text/markdown"}` or `"text/plain"`, up to `500,000` words / `1 MB` per source). Direct binary file upload is still on the [official roadmap](https://developers.google.com/notebook/docs/roadmap).
- **The Fix**: Use `notebook_cli.py add-pdf <notebook_id> file.pdf`. It uses `pdftotext` (`poppler-utils`) to extract every page cleanly into structured Markdown (`## Page 1`, `## Page 2`, ...) and uploads it as `text/markdown`.

### Trap 5: `429 RESOURCE_EXHAUSTED` When Bulk-Uploading Sources
- **What happens**: Uploading a folder of 25 PDFs in parallel or in a fast loop fails mid-way with HTTP `429`.
- **Why**: `CreateSource` has a strict quota of **20 Requests Per Minute (RPM)** (`1` request every `3s`), whereas read/list endpoints allow **60 RPM**.
- **The Fix**: `notebook_cli.py add-pdf` automatically sleeps `3.1s` between consecutive `CreateSource` calls and polls `GET /v1/notebooks/{id}/sources/{source_id}` until `state` transitions from `CREATING` to `ACTIVE`.

### Trap 6: Where Is the `query` / `chat` Endpoint?!
- **What happens**: You look at the 7 methods in the REST/MCP surface (`create_notebook`, `get_notebook`, `list_notebooks`, `update_notebook`, `create_source`, `get_source`, `list_sources`) and realize there is no `ask_notebook` or `generateAnswer` method yet, and `get_source` only returns metadata (`name`, `displayName`, `createTime`, `state`), not the body text!
- **Why**: *"Retrieving information from a notebook"* and *"Deleting notebooks and sources"* are listed under **Coming Soon** on `https://developers.google.com/notebook/docs/roadmap`.
- **The Fix**: Whenever `notebook_cli.py` uploads a Markdown or PDF source, it caches a local copy in `~/.cache/gemini-notebook-api/<notebook_id>/`. You can then run `notebook_cli.py ask <notebook_id> "Your question"` to query all ingested sources programmatically via Gemini (`gemini-3-flash-preview`), while using the NotebookLM Web UI (`https://notebooklm.google.com/notebook/<notebook_id>`) for interactive Studio/Audio Overviews!
