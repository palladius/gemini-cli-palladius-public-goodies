---
name: git-disk-cleanup
description: >-
  (💛) Daily or weekly ("Saturday Sweep") workspace-wide disk cleanup and Git
  branch/worktree hygiene skill across $GIT_WORKSPACE_DIR (defaults to ~/git or
  ~/workspace). Discovers interrupted /chumbia runs (.chumbia.touch), global uv
  cache, git-ignored dev dependencies (node_modules, .venv, .next, target),
  stale build outputs (guarded by mtime so active work is never deleted),
  merged vs. unmerged/dirty git worktrees (including ~/.gemini/antigravity/worktrees/),
  and precious media archives ("Gold" .zip/.mp4 to offload rather than delete).
license: Apache-2.0
compatibility: gemini-cli, antigravity, claude
metadata:
  version: "1.0.0"
  author: "Riccardo Carlesso"
  tags: "cleanup, disk, git, worktree, branch, chumbia, uv, node_modules, hygiene, weekly"
---

# 🧹💾 Git Disk Cleanup (`git-disk-cleanup`) — Fleet-Wide Workspace Janitor & Branch Merger

**`git-disk-cleanup`** is the macro-level ("Saturday Sweep" / daily disk emergency) counterpart to **`chumbia`**:
- **`/chumbia`** cleans up **1 repository / 1 worktree** at the end of a single conversation (creating `<GIT_ROOT>/.chumbia.touch` at start and removing it at Phase 4 sign-off).
- **`/git-disk-cleanup`** sweeps your **entire Git workspace** (`$GIT_WORKSPACE_DIR`, defaulting to `~/git` in the Carlessian Cinematic Universe or `~/workspace` elsewhere) plus global agent worktrees (`~/.gemini/antigravity/worktrees/`, `~/.gemini/jetski/worktrees/`) to reclaim gigabytes of disk space and rescue forgotten branches/worktrees before they rot!

---

## 🛡️ The 6 Ironclad Safety Invariants

1. **Always Run Discovery First (Dry-Run by Default)**:
   Run `python3 "$SKILL_DIR/scripts/git_disk_cleanup.py"` first and present the structured 4-Tier table to the user before deleting anything.
2. **Environment-Variable Portability (`GIT_WORKSPACE_DIR`)**:
   - Priority order: `--root <dir>` > `$GIT_WORKSPACE_DIR` > `$WORKSPACE_DIR` > `~/git` (if present) > `~/workspace`.
   - Never hardcode user home paths in scripts or docs.
3. **Interrupted `/chumbia` Detection (`.chumbia.touch`)**:
   - Any repository containing `<GIT_ROOT>/.chumbia.touch` had an interrupted, crashed, or incomplete `/chumbia` run. Highlight it at the very top of the report so the user can finish merging/cleaning that repo!
4. **Timestamp Freshness Guard (`--protect-days 7`)**:
   - Never delete `out/`, `publish/`, `dist/`, or `build/` folders if any file inside was modified within the last `N` days (default: `7` days). Active work (e.g., today's conference slides or articles) is marked **`🔥 PROTECTED (RECENT M-TIME)`**.
5. **Worktree Branch & Dirty Audit**:
   - Inspects both repo-local `.worktrees/` and global `~/.gemini/antigravity/worktrees/`.
   - **Tier 3A (`🟢 MERGED & CLEAN`)**: Branch is merged into `main`/`master` (`git merge-base --is-ancestor` or `git cherry`) **AND** `git status --porcelain` is empty (`dirty: 0`). 100% safe to remove via `git worktree remove`.
   - **Tier 3B (`🟡 UNMERGED OR DIRTY`)**: Never delete the worktree directory! Report its unmerged commits and dirty file count so the user can merge/salvage it, and offer to clean **only** its internal `node_modules/` or stale build caches.
6. **"Gold" Media Quarantine (`💎 DO NOT ZAP`)**:
   - Large untracked/ignored media or archives (`.zip`, `.tgz`, `.tar.gz`, `.mp4`, `.mov` >50 MB) are flagged as **`💎 GOLD — ARCHIVE TO NAS`**. Never `rm` them automatically; always propose `rsync --checksum` to NAS/external storage first.

---

## 🚀 Step-by-Step Workflow

### Step 1: Run the Discovery & Triage Script
```bash
# Default scan (auto-detects $GIT_WORKSPACE_DIR, ~/git, or ~/workspace)
python3 "$SKILL_DIR/scripts/git_disk_cleanup.py"

# Custom workspace root or custom mtime protection window (in days)
GIT_WORKSPACE_DIR=~/workspace python3 "$SKILL_DIR/scripts/git_disk_cleanup.py" --protect-days 7

# JSON output for programmatic inspection
python3 "$SKILL_DIR/scripts/git_disk_cleanup.py" --json
```

### Step 2: Present the 4-Tier Cleanup Menu & Forgotten Branches Digest
Present the script's findings grouped into:
- 🚨 **Interrupted `/chumbia` Runs (`.chumbia.touch`)** & **Dirty Main Repos**: Repos that need commits/pushes or finished `/chumbia` runs.
- **Tier 1 — Pure Dev Caches (0% Risk)**: Global `uv` cache (`~/.cache/uv`) + git-ignored `node_modules/`, `.venv/`, `.next/`, `target/`, `__pycache__/`.
- **Tier 2 — Stale Reproducible Build Outputs (`>7d` old)**: Old `publish/`, `out/`, `dist/` directories (explicitly showing which recent `out/`/`publish/` dirs were **protected** by the timestamp guard!).
- **Tier 3 — Git Worktrees & Forgotten Branches**:
  - **Tier 3A**: Merged & clean (`dirty: 0`) worktrees ready for `git worktree remove`.
  - **Tier 3B**: Unmerged or dirty worktrees — offer to either (a) strip their internal `node_modules/`/`publish/` bloat while keeping the code, or (b) inspect their diff/commits to merge them into `main` now!
- 💎 **Gold Media Archives (`DO NOT ZAP`)**: Large `.zip`/`.mp4` archives to move to NAS rather than delete.

### Step 3: Execute Approved Tiers
```bash
# Execute Tier 1 (uv cache + git-ignored node_modules/.venv/.next/__pycache__)
python3 "$SKILL_DIR/scripts/git_disk_cleanup.py" --execute --tier 1

# Execute Tier 2 (stale build outputs older than --protect-days)
python3 "$SKILL_DIR/scripts/git_disk_cleanup.py" --execute --tier 2

# Execute Tier 3A (remove merged+clean worktrees & prune inner bloat of unmerged worktrees)
python3 "$SKILL_DIR/scripts/git_disk_cleanup.py" --execute --tier 3
```

---

## ⏰ Scheduling Weekly ("Il Sabato delle Pulizie")
To run this automatically every Saturday morning (or daily when disk space is tight), recommend the `/schedule` command to the user:
> *"You can use `/schedule` to run `git-disk-cleanup` in audit mode every Saturday at 09:00 (`0 9 * * 6`) to catch forgotten worktrees, `.chumbia.touch` breadcrumbs, and multi-GB caches!"*
