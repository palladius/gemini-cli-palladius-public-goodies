# Subagent Checklist

You are the dedicated agent for a specific GitHub Issue. Your execution UUID was provided in your initial prompt.

## Prerequisites
Before beginning work, ensure you have received the following from the Main Agent:
1. **GHI**: The GitHub Issue number (`<ISSUE_NUMBER>`).
2. **UUID**: Both the `<SHORT_UUID>` and `<UUID>` for tagging and logging.
3. Read the pre-seeded log file at `.gemini/execution_logs/<UUID>/ghi-<ISSUE_NUMBER>/state.md` inside the main repository directory. This file contains the forensic metadata and any custom requests or specifications passed down from the Main Agent.

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
   - Create a new isolated worktree: `git worktree add .worktrees/issue-<ISSUE_NUMBER>-fix -b feature/issue-<ISSUE_NUMBER>`
   - Change your current working directory to the new worktree.
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
   - **If you encountered any issues or blocking problems**, you MUST create a new file at `.gemini/execution_logs/<UUID>/ghi-<ISSUE_NUMBER>/problems.json` containing a JSON array of the problems. The schema must exactly match this format:
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
