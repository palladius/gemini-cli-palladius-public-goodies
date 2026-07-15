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

MAIN_JSON="$LOG_DIR/main.json"
SKILL_VERSION=""
SKILL_COMMIT=""
if [ -f "$MAIN_JSON" ]; then
    SKILL_VERSION=$(python3 -c "import json; d=json.load(open('$MAIN_JSON')); print(d.get('skill_version','?'))" 2>/dev/null)
    SKILL_COMMIT=$(python3 -c "import json; d=json.load(open('$MAIN_JSON')); print(d.get('skill_commit','?')[:7])" 2>/dev/null)
fi

echo "====================================================="
echo -e "🚀 GHI Fan-Out Bonanza Dashboard | UUID: $UUID"
echo -e "   Skill: \033[1;37mv${SKILL_VERSION}\033[0m  \033[90m#${SKILL_COMMIT}\033[0m"
echo -e "   \033[90mhttps://github.com/palladius/gemini-cli-palladius-public-goodies/tree/${SKILL_COMMIT}/skills/ghi-fan-out-coding\033[0m"
echo "====================================================="

total_dirs=$(find "$LOG_DIR" -type d -name "ghi-*" | wc -l | tr -d ' ')
echo "Total Issue Folders Created: $total_dirs"

completed=$(grep -r "Execution End" "$LOG_DIR"/ghi-*/state.md 2>/dev/null | wc -l | tr -d ' ')
echo "Subagents Completed: $completed / $total_dirs"

prs_created=$(grep -rE "pull/|PR #[0-9]+" "$LOG_DIR"/ghi-*/state.md 2>/dev/null | wc -l | tr -d ' ')
echo "PRs Created: $prs_created"

problems=$(find "$LOG_DIR" -name "problems.json" | wc -l | tr -d ' ')
echo "Problem Reports (JSON): $problems"

echo "====================================================="
if [ "$total_dirs" -gt 0 ]; then
    echo "📊 Agent Status:"
    for state in $(ls "$LOG_DIR"/ghi-*/state.md 2>/dev/null); do
        issue=$(basename $(dirname "$state"))
        if grep -q "Execution End" "$state"; then
            status_file="$(dirname "$state")/status.json"
            review_file="$(dirname "$state")/review.json"
            
            # Parse review data
            quality_bar="          "  # 10 chars blank placeholder
            review_detail=""
            if [ -f "$review_file" ]; then
                json_rev_outcome=$(python3 -c "import json, sys; d=json.load(open('$review_file')); print(d.get('outcome', ''))" 2>/dev/null)
                json_quality=$(python3 -c "import json, sys; d=json.load(open('$review_file')); print(d.get('code_quality_score', ''))" 2>/dev/null)
                
                # Build quality bar: 8 chars wide, █ for filled, ░ for empty
                if [ -n "$json_quality" ] && [ "$json_quality" -gt 0 ] 2>/dev/null; then
                    filled=$(( json_quality * 8 / 100 ))
                    [ "$filled" -gt 8 ] && filled=8
                    [ "$filled" -lt 0 ] && filled=0
                    empty=$(( 8 - filled ))
                    bar_str="$(printf '█%.0s' $(seq 1 $filled 2>/dev/null))$(printf '░%.0s' $(seq 1 $empty 2>/dev/null))"
                    quality_bar=$(printf '%-10s' "$bar_str ${json_quality}%")
                fi

                if [ "$json_rev_outcome" == "auto_merged" ]; then
                    review_detail="🕵️ Auto-Merged"
                elif [ "$json_rev_outcome" == "hitl_required" ]; then
                    review_detail="🕵️ HITL"
                else
                    review_detail="🕵️ Reviewed"
                fi
            fi

            if [ -f "$status_file" ]; then
                json_state=$(python3 -c "import json, sys; d=json.load(open('$status_file')); print(d.get('state', ''))" 2>/dev/null)
                json_outcome=$(python3 -c "import json, sys; d=json.load(open('$status_file')); print(d.get('explanation', ''))" 2>/dev/null)
                json_pr=$(python3 -c "import json, sys; d=json.load(open('$status_file')); print(d.get('pr_id', ''))" 2>/dev/null)
                
                if [ "$json_state" == "MERGED" ]; then
                    bullet="🟢"; emoji="🟣"; state_code="MERGED"
                    detail="$json_outcome"
                elif [ "$json_state" == "PR_CREATED" ]; then
                    bullet="🟢"; emoji="✅"; state_code="PR_CREATED"
                    if [ -n "$json_pr" ]; then
                        detail="PR #$json_pr"
                    else
                        detail="⚠️ FIXME: pr_id missing in status.json"
                    fi
                elif [ "$json_state" == "NOOP_GOOD" ]; then
                    bullet="🟢"; emoji="♻️ "; state_code="NOOP_GOOD"
                    detail="$json_outcome"
                elif [ "$json_state" == "NOOP_BAD" ]; then
                    bullet="🔴"; emoji="🛑"; state_code="NOOP_BAD"
                    detail="$json_outcome"
                else
                    bullet="🟢"; emoji="✅"; state_code="$json_state"
                    detail="$json_outcome"
                fi
                [ -n "$review_detail" ] && detail="$detail $review_detail"
                printf "  %s %s %-8s %-12s %s  %s\n" "$bullet" "$emoji" "$issue" "$state_code" "$quality_bar" "$detail"
                continue
            fi
            
            pr=$(grep -oE "(https://github.com/[^ ]+/pull/[0-9]+|PR #[0-9]+)" "$state" | head -n 1)
            status_line=$(grep -E "^\- \*\*Status\*\*:" "$state" | sed 's/^- \*\*Status\*\*: *//' | head -n 1)
            outcome_line=$(grep -E "^\- \*\*Outcome\*\*:" "$state" | sed 's/^- \*\*Outcome\*\*: *//' | head -n 1)
            
            # Legacy heuristics if structured fields are missing
            if [ -z "$status_line" ] || [ -z "$outcome_line" ]; then
                if grep -qi "fanout-couldnt-complete\|human intervention" "$state"; then
                    state_code="ABORTED"; detail="Requires human intervention"
                    bullet="🔴"; emoji="🛑"
                elif grep -qi "already successfully implemented\|already fixed\|closed issue" "$state"; then
                    state_code="NOOP_GOOD"; detail="Already fixed/closed"
                    bullet="🟢"; emoji="♻️ "
                elif grep -qi "permission to push\|user confirmation" "$state"; then
                    state_code="COMPLETED"; detail="Pending push approval"
                    bullet="🟢"; emoji="✅"
                elif [ -n "$pr" ]; then
                    state_code="COMPLETED"; detail="$pr"
                    bullet="🟢"; emoji="✅"
                else
                    state_code="COMPLETED"; detail="Work finished"
                    bullet="🟢"; emoji="✅"
                fi
            else
                if [[ "$status_line" == *"Aborted"* ]]; then
                    state_code="ABORTED"; bullet="🔴"; emoji="🛑"
                elif [[ "$status_line" == *"NOOP"* ]]; then
                    state_code="NOOP_GOOD"; bullet="🟢"; emoji="♻️ "
                else
                    state_code="COMPLETED"; bullet="🟢"; emoji="✅"
                fi
                detail="$outcome_line"
            fi
            [ -n "$review_detail" ] && detail="$detail $review_detail"
            printf "  %s %s %-8s %-12s %s  %s\n" "$bullet" "$emoji" "$issue" "$state_code" "$quality_bar" "$detail"
        else
            # Is the bonanza still running or has it ended?
            bonanza_ended=""
            if [ -f "$MAIN_JSON" ]; then
                bonanza_ended=$(python3 -c "import json; d=json.load(open('$MAIN_JSON')); print(d.get('fanout_end_time',''))" 2>/dev/null)
            fi
            if [ -n "$bonanza_ended" ]; then
                printf "  ⚪ 💀 %-8s %-12s\n" "$issue" "ABANDONED"
            else
                printf "  ⚪ ⏳ %-8s %-12s\n" "$issue" "PENDING"
            fi
        fi
    done
fi

if [ "$problems" -gt 0 ]; then
    echo "⚠️ Problems Found:"
    for p in $(find "$LOG_DIR" -name "problems.json"); do
        issue=$(basename $(dirname $p))
        echo "  - $issue: " $(grep -o '"id": "[^"]*"' "$p" | cut -d'"' -f4 | paste -sd ", " -)
    done
fi
echo "====================================================="
