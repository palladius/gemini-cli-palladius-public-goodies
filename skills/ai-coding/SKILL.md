---
name: ai-coding
description: >-
  (💛) Best practices for AI-assisted coding and maintaining agent system instructions
  (AGENTS.md, GEMINI.md, CLAUDE.md, CONTRIBUTING.md, SPECS.md, INSTRUCTIONS.md, SKILL.md).
  Enforces inclusive AGENTS.md over vendor-specific files, prevents prompt bloat
  (instruction cramming, single-concept overfitting H2 sections, append-only drift),
  and provides analyze_bloat_history.py to audit Git history or uncommitted diffs.
compatibility: Gemini CLI
metadata:
  version: 0.1.1
---
# AI Coding & Agent Prompt Hygiene (`ai-coding`)

## Overview
Just like `ruby-coding`, `python-coding`, `typescript-coding`, and `git-coding` govern code and version control, **`ai-coding`** governs how we architect, maintain, and evolve instructions for AI agents across repositories.

System instruction files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SPECS.md`, `INSTRUCTIONS.md`, `SKILL.md`) are loaded into the context window on every turn. Keeping them inclusive, modular, and bloat-free is critical for agent reliability and token efficiency.

---

## Core Mandates

### 1. Prefer `AGENTS.md` Over `GEMINI.md` (Inclusivity & Single Source of Truth)
- **`AGENTS.md` is the primary standard:** Whenever creating or refactoring project-level instructions for AI coding assistants, prefer **`AGENTS.md`** over vendor-specific names like `GEMINI.md` or `CLAUDE.md`. `AGENTS.md` is vendor-neutral, inclusive, and natively discovered by Antigravity, Gemini CLI, OpenClaw/Hermes, Codex, and modern multi-agent harnesses.
- **Symlink for backwards compatibility:** If a specific tool or legacy workflow explicitly expects `GEMINI.md` (or `CLAUDE.md`), **never duplicate the content**. Instead, create a symlink:
  ```bash
  ln -s AGENTS.md GEMINI.md
  ```
- **Canonical `.agents/` (plural):** Place modular rules in `.agents/rules/<name>.md` (`trigger: glob` or `model_decision`). `.agent/` (singular) is obsolete — always `git mv .agent .agents`.

---

### 2. Anti-Bloat Guardrails When Patching Prompt Markdowns

When patching checked-in system instruction markdowns (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SPECS.md`, `INSTRUCTIONS.md`, `SKILL.md`), **make sure you do not bloat them**.

#### ❌ Negative Examples (Bloat Smells to Avoid)

1. **Instruction Cramming (`CRAMMED_LINE` — "10 instructions in 1 line"):**
   - *Smell:* Packing 5–10 distinct rules, clauses, or imperatives (`must`, `never`, `always`, `make sure`, `ensure`, semicolons, comma-chains) into a single run-on line to "save vertical space".
   - *Why it hurts:* LLMs lose attention in dense multi-clause lines and skip middle constraints.
   - *Fix:* Break rules into concise, atomic bullet points under an appropriate existing section.

2. **Single-Concept Overfitting H2/H3 Section (`OVERFITTING_H2_SECTION`):**
   - *Smell:* Adding a whole new `## Heading` (or `### Subheading`) containing just 1–2 lines/bullets for a narrow, reactive, one-off edge case (e.g., adding `## Dependencies` at the bottom of a root `GEMINI.md` just to say *"If you change sub-agents in Septober, remember to update skill X"*).
   - *Why it hurts:* Every future turn on any topic pays the token and attention cost of a narrow rule that only applies to 1% of tasks.
   - *Fix:*
     - Move narrow rules down into the specific **Skill** (`skills/<name>/SKILL.md`), subdirectory `AGENTS.md`, or `.agents/rules/` glob rule where they actually apply (**Progressive Disclosure**).
     - Or integrate the bullet into an existing general section instead of spawning a new H2 header.

3. **Append-Only EOF Drift (`APPEND_ONLY_EOF`):**
   - *Smell:* Repeatedly appending new rules at the very bottom of `AGENTS.md` / `GEMINI.md` (`+N / -0 lines`) without reading or consolidating what is already in the file.
   - *Fix:* Read the entire file before patching. Merge related bullets and prune outdated instructions.

4. **Merge Conflict Markers or Wall of Text (`CONFLICT_OR_GARBAGE` / `WALL_OF_TEXT`):**
   - *Smell:* Committing `<<<<<<< HEAD` / `=======` / `>>>>>>>` markers or dumping `>25` lines of procedural runbooks into a root prompt file.
   - *Fix:* Keep root `AGENTS.md` / `GEMINI.md` under ~100–150 lines of high-signal architectural map and invariants; delegate procedural runbooks to `skills/` or `docs/`.

---

## 🔍 Retrofitting & Pre-Commit Bloat Analyzer (`analyze_bloat_history.py`)

Use the bundled script (`analyze_bloat_history.py` or `analize_bloat_history.py`) to inspect Git commit history or uncommitted changes on any prompt markdown file:

```bash
# 1. Fast, deterministic git history audit on a prompt file (< 20ms)
python3 $SKILL_DIR/scripts/analyze_bloat_history.py GEMINI.md
python3 $SKILL_DIR/scripts/analyze_bloat_history.py AGENTS.md

# 2. Auto-discover and audit all prompt files in a repository (AGENTS.md, GEMINI.md, SPECS.md, etc.)
python3 $SKILL_DIR/scripts/analyze_bloat_history.py --all

# 3. Pre-commit check on uncommitted working-tree / staged changes
python3 $SKILL_DIR/scripts/analyze_bloat_history.py --uncommitted GEMINI.md

# 4. Hybrid LLM evaluation (uses gemini-flash-latest / gemini-3-flash-preview and outputs strict JSON)
python3 $SKILL_DIR/scripts/analyze_bloat_history.py --llm GEMINI.md
```

### Output Modes
- **Default (Agent-Friendly Text):**
  ```text
  ================================================================================
  commit #aa6f640 , file GEMINI.md
  Date: Sun Sep 27 08:05:27 2026 +0200 | Author: Riccardo Carlesso | Subject: chore: sync
  Line 82..87 (@@ -82,2 +82,6 @@)
  Bloat Probability: 0.85 (85%) [HIGH] — Signals: OVERFITTING_H2_SECTION, APPEND_ONLY_EOF
  Reason: [OVERFITTING_H2_SECTION] Added whole heading '## Dependencies' for a single-concept / 1-item rule...
  Diff:
  +## Dependencies
  +* **Septober Sub-Agents**: If you change the way sub-agents work in Septober...
  ================================================================================
  ```
- **`--llm` / `--json` (Strict JSON Schema):**
  Always returns a JSON object with:
  - `"error"`: boolean (`true` or `false`)
  - `"error_message"`: string or `null`
  - `"probability"`: float (`0.0` to `1.0`, **always** present — falls back to deterministic probability if LLM API is unreachable)
  - `"reason"`: string (**always** present — explains why that probability was assigned)
  - `"findings"`: array of per-commit/per-hunk evaluations
