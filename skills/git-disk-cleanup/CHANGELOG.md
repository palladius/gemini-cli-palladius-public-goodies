# Changelog — `git-disk-cleanup`

All notable changes to this skill will be documented in this file.

## [1.0.0] - 2026-10-27

- 🧹💾 Initial release of `git-disk-cleanup` (`(💛)`) in `palladius-public-goodies`.
- 🌍 **Workspace Portability (`GIT_WORKSPACE_DIR`)**: Supports `--root`, `$GIT_WORKSPACE_DIR`, `$WORKSPACE_DIR`, with automatic fallback to `~/git` or `~/workspace`.
- 📌 **`.chumbia.touch` Breadcrumb Detection**: Detects interrupted or incomplete `/chumbia` executions across all repositories in the workspace.
- ⏱️ **Timestamp Freshness Guard (`--protect-days 7`)**: Protects `out/`, `publish/`, `dist/`, and `build/` folders modified within the last `N` days so active presentations/articles are never deleted.
- 🌿 **Worktree & Branch Hygiene**: Scans both repo-local `.worktrees/` and global `~/.gemini/antigravity/worktrees/` (and `jetski/worktrees`), separating `MERGED + CLEAN (dirty: 0)` worktrees from `UNMERGED / DIRTY` worktrees.
- 💎 **Gold Media Protection**: Flags large `.zip`, `.tgz`, `.mp4`, `.mov` archives (>50 MB) as `GOLD / DO NOT ZAP` candidates for NAS offload.
