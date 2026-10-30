# CHANGELOG for ai-coding

## 0.1.2 (2026-10-30)
- Added incremental `.cache/bloat-prevention.json` caching (`< last checked: YYYY-MM-DD HH:MM @ #commit >`) to `analyze_bloat_history.py`, scanning only `<last_checked_commit>..HEAD` on subsequent runs and supporting `--mark-clean` and `--no-cache` (`--full-history`).

## 0.1.1 (2026-10-27)
- Enforced canonical `.agents/` (plural) directory and added `OBSOLETE_DOT_AGENT` / directory check (`WARNING: .agent/ is obsoleted, use .agents/ instead!`) to `analyze_bloat_history.py`.

## 0.1.0 (2026-10-25)
- Initial release of `ai-coding`: best practices for agent instruction files (`AGENTS.md` over `GEMINI.md` for inclusivity, symlink strategy, and `.agents/rules/` glob rules).
- Added Anti-Bloat Guardrails (`OVERFITTING_H2_SECTION`, `CRAMMED_LINE`, `APPEND_ONLY_EOF`, `CONFLICT_OR_GARBAGE`, `WALL_OF_TEXT`).
- Bundled `scripts/analyze_bloat_history.py` (and `scripts/analize_bloat_history.py` alias) with fast deterministic git diff analysis and `--llm` strict JSON mode (`gemini-flash-latest` / `gemini-3-flash-preview` / `gemini-3.1-flash-lite`).
