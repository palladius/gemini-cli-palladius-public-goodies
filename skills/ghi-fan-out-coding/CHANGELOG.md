# Changelog

All notable changes to this skill will be documented in this file.
## [1.5.4] - 2026-07-15
### Fixed
- 🛡️ SA: symlink only the UUID subfolder (`ln -sfn .../<UUID>`), not the entire `execution_logs/` dir. No more `rm -rf`.

## [1.5.3] - 2026-07-15
### Fixed
- 🛡️ MA: `git add -f` execution_logs after init so they persist past `.gitignore` across branch switches.
- 🛡️ SA: symlink `execution_logs` back to main repo root so all worktrees write to one shared location.
- Worktree dir names now include `<SHORT_UUID>` for traceability.

## [1.5.2] - 2026-07-15
### Fixed
- 🛡️ Added **CRITICAL** rule to both MA and SA checklists: NEVER delete `.gemini/execution_logs/`.
- 📊 Dashboard: disambiguated `⏳ Pending` (bonanza running) vs `💀 Abandoned` (bonanza ended, no status).
- 📊 Dashboard: shows skill version (bold white), commit hash (gray), and permalink to skill repo.
- 🎭 Added `playwright_hello.js` generic template and `--url` flag for Cloud Run testing.

## [1.5.1] - 2026-07-15
### Improved
- All `state_manager.sh` echo statements now print `[$CURRENT_TIME]` so agents never hallucinate timestamps.
- `review.json` gains: `code_quality_score`, `files_changed`, `lines_added`, `lines_removed`, `tests_added`, `tests_passing`, `breaking_change_detected`.
- Added signature convention to both Phase 1 and Phase 2 checklists.
- HITL path now explicitly requires commenting on BOTH the PR and the GHI.
- `main.json` timestamps renamed to `fanout_start_time`/`fanout_end_time`, added `review_start_time`/`review_end_time`.

## [1.5] - 2026-07-15
### Added
- Implemented `REVIEW_AGENT_CHECKLIST.md` for the Phase 2 sequential review workflow.
- Updated `dashboard.sh` to parse and visualize `review.json` states (`hitl_required` vs `auto_merged`).
- Updated `state_manager.sh` and Main Agent checklist to inject `hitl_threshold` and `retrospective_ghi` into `main.json` telemetry.

## [1.4] - 2026-07-15
### Added
- Added `COMMON_ERRORS.md` to help subagents self-heal based on known failures.
- Updated Main and Subagent checklists to ensure they read the common errors file before failing.
- Added a new `scripts/dashboard.sh` to provide a live, terminal-based dashboard of the bonanza progress.
*Note: This was done piggybacking off the successful execution of UUID `AC67EF98` with findings available at https://github.com/palladius/rails8-turbo-chat/issues/71.*

## [1.3] - 2026-07-14
### Added
- Refactored the logging architecture to give each subagent its own dedicated folder (`.gemini/execution_logs/<UUID>/issue-<ISSUE_NUMBER>/`).
- The primary log file is now named `state.md` and problem reports are named `problems.json`.
- Subagents can use this dedicated workspace for any custom debug files or scratch scripts.

## [1.2] - 2026-07-14
### Added
- Subagents now report problems and blockers in a structured JSON file (`issue-<ISSUE_NUMBER>-problems.json`).
- Main Agent now reads and aggregates the JSON problem reports instead of parsing raw markdown.

## [1.1] - 2026-07-14
### Added
- Added robust forensic telemetry tracking using `scripts/state_manager.sh`.
- The Main Agent now orchestrates centralized logging via `main.json` capturing execution scope (User, Hostname, Custom prompt, Harness).
- Subagents now have their logs pre-seeded with forensic metadata (git commit, git branch) and accurately timestamp their execution.

## [1.0] - 2026-07-14
### Added
- Initial release of the `ghi-fan-out-coding` skill.
- Implemented polymorphic architecture (Main Agent vs Subagent logic).
- Added references for `MAIN_AGENT_CHECKLIST.md` and `SUB_AGENT_CHECKLIST.md`.
