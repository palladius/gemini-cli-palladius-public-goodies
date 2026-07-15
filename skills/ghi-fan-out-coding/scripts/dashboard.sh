#!/bin/bash

# dashboard.sh
# Parses the .gemini/execution_logs/<UUID>/ folder and prints a live summary.

if [ -z "$1" ]; then
  echo "Usage: $0 <UUID>"
  echo "Example: watch -n 2 bash $0 AC67EF98"
  exit 1
fi

UUID=$1
LOG_DIR="../../rails8-turbo-chat/.gemini/execution_logs/$UUID" # Assuming running from skill dir against sibling repo, or just look for .gemini
# Let's search from current dir up to find .gemini, or just assume the standard path
# Actually, the user will probably run this from the target repo root.
if [ -d ".gemini/execution_logs/$UUID" ]; then
    LOG_DIR=".gemini/execution_logs/$UUID"
elif [ -d "$HOME/git/rails8-turbo-chat/.gemini/execution_logs/$UUID" ]; then
    LOG_DIR="$HOME/git/rails8-turbo-chat/.gemini/execution_logs/$UUID"
else
    echo "Could not find .gemini/execution_logs/$UUID in current dir or known target repo."
    exit 1
fi


echo "====================================================="
echo "🚀 GHI Fan-Out Bonanza Dashboard | UUID: $UUID"
echo "====================================================="

total_dirs=$(find "$LOG_DIR" -type d -name "ghi-*" | wc -l | tr -d ' ')
echo "Total Issue Folders Created: $total_dirs"

completed=$(grep -r "Execution End" "$LOG_DIR"/ghi-*/state.md 2>/dev/null | wc -l | tr -d ' ')
echo "Subagents Completed: $completed / $total_dirs"

prs_created=$(grep -r "pull/" "$LOG_DIR"/ghi-*/state.md 2>/dev/null | wc -l | tr -d ' ')
echo "PRs Created: $prs_created"

problems=$(find "$LOG_DIR" -name "problems.json" | wc -l | tr -d ' ')
echo "Problem Reports (JSON): $problems"

echo "====================================================="
if [ "$problems" -gt 0 ]; then
    echo "⚠️ Problems Found:"
    for p in $(find "$LOG_DIR" -name "problems.json"); issue=$(basename $(dirname $p)); do
        echo "  - $issue: " $(grep -o '"id": "[^"]*"' "$p" | cut -d'"' -f4 | paste -sd ", " -)
    done
fi
echo "====================================================="
