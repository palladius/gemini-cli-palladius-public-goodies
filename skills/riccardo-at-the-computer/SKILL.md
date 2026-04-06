---
name: riccardo-at-the-computer
description: Contains the logic and tools to determine if Riccardo is active on his Ubuntu computer (pupurabbux). Use this skill when Riccardo asks "am I at the computer?" or similar questions about his desktop activity.

---

# Logic for "Riccardo at the Computer"

This skill centralizes the information used to determine when Riccardo is active on his Linux computer.

## 1. Last Screen Unlock Timestamp

To find the exact time Riccardo last entered his password to unlock the screen, run the `journalctl` command directly. This is more portable than a custom script.

- **Command:** `journalctl -q -g "unlocked" --since "today" | grep -i "$USER" | tail -n 1`
- **Purpose:** Finds the most recent unlock event in the system logs. This is the most accurate way to know if you've actively used the computer.

## 2. Desktop To-Do Notifications

A script exists to check the to-do file and send a desktop notification if there are pending tasks.

- **Script Name:** `pupurabbux-notifications.sh`
- **Location:** `~/bin/pupurabbux-notifications.sh` (in the workspace's `bin` folder)
- **To-Do File Location:** `riccardo_notes/todo_computer.md`
- **Logic:** Counts lines starting with `- ` and if the count is greater than zero, sends a desktop notification using `notify-send`.

## 3. Cron Job for Notifications

To ensure Riccardo is notified about open to-dos, the notification script is executed periodically via a cron job.

- **Frequency:** Every 30 minutes (`*/30 * * * *`).
- **Command Executed:** `/Users/riccardo/.openclaw/workspace/bin/pupurabbux-notifications.sh`
- **Purpose:** To automate "nagging" for open to-do items.
