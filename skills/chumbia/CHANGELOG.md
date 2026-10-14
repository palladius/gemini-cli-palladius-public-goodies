# Changelog — `chumbia`

All notable changes to this skill will be documented in this file.

## [1.0.0] - 2026-10-14

- 💃🕺🎺 Initial release of `chumbia` skill (`(💛)`).
- 🔍 **Phase 1 (Readiness Audit)**: 6-gate verification (working tree status, version/changelog bump, `just test`, `origin/main` ancestor check, Conductor track status, conversation deliverables). Refuses to say "Chumbia" if anything is incomplete.
- 🧹 **Phase 2 (Post-Work Cleanup)**: Automated cleanup of temporary Git worktrees, merged local & remote feature branches (`git push origin --delete`, `git fetch --prune`), `just clean` execution, leftover `node_modules/` in secondary worktrees, and active background timers — while strictly forbidding `git clean -fd` and `git reset --hard`.
- 🛠️ Added non-destructive audit helper script `scripts/chumbia_audit.sh`.
