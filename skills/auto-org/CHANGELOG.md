# Changelog - auto-org

## [1.0.0] - 2026-10-05

- ✨ Feat: Initial release of `auto-org` skill for Desktop and Downloads intelligent file triage.
- 📂 Taxonomies: `screenshots`, `scontrini`, `viaggi`, `presentazioni`, `idee`, `documenti`, `media`, and `vecchiume`.
- 🛡️ Non-destructive staging: Candidate files are moved to `vecchiume/` without deleting anything.
- 📝 Audit logging: Automatic markdown logging in `~/Auto.org/TRIAGE_LOG.md` and Obsidian sync (`System/AutoOrg/Triage_History.md`).
- 🤖 Tooling: Bundled `scripts/auto_org.py` supporting dry-run previews, collision-safe moves, and custom age thresholds.
