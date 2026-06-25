# Antigravity CLI Termination Hook

This folder contains the configuration and scripts to handle lifecycle hooks when running the Antigravity CLI (`agy`) in this workspace.

## Components

1. **`hooks.json`**: Configures the `Stop` event hook to trigger our Python handler.
2. **`on_terminate.py`**: A Python script executed when the agent's execution loop ends.

## Features

When the session exits, the script performs the following actions:
- **Speech Notification**: Speaks `"Sto uscendo da anti gravita permanente"` in Italian using `spd-say`.
- **Terminal Output**: Prints `"Chumbia!"` to standard output.
- **Session Log**: Creates a file named `.agy-terminated.YYYYMMDD-HHMM.log` in the current directory containing:
  - Timestamp of termination.
  - JSON payload sent by the Antigravity engine (including `conversationId` / session ID, status, and exit reasons).
  - Active environment variables for the session.
