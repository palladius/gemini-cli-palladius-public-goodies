# Changelog — `chumbia`

All notable changes to this skill will be documented in this file.

## [1.3.0] - 2026-10-27

- 📌 **`.chumbia.touch` Breadcrumb Lock**: Added Phase 0 creation of `<GIT_ROOT>/.chumbia.touch` (with ISO timestamp, branch, and status) at the start of `chumbia_audit.sh` and removal via `chumbia_audit.sh --complete` in Phase 4. Enables the companion `git-disk-cleanup` skill to detect interrupted or failed `/chumbia` executions across `$GIT_WORKSPACE_DIR`.

## [1.2.0] - 2026-10-25

- 🎯 **Expanded Trigger Phrases**: Added English readiness-audit triggers (*"check git / git st and commit push if the work is finished, or tell me what is missing"*).
- 🛡️ **Stale `.git/sequencer/` Guardrail**: Check full `git status` (since `git status -s` / `--porcelain` hides in-progress cherry-pick/rebase sequencer state) and use `git cherry-pick --quit` (never `--abort`) when commits are already on `HEAD`.
- 🌿 **Cherry-Picked / Squashed Worktree Detection**: Added `git cherry -v origin/main <branch>` check when `git merge-base --is-ancestor` returns `1`.

## [1.1.0] - 2026-10-23

- 🧠 **Phase 3 (`/learn` Piggyback)**: Added mandatory session-learnings distillation phase ("Cosa Abbiamo Imparato Oggi?") before the final `CHUMBIA!` sign-off. Scans the conversation for user corrections, complex setup discoveries, and reusable workflows, persists what can be saved directly, and always outputs a `🧠 Learnings (/learn Piggyback)` block with a ready-to-copy `/learn` command recommendation.

## [1.0.0] - 2026-10-14

- 💃🕺🎺 Initial release of `chumbia` skill (`(💛)`).
- 🔍 **Phase 1 (Readiness Audit)**: 6-gate verification (working tree status, version/changelog bump, `just test`, `origin/main` ancestor check, Conductor track status, conversation deliverables). Refuses to say "Chumbia" if anything is incomplete.
- 🧹 **Phase 2 (Post-Work Cleanup)**: Automated cleanup of temporary Git worktrees, merged local & remote feature branches (`git push origin --delete`, `git fetch --prune`), `just clean` execution, leftover `node_modules/` in secondary worktrees, and active background timers — while strictly forbidding `git clean -fd` and `git reset --hard`.
- 🛠️ Added non-destructive audit helper script `scripts/chumbia_audit.sh`.

## [1.4.0] - 2026-11-09

- 🧬 **Superpowers Lineage & Worktree Ancestry (`references/about.md`)**:
  - Aggiunto [`references/about.md`](references/about.md) con documentazione su somiglianze e superiorità rispetto a `obra/superpowers` (`finishing-a-development-branch`, `verification-before-completion`).
  - Integrata la tecnica Superpowers per environment detection: discriminare repo standard da worktree secondari confrontando `git rev-parse --git-dir` vs `--git-common-dir`.
  - Calcolo sicuro di `MAIN_ROOT` via `$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)` prima di eliminare worktree o cambiare branch.
  - Rafforzato il check di ancestry con fallback combinato `git merge-base --is-ancestor` + `git cherry -v` per gestire squash e cherry-pick senza falsi positivi.
- 🤖 **Structured Machine-Readable Output (`--json`)**:
  - Supporto in `chumbia_audit.sh --json` con payload JSON deterministico (`chumbia_ready: true/false`, `gates`, `cleanup_eligible`) per integrazione nativa con JEV, Antigravity Sidecar, MCP server e auto-archiviazione delle chat.

## [1.5.0] - 2026-11-10

- 📦 **T3 Code MCP Auto-Archive (`t3_thread_organize`)**:
  - Aggiunta in Fase 4 la chiamata nativa a `call_mcp_tool` (`ServerName: "t3-code"`, `ToolName: "t3_thread_organize"`, `action: "archive"` o `"settle"`). Se Chumbia passa su T3 Code, la sessione viene sigillata e archiviata programmaticamente a fine turno senza alcun intervento manuale.
- 🟦 **Antigravity Interactive Archival Applet (`<agent-embed>`)**:
  - Creato template standalone `scripts/chumbia_applet.html` con card Tailwind e bottone azzurro interattivo ("📦 Archivia Chat") + "Mantieni Aperta".
  - Supporto al rendering inline dell'applet via `<agent-embed>` in chat su Antigravity IDE/Desktop con fallback su bridge sidecar o auto-archiviazione via slash command.

## [1.5.1] - 2026-11-13

- ⏱️ **Bounded SSH/Network Timeout on `git fetch`**:
  - Aggiornato `scripts/chumbia_audit.sh` e i comandi manuali in `SKILL.md` per usare `timeout 8 git fetch --prune origin` con `GIT_SSH_COMMAND="ssh -o ConnectTimeout=5"`, evitando blocchi multi-minuto quando la porta SSH 22 verso GitHub e' filtrata da firewall restrittivi.
- 🛡️ **Antigravity `<agent-embed>` CSP Compatibility**:
  - Sostituito `https://cdn.tailwindcss.com` (bloccato dalla Content Security Policy degli iframe `<agent-embed>`) con lo script allowlisted `https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js` e token semantici CSS (`var(--card)`, `var(--foreground)`) in `scripts/chumbia_applet.html`, richiedendo `ArtifactMetadata` (`UserFacing: true`, `RequestFeedback: false`) alla creazione del file HTML.

## [1.5.2] - 2026-11-18

- 🛠️ **Safe `set -euo pipefail` `grep` Pipeline in `chumbia_audit.sh`**:
  - Neutralized exit-code 1 from `grep -v '^-'` when `git cherry -v` has 0 unmerged commits (`{ grep -v '^-' || true; } | wc -l | tr -d ' '`), avoiding false `"0\n99"` fallback output.

## [1.5.3] - 2026-11-19

- 🤖 **Agent Experience (AX) Virtuous Feedback Loop**:
  - Integrated AX friction checks into Phase 3 (`/learn` & AX Piggyback) and Phase 4 Sign-Off, logging CLI hangs, context floods, and ambiguous multi-path docs via `ax_toolkit.py learn` and `/learn [AX]`.

## [1.5.4] - 2026-11-19

- 🧭 **`/learn` Target Routing (`~/.gemini/carlessian/AGENTS_LOCAL.md`)**:
  - Updated Phase 3 to forbid editing chezmoi-managed `~/.gemini/AGENTS.md` / `GEMINI.md` directly and route global learnings to `~/.gemini/carlessian/AGENTS_LOCAL.md`, work-only learnings to `~/.gemini/carlessian/AGENTS_WORK.md`, and repo/skill learnings to the local repo `AGENTS.md` or `SKILL.md`.
