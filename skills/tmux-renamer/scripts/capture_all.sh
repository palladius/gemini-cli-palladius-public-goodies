#!/bin/bash
# capture_all.sh - Dumps the content of all tmux sessions for auditing
tmux list-sessions -F '#{session_name}' | while read session; do
  echo "--- SESSION: $session ---"
  # Capture the last 50 lines to get recent activity
  tmux capture-pane -pt "$session:0.0" | tail -n 50
  echo "--- END SESSION: $session ---"
  echo ""
done
