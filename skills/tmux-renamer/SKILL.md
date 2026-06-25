---
name: tmux-renamer
description: Audits and renames tmux sessions based on their active content. Use when the user wants to organize their tmux workspace, identify what's running in each session, or apply a consistent naming convention (giancarlo-YYYYMMDD-SYNOPSIS) to all active sessions.
compatibility: gemini-cli
metadata:
  version: 0.1.0
---

# 💛 tmux-renamer

This skill automates the process of auditing tmux sessions and renaming them descriptively.

## Workflow

1.  **Capture Context**: Run the bundled script to dump the content of all active sessions.
    ```bash
    ./scripts/capture_all.sh
    ```
2.  **Analyze & Synopsis**: For each session, analyze the captured content (e.g., shell commands, git diffs, build logs, tool outputs) to determine the primary task.
3.  **Rename Sessions**: Rename each session using the following standard:
    -   **Pattern**: `giancarlo-YYYYMMDD-SUBSTANCE`
    -   **Rules**:
        -   Keep the original date if possible (if it follows the `giancarlo-YYYYMMDD` pattern).
        -   The `SUBSTANCE` part should be concise, lowercase, and use dashes instead of spaces.
        -   Command: `tmux rename-session -t <old-name> <new-name>`
4.  **Summary**: Provide a synopsis of each session's activity to the user after renaming.

## Guidelines

-   If a session name is already descriptive and follows the pattern, skip it unless it's outdated.
-   If you encounter a session without a date (e.g., `storazzo`), prepend the creation date or current date in `YYYYMMDD` format.
-   Always use `capture-pane` (via the script) to verify "what's cooking" before renaming.
