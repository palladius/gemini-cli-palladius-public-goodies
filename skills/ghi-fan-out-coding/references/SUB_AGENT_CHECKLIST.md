# Subagent Checklist

You are the dedicated agent for a specific GitHub Issue. Your execution UUID was provided in your initial prompt.

## Prerequisites
Before beginning work, ensure you have received the following from the Main Agent:
1. **GHI**: The GitHub Issue number (`<ISSUE_NUMBER>`).
2. **UUID**: Both the `<SHORT_UUID>` and `<UUID>` for tagging and logging.
3. **[Optional]**: Any custom requests or specifications passed down from the Main Agent.

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
   - Create a log file at `.gemini/execution_logs/<UUID>/issue-<ISSUE_NUMBER>.md`. **IMPORTANT: You must write this file inside the MAIN repository directory, safely outside your isolated worktree.**
   - Format the log exactly with the following 3 stanzas:
     ```markdown
     fan_out_uuid: <SHORT_UUID>
     
     ## What worked well
     <your notes here>
     
     ## Issues (Cosmetic/Curiosity)
     <your notes here>
     
     ## Blocking things that broke the execution
     <your notes here (only action this if a failure occurred)>
     ```
