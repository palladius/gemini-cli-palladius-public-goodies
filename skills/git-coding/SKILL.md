---
name: git-coding
description: >-
  (💛) Core guidelines for interacting with git repositories, updating CHANGELOGs,
  safely bumping versions, and preventing prompt bloat when editing or committing
  agent system instruction files (GEMINI.md, AGENTS.md, CLAUDE.md, CONTRIBUTING.md,
  SPECS.md, INSTRUCTIONS.md, SKILL.md). Use this skill whenever proposing or
  executing git commits, pushing code, making destructive file changes, or patching
  and auditing system prompt markdowns.
compatibility: Gemini CLI
metadata:
  version: 0.0.3
---
# Git Coding Best Practices

## Overview
This skill provides the mandatory guidelines for executing git operations, ensuring safe repository management, preventing prompt bloat in checked-in agent instruction files, and correctly formatting commits and releases.

## Core Mandates

### 1. No Destructive Commands

**NEVER** use destructive git commands such as `git clean -fd`, `git reset --hard`, or `git push --force`.
Untracked files may contain active, uncommitted work by the user or other agents.
- **Rule of Thumb:** If you need to revert or clean up, only use surgical `rm` commands on the exact files you created. If you are unsure about untracked files, always ask the user before deleting them.

### 2. The Pre-Commit Checklist

Before proposing or executing any `git commit`, you must perform the following actions in the repository:
1. **Bump Version:** Find the main configuration file containing the version (e.g., `gemini-extension.json`, `plugin.json`, `package.json`, etc.) and increment it according to Semantic Versioning (usually a patch bump, like `0.1.4` -> `0.1.5`).
2. **Update CHANGELOG.md:** Add a new entry to the `CHANGELOG.md` file documenting the changes under the new version header. Follow the `[Keep a Changelog]` format.
3. **Run Anti-Bloat Check on System Prompts:** If your diff touches `GEMINI.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SPECS.md`, `INSTRUCTIONS.md`, or `SKILL.md`, run `$SKILL_DIR/scripts/analyze_bloat_history.py --uncommitted <FILENAME>` before committing (see Mandate #6 and the `ai-coding` skill).

### 3. Commit Message Formatting
- Start by gathering context: `git status`, `git diff HEAD`, and `git log -n 3` to match the existing commit style.
- Prefer commit messages that are clear, concise, and focused more on "why" than "what".
- If the repository uses `gitmoji`, use the appropriate emoji in the commit title (e.g., 🐛 for bugs, ✨ for features, 🤖 for chores, etc.).

### 4. Push Etiquette
- **NEVER** push changes to a remote repository automatically unless explicitly requested by the user.

### 5. Renaming

* Prefer `git mv` to `mv` if file is under version control.

### 6. Anti-Bloat Guardrails for Agent System Prompts (`GEMINI.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SPECS.md`, `SKILL.md`)

When patching checked-in system instruction markdowns (`GEMINI.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SPECS.md`, `INSTRUCTIONS.md`, `SKILL.md`), **do not bloat them** (see also the companion `ai-coding` skill, which recommends preferring `AGENTS.md` over `GEMINI.md` and symlinking `GEMINI.md -> AGENTS.md`).

#### ❌ Negative Examples (Bloat Smells to Avoid)
1. **Instruction Cramming (`CRAMMED_LINE` — "10 instructions in 1 line"):**
   - *Bad:* Packing 5–10 distinct rules, clauses, or imperatives (`must`, `never`, `always`, `make sure`, `also`) into a single dense run-on line to "save vertical space".
   - *Fix:* Keep instructions atomic, concise, and grouped under an existing relevant bullet list.
2. **Overfitting Single-Concept H2/H3 Section (`OVERFITTING_H2_SECTION`):**
   - *Bad:* Adding an entire new `## Heading` (or `### Subheading`) with just 1 bullet point for a narrow, hyper-specific edge case (e.g. adding `## Dependencies` at the root `GEMINI.md` just to say *"If you change X in Septober, remember to update skill Y"*).
   - *Fix:* Either fold the rule into an existing section or push the specific rule down into the dedicated skill/subfolder where `X` lives (Progressive Disclosure).
3. **Append-Only Growth at EOF (`APPEND_ONLY_EOF`):**
   - *Bad:* Blindly appending new paragraphs to the bottom of `GEMINI.md` without reading and consolidating existing rules.
   - *Fix:* Read the whole file first, merge related rules, and prune obsolete instructions when adding new ones.

#### 🔍 Retrofitting & Pre-Commit Bloat Analyzer (`analyze_bloat_history.py`)

Use the bundled deterministic + optional-LLM script (`analyze_bloat_history.py` or `analize_bloat_history.py`) to audit git history or uncommitted changes on any prompt markdown file:

```bash
# 1. Fast, deterministic git history audit on a prompt file
python3 $SKILL_DIR/scripts/analyze_bloat_history.py GEMINI.md

# 2. Audit all discovered prompt files (GEMINI.md, AGENTS.md, CONTRIBUTING.md, SPECS.md, etc.)
python3 $SKILL_DIR/scripts/analyze_bloat_history.py --all

# 3. Pre-commit check on uncommitted / staged changes
python3 $SKILL_DIR/scripts/analyze_bloat_history.py --uncommitted GEMINI.md

# 4. Hybrid LLM audit (uses gemini-flash-latest / gemini-3-flash-preview and outputs strict JSON)
python3 $SKILL_DIR/scripts/analyze_bloat_history.py --llm GEMINI.md
```

- **Default Output:** Agent-friendly blocks showing `commit #<hash> , file <path>`, `Line X..Y`, `Bloat Probability`, triggered `Signals`, `Reason`, and the `Diff`.
- **`--llm` Output:** Strict JSON containing `"error"` (`true`/`false`), `"error_message"`, `"probability"` (float `0.0`–`1.0`, **always** present), `"reason"` (**always** present), and per-commit `"findings"`.

## Workflow Example

When asked to "commit the recent changes":

1. Check `git status` and `git diff`.
2. If any prompt markdown (`GEMINI.md`, `AGENTS.md`, `SPECS.md`, `CONTRIBUTING.md`, `SKILL.md`) was modified, run `python3 $SKILL_DIR/scripts/analyze_bloat_history.py --uncommitted <FILE>` and refactor any bloat signals (`OVERFITTING_H2_SECTION`, `CRAMMED_LINE`).
3. Find the version file and bump it.
4. Add the changes to `CHANGELOG.md`.
5. Stage the files (`git add ...`).
6. Propose the commit message to the user or execute it if given permission.
7. Ensure to attach GH issue if available in the messages. If so, also comment on the issue post-commit/push with a digest of what has been done. It reads nicely.
