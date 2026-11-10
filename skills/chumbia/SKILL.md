---
name: chumbia
description: >-
  (💛) End-of-session verification, post-work cleanup ('le pulizie dopo la fatica'), '/learn'
  piggyback, and harness-aware auto-archival/settle skill. Use when the user says 'chumbia',
  '/chumbia', 'possiamo chiudere?', 'are we done? if yes say chumbia', or asks to 'check git / git st
  and commit push if the work is finished, or tell me what is missing'. Audits whether all work
  is committed, tested, and merged to main; if not done, reports what remains. If done, cleans up
  stale git sequencer states (cherry-pick/rebase), merged local/remote feature branches, temporary
  git worktrees (with safe common-dir navigation & ancestor verification), leftover node_modules/
  and build caches (via 'just clean'), cancels active background timers, piggybacks a mandatory
  '/learn' session-learnings distillation, settles/archives the thread on T3 Code via MCP
  ('t3_thread_organize') or renders an interactive archival applet on Antigravity ('<agent-embed>'),
  and concludes with CHUMBIA! so the conversation can be safely archived or destroyed.
compatibility: gemini-cli, antigravity, claude, t3-code
metadata:
  version: "1.5.0"
  author: "Riccardo Carlesso"
  tags: "cleanup, git, worktree, branch, workflow, session-end, chumbia, hygiene, learn, learnings, breadcrumbs, superpowers, t3-code, mcp, auto-archive"
---

# 💃🕺🎺 Chumbia! — End-of-Session Verification, Cleanup, `/learn` Piggyback & Auto-Archive

> **Lineage & References:** See [`references/about.md`](references/about.md) for how `chumbia` compares to and supersedes `obra/superpowers` (`finishing-a-development-branch`, `verification-before-completion`).

**Chumbia** is the end-of-conversation protocol ("le pulizie DOPO la fatica + `/learn` piggyback + auto-archiviazione").
For weekly workspace-wide sweeps across `$GIT_WORKSPACE_DIR`, see **`git-disk-cleanup`**.

When invoked, run the 5-step protocol below:

0. **Phase 0 — Breadcrumb Lock (`.chumbia.touch`)**:
   - `chumbia_audit.sh` creates `<GIT_ROOT>/.chumbia.touch` with timestamp, branch, and PID.
   - Removed only at the end of Phase 4 (`--complete`) so `git-disk-cleanup` can detect interrupted `/chumbia` runs.
1. **Phase 1 — Readiness Audit ("Abbiamo davvero finito?")**: Verify the task is tested, version-bumped, committed, pushed, and merged into `main`.
   - **If NO**: Stop (leave `.chumbia.touch` in place) and list what is pending.
2. **Phase 2 — Post-Work Cleanup ("Le Pulizie Dopo la Fatica")**:
   - Detect linked Git worktrees via `git rev-parse --git-dir` vs `--git-common-dir`.
   - Remove merged worktrees (`~/.gemini/antigravity/worktrees/`), merged branches, temporary `node_modules/`, and run `just clean`.
3. **Phase 3 — 🧠 `/learn` Piggyback**: Distill session learnings, persist what can be saved directly, and output a ready-to-trigger `/learn` recommendation.
4. **Phase 4 — Harness-Aware Settle/Archive, Clear `.chumbia.touch` & Sign-Off**:
   - On **T3 Code**: Automatically call `t3_thread_organize` with `action: "archive"` (or `"settle"`).
   - On **Antigravity**: Render the interactive **Chumbia Archival Applet** via `<agent-embed>` with a blue "Archivia Chat" button.
   - Conclude with **`CHUMBIA! 💃🕺🎺🦖✨`**.

---

## 🛡️ Ironclad Safety Rules (NEVER Violate)

- 🚫 **NEVER run `git clean -fd` or `git reset --hard`**. Untracked files may contain active work by the user or other agents.
- 🚫 **NEVER touch `.env` or `.riccardo/`**.
- 🚫 **NEVER delete unmerged branches** (`git branch -D` is forbidden unless you have first proven `git merge-base --is-ancestor <branch> origin/main` returns `0` or `git cherry -v origin/main <branch>` confirms all patches landed).
- 🚫 **NEVER run `git cherry-pick --abort` or `git rebase --abort` blindly on `main`** if a stale `.git/sequencer/` exists after commits were already landed manually — `--abort` rewinds `HEAD` to `.git/sequencer/abort-safety`! Verify whether commits are already on `HEAD`, and use `git cherry-pick --quit` to clear stale sequencer state safely without moving `HEAD`.
- 🚫 **NEVER delete protected branches** (`main`, `master`, `gh-pages`, `production`, `release/*`).
- 🚫 **NEVER delete `node_modules/` in the primary active repository** if the user is actively running a foreground dev server there — only remove `node_modules/` inside temporary/secondary worktrees or sub-repos after work is finished, or via the project's own `just clean` recipe.

---

## 🔍 Phase 1: Readiness Audit ("Abbiamo davvero finito?")

Run a non-destructive diagnostic check (or run `bash "$SKILL_DIR/scripts/chumbia_audit.sh"` / `bash "$SKILL_DIR/scripts/chumbia_audit.sh --json"` if available) covering these 6 gates:

1. **Working Tree & Sequencer Status (`git status` + `git status --porcelain`)**:
   - Are there modified, staged, or newly created files from this session that haven't been committed?
   - **Always check full `git status` (or `.git/sequencer/`, `.git/CHERRY_PICK_HEAD`, `.git/REBASE_HEAD`)**: `git status -s` / `--porcelain` hides in-progress cherry-pick/rebase sequencer state! If `.git/sequencer/` is left over from a cherry-pick whose commits are already on `HEAD`, clear it safely with `git cherry-pick --quit` (never `--abort`).
2. **Version & Changelog Hygiene**:
   - If code or skills were modified in this session and the repo maintains `VERSION` / `gemini-extension.json` and `CHANGELOG.md`, were they bumped and updated?
3. **Test Suite (`just test`)**:
   - If a `justfile` with a `test` recipe exists (`just -l | grep -E '^\s*test\b'`), are the tests passing?
4. **Branch & Upstream Sync**:
   - Run `git fetch --prune origin`.
   - Identify base branch (`origin/main`, `origin/master`).
   - If on `main`: are there unpushed local commits (`git rev-list --count origin/main..HEAD`)?
   - If on a feature branch (`<feature-branch>`): has `<feature-branch>` been merged into `origin/main` (`git merge-base --is-ancestor HEAD origin/main`), or is there still an open PR/MR waiting to land?
   - **Cherry-Picked / Squashed Worktree Check**: If a worktree branch was cherry-picked or squashed onto `main` rather than merged with `git merge`, `git merge-base --is-ancestor` returns `1`. Check `git cherry -v origin/main <branch>` (all lines prefixed with `-` means all patches are in `origin/main`) or inspect the commit log/diff on `main` to confirm the work has landed.
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

### 2. Environment Detection & Temporary Git Worktree Cleanup
Detect whether the current directory is a standard repo checkout or a linked worktree:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
```

- **Case A — Inside a Linked Git Worktree (`GIT_DIR != GIT_COMMON`)**:
  1. Determine the primary repository root safely via common dir:
     ```bash
     MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel 2>/dev/null || git worktree list --porcelain | head -n 1 | sed 's/^worktree //')
     WORKTREE_PATH=$(git rev-parse --show-toplevel)
     FEATURE_BRANCH=$(git branch --show-current)
     ```
  2. Verify that `<FEATURE_BRANCH>` is an ancestor of `origin/main` (or squashed/cherry-picked):
     ```bash
     git merge-base --is-ancestor HEAD origin/main || [ "$(git cherry -v origin/main "$FEATURE_BRANCH" | grep -v '^-' | wc -l)" -eq 0 ]
     ```
  3. Clean up ephemeral caches inside the worktree before unlinking:
     ```bash
     rm -rf "$WORKTREE_PATH/node_modules" "$WORKTREE_PATH/.turbo" "$WORKTREE_PATH/.next"
     ```
  4. Navigate safely out of the worktree back to the primary repo root before deleting the worktree:
     ```bash
     cd "$MAIN_ROOT"
     git fetch --prune origin
     git checkout main && git pull --ff-only origin main
     git worktree remove "$WORKTREE_PATH"
     if [ -n "$FEATURE_BRANCH" ] && [ "$FEATURE_BRANCH" != "main" ]; then
       git branch -d "$FEATURE_BRANCH"
     fi
     ```

- **Case B — In Primary Repository or Stale Merged Worktrees Exist (`GIT_DIR == GIT_COMMON`)**:
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
  - Check if the repo has a `clean` recipe in its `justfile`:
    ```bash
    if [ -f justfile ] && just -l 2>/dev/null | grep -qE '^\s*clean\b'; then
      just clean
    fi
    ```
- **Leftover `node_modules/` & Scratch Caches**:
  - Remove surgically leftover `node_modules/` in secondary worktrees or temporary test directories.
  - Clean up temporary scratch files in `/tmp` without ever running `git clean`.

### 5. Conductor Metadata Finalization (if applicable)
- If a Conductor track was completed in this session, ensure its `metadata.json` status is set to `"DONE"`.

---

## 🧠 Phase 3: `/learn` Piggyback ("Cosa Abbiamo Imparato Oggi?")

Before declaring `CHUMBIA!`, you **MUST ALWAYS** piggyback a `/learn` knowledge-capture pass so no valuable lesson vanishes when the conversation is destroyed:

1. **Scan the Conversation Trajectory for Learnings**:
   - User corrections, style rules, gotchas, tricky setups, or reusable recipes.
2. **Persist or Stage the Learnings**:
   - Save directly if appropriate, and always output a ready-to-copy `/learn <frase>` command snippet.

---

## 🎺 Phase 4: Clear `.chumbia.touch`, Auto-Archive & Sign-Off

When Phases 1, 2, and 3 are complete:

1. **Remove the `.chumbia.touch` Breadcrumb**:
   ```bash
   bash "$SKILL_DIR/scripts/chumbia_audit.sh" --complete
   ```

2. **Harness-Aware Auto-Archive / Settle**:
   - **If on T3 Code (MCP `t3-code` available)**:
     Call the T3 MCP tool to settle and archive the active thread cleanly:
     ```json
     call_mcp_tool(
       ServerName="t3-code",
       ToolName="t3_thread_organize",
       Arguments={"action": "archive"}
     )
     ```
     *(Note: omitting `threadId` targets the current thread; settling applies automatically at the end of the turn).*

   - **If on Antigravity (Desktop / IDE / agy CLI)**:
     Render the interactive **Chumbia Archival Applet** inline in chat:
     1. Copy `$SKILL_DIR/scripts/chumbia_applet.html` to `<appDataDir>/brain/<conversation-id>/chumbia_applet.html` (via `write_to_file` or copy command).
     2. Render the inline embed widget in your response:
        ```html
        <agent-embed src="file:///<appDataDir>/brain/<conversation-id>/chumbia_applet.html"></agent-embed>
        ```
     *(This displays a card with a prominent blue button **"📦 Archivia Chat"** and secondary **"Mantieni Aperta"**).*

3. **End with the Joyful Chumbia Sign-Off**:

```markdown
## 💃🕺🎺 CHUMBIA! 🦖✨

Tutto pulito e archiviato su `main` — puoi chiudere o distruggere questa conversazione in totale tranquillità!

- ✅ **Git & Main**: `origin/main` allineato (`vX.Y.Z`), working tree pulito, test verdi.
- 🌿 **Branch & Worktree**: [Rimosso worktree temporaneo / eliminato branch locale e remoto `<branch>` / `git fetch --prune` eseguito].
- 🧹 **Pulizie Disco & Task**: [`just clean` eseguito / rimossi `node_modules` temporanei / nessun task o cron rimasto attivo].
- 📦 **Session Status**: [Archiviata / Settled via T3 MCP | In attesa click su Applet Antigravity].
- 🧠 **Learnings (`/learn` Piggyback)**:
  - 💡 *Takeaways*: [1–3 bullet sintetici].
  - 📌 *Persistenza*: [Già salvato / Consigliato prima di chiudere: `/learn ...`].
```
