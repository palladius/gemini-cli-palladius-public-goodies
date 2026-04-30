# 📋 CFP Generation Checklist

Follow these three phases rigorously to ensure a high-quality CFP.

## Phase 1: Gathering Constraints & Setup
- [ ] Ask the user for the **Event Name**.
- [ ] Ask the user for the **Event URL** (what the event is about) AND the **CFP URL** (constraints, deadlines, tracks).
- [ ] Ask the user for the **Core Topic** and any relevant links (repos, blogs).
- [ ] Ask the user for specific constraints (e.g., max chars, max words) and Meta info (Demo, Duration).
- [ ] **Setup Workspace:** Create a directory named `YYYYMM-cfp-<event_name>` (e.g., `202604-cfp-codemotion`).
- [ ] **Log Context:** Save all the gathered answers and constraints into `YYYYMM-cfp-<event_name>/CFP_SYNOPSIS.md`.

## Phase 2: Data Crunching & Drafting
- [ ] **AI Independence:** Autonomously fetch the Event URL, CFP URL, and topic links.
- [ ] **Log Evidence:** Save the scraped content, themes, and research notes into `YYYYMM-cfp-<event_name>/cfp_evidence/`.
- [ ] **Drafting:** Generate 3 distinct options (Safe Bet, Storyteller, Riccardo Special) using `assets/proposal_template.md`. Save these drafts into `YYYYMM-cfp-<event_name>/out/`.
- [ ] **Feedback Loop:** Present the options to the user. Ask them to select or mix-and-match.
- [ ] **Bio Selection:** Pull the appropriate bio from `assets/riccardo_bio_templates.md`.

## Phase 3: Validation & Finalization
- [ ] Save the finalized proposal to a file (e.g., `YYYYMM-cfp-<event_name>/out/FINAL_PROPOSAL.md`).
- [ ] Run the validation script: `uv run <path_to_skill>/scripts/validate_proposal.py <path_to_final_proposal.md>`
- [ ] Report the stats (character count, word count) to the user to ensure it meets constraints.

## Phase 4: Post-Submission Tasks
When the CFP is successfully submitted:
- [ ] Ask the user to update their internal ticketing system (e.g., Buganizer) to track the proposal.
- [ ] Update the `apps-portfolio` project with this application and the skill.
- [ ] Update the Bio Sessions GH repo (usually located at `~/git/my-sessions-and-bio/`).