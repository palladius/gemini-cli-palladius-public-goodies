# Changelog

All notable changes to this skill will be documented in this file.
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
