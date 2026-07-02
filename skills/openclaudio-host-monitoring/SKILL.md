---
name: openclaudio-host-monitoring
description: Installs a lightweight CPU and RAM monitoring cron job and visualization script for agents on the local machine.
---

# openclaudio-host-monitoring

This skill helps set up a zero-config, low-overhead monitoring solution to track CPU and RAM usage for local agents (like Hermes, OpenClaudio, and Tailscale).

## Instructions

When invoked to set up monitoring on a new host, follow these exact steps:

1. **Install Scripts:**
   - Copy `scripts/monitor-agents.sh` to the local `~/.hermes/bin/` or `~/bin/` directory.
   - Copy `scripts/plot_agent_metrics.py` to the same bin directory.
   - Ensure both scripts have executable permissions (`chmod +x`).

2. **Setup Cron Job:**
   - Add the following line to the user's `crontab` to run the data collection every minute:
     ```bash
     * * * * * /absolute/path/to/monitor-agents.sh
     ```

3. **Data Verification:**
   - Run the script manually once to verify it creates the CSV log file at the specified logs directory.
   - Run the visualization script via `uv run /absolute/path/to/plot_agent_metrics.py` to ensure the PNG graph is generated successfully.

4. **Documentation:**
   - Remind the user they can view the generated metrics graph anytime by running the visualization command.
