# Changelog — `gemini-notebook-api`

## [1.0.0] - 2026-11-06

- 🎉 Initial public release of `gemini-notebook-api` in `palladius-public-goodies`:
  - Parameterized configuration via `.env.dist` / `.env` (`GMAIL_ACCOUNT`, `QUOTA_PROJECT_ID`, `NOTEBOOK_CLIENT_ID_FILE`, `NOTEBOOK_CLOUDSDK_CONFIG`, `GEMINI_API_KEY`) with `gprism` integration.
  - Added comprehensive **"What Could Possibly Go Wrong? (Troubleshooting & Caveats)"** guide covering `403 WORKSPACE_ACCOUNT_NOT_SUPPORTED`, OAuth `"This app is blocked"` bypass via custom Desktop OAuth Client ID, `x-goog-user-project` header, `20 RPM` `CreateSource` rate limits, and PDF-to-Markdown conversion via `pdftotext`.
  - Bundled zero-dependency CLI (`scripts/notebook_cli.py`) supporting `config`, `auth`, `list`, `create`, `get`, `sources`, `add-url`, `add-md`, `add-pdf`, and `ask`.
