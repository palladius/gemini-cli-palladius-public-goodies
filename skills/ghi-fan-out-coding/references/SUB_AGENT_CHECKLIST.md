# Subagent Checklist

You are the dedicated agent for a specific GitHub Issue. Your execution UUID was provided in your initial prompt.

**CRITICAL**: NEVER delete, clean up, or run `git clean` on the `.gemini/execution_logs/` directory. It contains forensic data from ALL bonanza runs. Only write to YOUR specific `ghi-<ISSUE_NUMBER>` subfolder under YOUR UUID. Deleting other folders destroys irreplaceable historical data.

## Prerequisites
Before beginning work, ensure you have received the following from the Main Agent:
1. **GHI**: The GitHub Issue number (`<ISSUE_NUMBER>`).
2. **UUID**: Both the `<SHORT_UUID>` and `<UUID>` for tagging and logging.
3. Read the pre-seeded log file at `.gemini/execution_logs/<UUID>/ghi-<ISSUE_NUMBER>/state.md` inside the main repository directory. This file contains the forensic metadata and any custom requests or specifications passed down from the Main Agent.

## HITL Threshold (Human-In-The-Loop)
You operate under a `hitl_threshold` on a 1-100 scale (default: **80**).
- **80 (Default)**: High threshold. MINIMIZE human intervention. Bother the human ONLY for super important architectural choices, severe security issues, or hard blockers (e.g., missing credentials). Drive everything else to resolution autonomously.
- **100**: Never bother the human. Make best-effort guesses or skip entirely.
- **1**: Ask the human for any choice that could possibly be wrong.

## Signature Convention
Every comment you leave on a GitHub Issue or Pull Request MUST end with:
```
--- <HARNESS> on behalf of <USERNAME>, from ghi-fan-out-coding v<SKILL_VERSION> (Phase 1 Builder Agent)
```
For example: `--- Antigravity on behalf of palladius, from ghi-fan-out-coding v1.5 (Phase 1 Builder Agent)`
You can find the harness/username in the `state.md` forensic metadata, and the skill version in `SKILL.md`.

## Execution Steps
Follow these steps exactly:

1. **Identify Feasibility**
   - Read the issue (`gh issue view <ISSUE_NUMBER>`).
   - Identify if the issue is doable without human intervention. Does it have all it takes to independently drive it to resolution?

2. **Handle Unfeasible Issues**
   - If the issue is **NOT** doable without human intervention:
     - Add a GitHub label: `gh issue edit <ISSUE_NUMBER> --add-label "fanout-couldnt-complete"`
     - Update the issue (`gh issue comment <ISSUE_NUMBER>`) asking specific, clarifying questions which can be answered by a human to allow resolution at the next pass.
     - Stop execution here.

3. **Implement Fix (If Feasible)**
   - If yes, add a GitHub label: `gh issue edit <ISSUE_NUMBER> --add-label "fanout-automation-possible"`
   - Create a new isolated worktree: `git worktree add .worktrees/issue-<ISSUE_NUMBER>-fix-<SHORT_UUID> -b feature/issue-<ISSUE_NUMBER>`
   - Change your current working directory to the new worktree.
   - **Symlink execution_logs back to main repo** so all agents write to ONE shared location (not scattered copies in each worktree):
     ```bash
     # In the worktree directory:
     MAIN_REPO_ROOT="$(git worktree list | head -1 | awk '{print $1}')"
     mkdir -p .gemini/execution_logs
     ln -sfn "$MAIN_REPO_ROOT/.gemini/execution_logs/<UUID>" .gemini/execution_logs/<UUID>
     # Exclude from git tracking in this worktree:
     mkdir -p "$(git rev-parse --git-dir)/info" && echo ".gemini/execution_logs" >> "$(git rev-parse --git-dir)/info/exclude"
     ```
   - **TDD Requirement**: Write meaningful failing tests *first* to confirm the bug exists, and then implement the code to make them pass.

4. **Create PR and Update**
   - When the fix is done and tests are passing, commit your changes.
   - Create a Pull Request with your branch. Include a message for the user in the PR body.
   - Update the original GHI with a comment summarizing what has been done and what choices were taken.

5. **Clean Up Worktree**
   - Immediately after successfully creating the PR, navigate back to the main repository directory.
   - Run `git worktree remove <path-to-your-worktree-folder>`.
   - *Note*: It is 100% safe to do this while the PR is open because the code has already been pushed to GitHub. If this command fails due to uncommitted files, report the error as a comment in the GHI so it can be investigated by a human.

6. **Log Execution Results**
   - **IMPORTANT**: Open the pre-seeded log file at `.gemini/execution_logs/<UUID>/ghi-<ISSUE_NUMBER>/state.md` in the MAIN repository directory.
   - Append the following stanza to the bottom of the file:
     ```markdown
     ## What worked well
     <your notes here>
     ```
   - **Crucial JSON Status**: In addition to `state.md`, you MUST create a `status.json` file in the exact same directory: `.gemini/execution_logs/<UUID>/ghi-<ISSUE_NUMBER>/status.json`.
   - The `status.json` must exactly match this schema based on what you accomplished:
     ```json
     {
       "state": "MERGED | PR_CREATED | NOOP_GOOD | NOOP_BAD",
       "explanation": "Brief explanation of what happened or why a NOOP was triggered",
       "commit_hash": "12ab34",  // Required if state is MERGED
       "pr_id": "69",            // Required if state is PR_CREATED
       "ghi_tags_added": ["fanout-couldnt-complete"] // Required if state is NOOP_BAD (waiting for user input)
     }
     ```
     *Definitions:*
     - `MERGED`: Issue resolved and merged directly to main.
     - `PR_CREATED`: You successfully created a PR (default success path).
     - `NOOP_GOOD`: The issue is already fixed or invalid, no code changes needed.
     - `NOOP_BAD`: You hit a blocker (missing credentials, vague issue) and are waiting for human input.
   - **If you encountered any issues or blocking problems**, first read the file `references/COMMON_ERRORS.md` to see if a known solution exists. If you can self-correct, do so!
   - If the error is unknown or unrecoverable, you MUST create a new file at `.gemini/execution_logs/<UUID>/ghi-<ISSUE_NUMBER>/problems.json` containing a JSON array of the problems. The schema must exactly match this format:
     ```json
     [
       {
         "id": "short_unique_id_no_spaces",
         "description": "A lengthy markdown description of what the problem was.",
         "proposed_resolution": "What we should do differently next time to avoid this."
       }
     ]
     ```
   - *Note*: The folder `.gemini/execution_logs/<UUID>/ghi-<ISSUE_NUMBER>/` is your dedicated workspace for this execution. You are free to write any additional debug logs, scratch scripts, or investigation notes you need into this directory.

7. **End Forensic Telemetry**
   - As your final step, run the state manager script to stamp the end time into your log file:
     ```bash
     bash ~/git/gemini-cli-palladius-public-goodies/skills/ghi-fan-out-coding/scripts/state_manager.sh sub_end --issue <ISSUE_NUMBER> --uuid <UUID>
     ```
