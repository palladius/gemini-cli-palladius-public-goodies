# Main Agent Checklist

**IMPORTANT**: Ensure you are using a powerful, high thinking mode (e.g. Gemini 2.5 Pro or equivalent). If you believe you are running on a lightweight/flash model, you must **refuse to run** and ask the user to invoke you with a higher tier model.

Follow these steps exactly:

1. **Initialize Bonanza**
   - Generate a unique `UUID` for this execution run (e.g., using `uuidgen` or standard formatting).
   - Extract the first 8 characters to form the `<SHORT_UUID>`.

2. **Setup Labels**
   - Ensure the necessary GitHub labels exist by running the following commands:
     - `gh label create "fan_out_<SHORT_UUID>" --force`
     - `gh label create "fanout-automation-possible" --force`
     - `gh label create "fanout-couldnt-complete" --force`

3. **Pre-Flight Checks (Anticipate Blockers)**
   - The goal is for the subagents to run completely autonomously while the user is away. You must anticipate any environmental or policy blockers *before* you fan out.
   - **Check Auth**: E.g., is `gcloud auth login` required?
   - **Check Dependencies**: E.g., does `docker build` fail because the docker daemon isn't running?
   - **Check Rules**: Read `GEMINI.md` for any strict rules like "don't do X without asking the user first".
   - If you identify any blockers, interact with the user (back and forth as many times as needed) to resolve them *before* proceeding to the fan-out stage.

4. **Fetch Issues**
   - Use `gh issue list` to find all open GitHub issues in the current repository.
   - **Important**: Filter out and ignore any issues that contain `[META]` in the title to avoid recursion.

5. **Fan-Out (Subagent Creation)**
   - For *every* target GitHub issue found, tag it by adding a label: `gh issue edit <#> --add-label "fan_out_<SHORT_UUID>"`
   - Use your `invoke_subagent` tool to spawn a separate subagent for each issue.
   - For each subagent, use the following exact prompt:
     > "You are the agent for GHI #<ISSUE_NUMBER>. Read the `references/SUB_AGENT_CHECKLIST.md` instructions from the `ghi-fan-out-coding` skill. The execution short UUID for logging is <SHORT_UUID> and the long UUID is <UUID>."
   - Let the subagents run autonomously in the background.

6. **Monitor & Wait**
   - Wait until ALL subagents have completed their execution and reported back.

7. **Fan-In (Reconcile)**
   - Check the status of the PRs and GHIs that were worked on.
   - For each issue, check: "Did the subagent close the PR and GHI, and is it merged into main?"
   - If yes, append "Chumbia! 💥" next to the issue's status in your internal list.

8. **Meta (Synoptic Reporting)**
   - Create a Meta GitHub issue summarizing the entire execution run.
   - The title must be exactly: `[META] <YYYYMMDD> ghi parallel resolution bonanza report [<SHORT_UUID>]`
   - Read the subagent logs from the Main repository directory (`.gemini/execution_logs/<UUID>/`) to aggregate the 3 stanzas.
   - In the Meta issue body, include:
     - Links to what has been done (PRs and Issues touched).
     - Aggregated "What worked well".
     - Aggregated "Issues (Cosmetic/Curiosity)".
     - Aggregated "Blocking things that broke the execution".
