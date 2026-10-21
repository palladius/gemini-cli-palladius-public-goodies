# CHANGELOG for ai-coding

## 0.1.0 (2026-10-25)
- Initial release of `ai-coding`: best practices for agent instruction files (`AGENTS.md` over `GEMINI.md` for inclusivity, symlink strategy, and `.agents/rules/` glob rules).
- Added Anti-Bloat Guardrails (`OVERFITTING_H2_SECTION`, `CRAMMED_LINE`, `APPEND_ONLY_EOF`, `CONFLICT_OR_GARBAGE`, `WALL_OF_TEXT`).
- Bundled `scripts/analyze_bloat_history.py` (and `scripts/analize_bloat_history.py` alias) with fast deterministic git diff analysis and `--llm` strict JSON mode (`gemini-flash-latest` / `gemini-3-flash-preview` / `gemini-3.1-flash-lite`).
