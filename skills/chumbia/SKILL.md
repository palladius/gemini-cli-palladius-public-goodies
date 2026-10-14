---
name: chumbia
description: >-
  (💛) End-of-session verification and post-work cleanup skill ('le pulizie dopo la fatica').
  Use when the user says 'chumbia', '/chumbia', 'possiamo chiudere?', or 'are we done? if yes say chumbia'.
  Audits whether all work is committed, tested, and merged to main; if not done, reports what remains.
  If done, cleans up merged local/remote feature branches, temporary git worktrees, leftover node_modules/
  and build caches (via 'just clean'), cancels active background timers, and concludes with CHUMBIA!
  so the conversation can be safely archived or destroyed.
compatibility: gemini-cli, antigravity, claude
metadata:
  version: "1.0.0"
  author: "Riccardo Carlesso"
  tags: "cleanup, git, worktree, branch, workflow, session-end, chumbia, hygiene"
---

# 💃🕺🎺 Chumbia! — End-of-Session Verification & Cleanup

**Chumbia** is the official end-of-conversation protocol ("le pulizie DOPO la fatica") before archiving or destroying an agent conversation.

When the user asks *"manca qualcosa o /chumbia?"*, *"are we done? if yes say chumbia"*, or invokes `/chumbia`, you **MUST NOT** blindly say "Chumbia!". Instead, run the 3-phase protocol below:

1. **Phase 1 — Readiness Audit ("Abbiamo davvero finito?")**: Verify whether the task is 100% complete, tested, version-bumped, committed, pushed, and merged into `main`.
   - **If NO**: Do **NOT** say "Chumbia!". List clearly what is still pending and ask the user whether to finish it now.
2. **Phase 2 — Post-Work Cleanup ("Le Pulizie Dopo la Fatica")**: If Phase 1 passes, clean up temporary worktrees, merged local & remote feature branches, leftover `node_modules/` in secondary worktrees, build artifacts (`just clean`), and recurring background timers.
3. **Phase 3 — The Chumbia Sign-Off**: Conclude with a celebratory **`CHUMBIA! 💃🕺🎺🦖✨`** and a compact summary of what was verified and cleaned up.

---

## 🛡️ Ironclad Safety Rules (NEVER Violate)

- 🚫 **NEVER run `git clean -fd` or `git reset --hard`**. Untracked files may contain active work by the user or other agents.
- 🚫 **NEVER touch `.env` or `.riccardo/`**.
- 🚫 **NEVER delete unmerged branches** (`git branch -D` is forbidden unless you have first proven `git merge-base --is-ancestor <branch> origin/main` returns `0`).
- 🚫 **NEVER delete protected branches** (`main`, `master`, `gh-pages`, `production`, `release/*`).
- 🚫 **NEVER delete `node_modules/` in the primary active repository** if the user is actively running a foreground dev server there — only remove `node_modules/` inside temporary/secondary worktrees or sub-repos after work is finished, or via the project's own `just clean` recipe.

---

## 🔍 Phase 1: Readiness Audit ("Abbiamo davvero finito?")

Run a non-destructive diagnostic check (or run `bash "$SKILL_DIR/scripts/chumbia_audit.sh"` if available) covering these 6 gates:

1. **Working Tree Status (`git status --porcelain`)**:
   - Are there modified, staged, or newly created files from this session that haven't been committed?
2. **Version & Changelog Hygiene**:
   - If code or skills were modified in this session and the repo maintains `VERSION` / `gemini-extension.json` and `CHANGELOG.md`, were they bumped and updated?
3. **Test Suite (`just test`)**:
   - If a `justfile` with a `test` recipe exists (`just -l | grep -E '^\s*test\b'`), are the tests passing?
4. **Branch & Upstream Sync**:
   - Run `git fetch --prune origin`.
   - If on `main`: are there unpushed local commits (`git rev-list --count origin/main..HEAD`)?
   - If on a feature branch (`<feature-branch>`): has `<feature-branch>` been merged into `origin/main` (`git merge-base --is-ancestor HEAD origin/main`), or is there still an open PR/MR waiting to land?
5. **Conductor Track State (if applicable)**:
   - If a Conductor track was active in this session (`conductor/tracks/<track-id>/metadata.json`), are all tasks checked off?
6. **Conversation Deliverables**:
   - Review the user's requests in the current conversation. Was every question answered and every requested artifact/file delivered?

### 🛑 Decision Point
- **If ANY gate fails**:
  - **STOP.** Do **NOT** utter the word "Chumbia" as a completion signal.
  - Report a crisp checklist of what remains (e.g., *"Non siamo ancora da Chumbia! Manca: 1. Commit di X, 2. Merge del branch `feat/foo` su `main`..."*) and ask if you should complete those steps right now.
- **If ALL gates pass**:
  - Proceed immediately to **Phase 2**.

---

## 🧹 Phase 2: Post-Work Cleanup ("Le Pulizie Dopo la Fatica")

Once you have verified that all work is safely on `origin/main`, perform the post-work cleanup:

### 1. Stop Background Timers & Tasks
- Check active background tasks or scheduled crons (e.g., `manage_task` with `Action: "list"`).
- Kill any recurring `schedule` watchers (such as MR/PR polling crons) started during this conversation.

### 2. Temporary Git Worktree & Feature Branch Cleanup
Check `git worktree list` and `git branch --show-current`:

- **Case A — You are inside a temporary Git worktree** (e.g. `~/.gemini/jetski/worktrees/<repo>/<branch>`, `.worktrees/<dir>`, or a secondary worktree):
  1. Identify the primary repository path (`MAIN_REPO="$(git worktree list --porcelain | head -n 1 | sed 's/^worktree //')"`).
  2. Verify the worktree's branch `<feature-branch>` is an ancestor of `origin/main`:
     ```bash
     git merge-base --is-ancestor HEAD origin/main
     ```
  3. Remove any ephemeral `node_modules/` or build caches inside the temporary worktree before removing it.
  4. Update `main` in the primary repository and remove the temporary worktree:
     ```bash
     git -C "$MAIN_REPO" fetch --prune origin
     git -C "$MAIN_REPO" checkout main && git -C "$MAIN_REPO" pull --ff-only origin main
     git -C "$MAIN_REPO" worktree remove "<worktree-path>"
     git -C "$MAIN_REPO" branch -d "<feature-branch>"
     ```
- **Case B — You are in the main repository, or stale merged worktrees exist**:
  - Inspect `git worktree list`. If there are leftover secondary worktrees from this session whose branches are already merged into `origin/main` and whose `git status --porcelain` is clean, remove them with `git worktree remove <path>` and `git branch -d <branch>`.
  - Run `git worktree prune`.
  - If currently on a merged feature branch in the primary repo, switch back to `main`, pull `origin/main`, and delete the local feature branch (`git branch -d <feature-branch>`).

### 3. Remote Merged Branch Cleanup
- Check if the feature branch from this session is still lingering on `origin`:
  ```bash
  git branch -r --merged origin/main | grep -vE 'HEAD|origin/(main|master|gh-pages|production|release)'
  ```
- Delete the remote feature branch(es) created for this session/repo that are confirmed merged into `origin/main`:
  ```bash
  git push origin --delete "<feature-branch>"
  git fetch --prune origin
  ```

### 4. `just clean` & Ephemeral Artifact / `node_modules/` Sweep
- **Run `just clean` if available**:
  - Check if the repo (or the sub-repo worked on during the session) has a `clean` recipe in its `justfile`:
    ```bash
    if [ -f justfile ] && just -l 2>/dev/null | grep -qE '^\s*clean\b'; then
      just clean
    fi
    ```
- **Leftover `node_modules/` & Scratch Caches**:
  - Look for leftover `node_modules/` in secondary worktrees, temporary test directories, or sub-packages spun up only for verification during the session, and remove them surgically (`rm -rf <subpath>/node_modules`).
  - If in a standalone project where `node_modules/` was installed solely to run one-off validation and the user wants disk space reclaimed, remove `./node_modules` (unless a live daemon uses it).
  - Clean up any temporary scratch files created by you during this session in `/tmp` or session scratch folders, without ever running `git clean`.

### 5. Conductor Metadata Finalization (if applicable)
- If a Conductor track was completed in this session, ensure its `metadata.json` status is set to `"DONE"` (and committed/pushed before final branch cleanup).

---

## 🎺 Phase 3: The Chumbia Sign-Off

When Phase 1 and Phase 2 are complete, end your message with a clear, joyful sign-off so the user knows they can immediately archive or close the conversation:

```markdown
## 💃🕺🎺 CHUMBIA! 🦖✨

Tutto pulito e archiviato su `main` — puoi chiudere o distruggere questa conversazione in totale tranquillità!

- ✅ **Git & Main**: `origin/main` allineato (`vX.Y.Z`), working tree pulito, test verdi.
- 🌿 **Branch & Worktree**: [Rimosso worktree temporaneo / eliminato branch locale e remoto `<branch>` / `git fetch --prune` eseguito].
- 🧹 **Pulizie Disco & Task**: [`just clean` eseguito / rimossi `node_modules` temporanei / nessun task o cron rimasto attivo].
```
