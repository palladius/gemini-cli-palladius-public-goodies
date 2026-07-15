for state in $(ls "$HOME"/git/rails8-turbo-chat/.gemini/execution_logs/AC67EF98-9364-407A-A497-FD7DDD01EF98/ghi-*/state.md 2>/dev/null); do
    issue=$(basename $(dirname "$state"))
    if grep -q "Execution End" "$state"; then
        pr=$(grep -oE "(https://github.com/[^ ]+/pull/[0-9]+|PR #[0-9]+)" "$state" | head -n 1)
        status_line=$(grep -E "^\- \*\*Status\*\*:" "$state" | sed 's/^- \*\*Status\*\*: *//' | head -n 1)
        outcome_line=$(grep -E "^\- \*\*Outcome\*\*:" "$state" | sed 's/^- \*\*Outcome\*\*: *//' | head -n 1)
        
        # Legacy heuristics if missing
        if [ -z "$status_line" ]; then
            if grep -qi "fanout-couldnt-complete\|human intervention" "$state"; then
                status_line="Aborted"
                outcome_line="Requires human intervention"
            elif grep -qi "already successfully implemented\|already fixed\|closed issue" "$state"; then
                status_line="NOOP"
                outcome_line="Already fixed/closed"
            elif grep -qi "permission to push\|user confirmation" "$state"; then
                status_line="Completed"
                outcome_line="Pending push approval"
            elif [ -n "$pr" ]; then
                status_line="Completed"
                outcome_line="Created $pr"
            else
                status_line="Completed"
                outcome_line="Work finished (no PR found)"
            fi
        fi

        if [ -n "$status_line" ]; then
            if [[ "$status_line" == *"Aborted"* ]]; then
                emoji="🛑"
            elif [[ "$status_line" == *"NOOP"* ]]; then
                emoji="🤷"
            else
                emoji="✅"
            fi
            echo "  - $emoji $issue: $status_line ($outcome_line)"
        fi
    fi
done
