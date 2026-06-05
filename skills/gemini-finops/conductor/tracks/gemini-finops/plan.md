# Implementation Plan: Gemini FinOps Skill

## Phase 1: Research & Setup
- [x] Identify the best GCP APIs for Vertex AI and API key cost/usage tracking.
- [x] Set up the directory structure for scripts and assets.
- [x] Define the `SKILL.md` interface.

## Phase 2: Core Logic (Python)
- [x] Develop script to fetch per-project/per-key usage (`cost_fetcher.py`).
- [x] Develop script for ASCII graph generation (`visualizer.py`).
- [x] Develop script for CSV comparison logic (`comparator.py`).

## Phase 3: Integration
- [x] Update `SKILL.md` with the new tools and commands.
- [x] Add tests for the Python scripts (mock data verification).

## Phase 4: Refinement
- [ ] Optimize for speed and minimal API calls.
- [x] Ensure visually appealing ASCII output.
