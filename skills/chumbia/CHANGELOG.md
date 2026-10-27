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
