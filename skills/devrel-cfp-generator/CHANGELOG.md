# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.3] - 2026-04-30
### Added
- Added Phase 4 to the `cfp_checklist.md` with post-submission tasks (Update ticketing system, portfolio app, and bio sessions).

### Changed
- Updated `SKILL.md` to instruct the agent to copy the checklist file locally into the working directory so it can check off items.
- Bumped skill version from 0.0.2 to 0.0.3.

## [0.0.2] - 2026-04-30
### Added
- 🔍 Added `Small Print` section to `proposal_template.md` to capture metadata required by Sessionize.
- 🐍 Updated `validate_proposal.py` to validate `Small Print` section presence.

## [0.0.1] - 2026-04-30
### Added
- Initial release of the `devrel-cfp-generator` skill.
- 📋 Added `cfp_checklist.md` for a strict 3-phase CFP generation workflow.
- 🎯 Added `proposal_template.md` for deterministic CFP formatting.
- 🗣️ Added `riccardo_bio_templates.md` for standard and snarky bios.
- 🐍 Added `validate_proposal.py` to automatically count characters/words and validate sections.
- 📁 Enforced isolated directory structure (`YYYYMM-cfp-eventname/`) with `CFP_SYNOPSIS.md` and `cfp_evidence/`.
