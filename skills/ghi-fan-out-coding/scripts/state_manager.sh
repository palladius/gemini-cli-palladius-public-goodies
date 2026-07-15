#!/bin/bash
set -e

ACTION=$1
shift

# Parse arguments
ISSUE=""
UUID=""
SHORT_UUID=""
CUSTOM_PROMPT=""
HARNESS=""
HITL_THRESHOLD="80"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --issue) ISSUE="$2"; shift ;;
        --uuid) UUID="$2"; shift ;;
        --short-uuid) SHORT_UUID="$2"; shift ;;
        --custom-prompt) CUSTOM_PROMPT="$2"; shift ;;
        --harness) HARNESS="$2"; shift ;;
        --hitl-threshold) HITL_THRESHOLD="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [[ -z "$UUID" ]]; then
    echo "Error: --uuid is required."
    exit 1
fi

LOG_DIR=".gemini/execution_logs/$UUID"
mkdir -p "$LOG_DIR"

CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [[ "$ACTION" == "main_start" ]]; then
    MAIN_JSON="$LOG_DIR/main.json"
    GIT_REPO=$(git config --get remote.origin.url || echo "unknown")
    
    SKILL_DIR=$(dirname "$(dirname "$0")")
    SKILL_VERSION=$(grep -E "^  version:" "$SKILL_DIR/SKILL.md" 2>/dev/null | awk '{print $2}' || echo "unknown")
    SKILL_COMMIT=$(git -C "$SKILL_DIR" rev-parse HEAD 2>/dev/null || echo "unknown")
    
    cat <<EOF > "$MAIN_JSON"
{
  "fanout_start_time": "$CURRENT_TIME",
  "custom_prompt": "$CUSTOM_PROMPT",
  "github_repo": "$GIT_REPO",
  "username": "$USER",
  "hostname": "$HOSTNAME",
  "harness": "$HARNESS",
  "skill_version": "$SKILL_VERSION",
  "skill_commit": "$SKILL_COMMIT",
  "hitl_threshold": "$HITL_THRESHOLD"
}
EOF
    echo "Main state initialized at $MAIN_JSON"

elif [[ "$ACTION" == "main_end" ]]; then
    MAIN_JSON="$LOG_DIR/main.json"
    if [[ -f "$MAIN_JSON" ]]; then
        # Extract retro ghi if passed
        RETRO_GHI=""
        while [[ "$#" -gt 0 ]]; do
            case $1 in
                --retro-ghi) RETRO_GHI="$2"; shift ;;
            esac
            shift
        done
        
        # Use python to safely update the json
        python3 -c "
import json, sys
d = json.load(open('$MAIN_JSON'))
d['fanout_end_time'] = '$CURRENT_TIME'
if '$RETRO_GHI':
    d['retrospective_ghi'] = '$RETRO_GHI'
json.dump(d, open('$MAIN_JSON','w'), indent=2)
"
        echo "Main state finalized."
    else
        echo "Error: $MAIN_JSON not found."
    fi

elif [[ "$ACTION" == "review_start" ]]; then
    MAIN_JSON="$LOG_DIR/main.json"
    if [[ -f "$MAIN_JSON" ]]; then
        python3 -c "import json, sys; d=json.load(open('$MAIN_JSON')); d['review_start_time']='$CURRENT_TIME'; json.dump(d, open('$MAIN_JSON','w'), indent=2)"
        echo "Review phase started."
    else
        echo "Error: $MAIN_JSON not found."
    fi

elif [[ "$ACTION" == "review_end" ]]; then
    MAIN_JSON="$LOG_DIR/main.json"
    if [[ -f "$MAIN_JSON" ]]; then
        python3 -c "import json, sys; d=json.load(open('$MAIN_JSON')); d['review_end_time']='$CURRENT_TIME'; json.dump(d, open('$MAIN_JSON','w'), indent=2)"
        echo "Review phase finalized."
    else
        echo "Error: $MAIN_JSON not found."
    fi

elif [[ "$ACTION" == "sub_start" ]]; then
    if [[ -z "$ISSUE" || -z "$SHORT_UUID" ]]; then
        echo "Error: --issue and --short-uuid are required for sub_start."
        exit 1
    fi
    SUB_DIR="$LOG_DIR/ghi-$ISSUE"
    mkdir -p "$SUB_DIR"
    
    SUB_LOG="$SUB_DIR/state.md"
    GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")

    cat <<EOF > "$SUB_LOG"
fan_out_uuid: $SHORT_UUID

## Forensic Metadata
- **Start Time (UTC)**: $CURRENT_TIME
- **Hostname**: $HOSTNAME
- **User**: $USER
- **Git Branch**: $GIT_BRANCH
- **Git Commit**: $GIT_COMMIT
- **Custom Prompt**: $CUSTOM_PROMPT
- **HITL Threshold**: $HITL_THRESHOLD

EOF
    echo "Subagent state initialized at $SUB_LOG"

elif [[ "$ACTION" == "sub_end" ]]; then
    if [[ -z "$ISSUE" ]]; then
        echo "Error: --issue is required for sub_end."
        exit 1
    fi
    SUB_LOG="$LOG_DIR/ghi-$ISSUE/state.md"
    echo -e "\n## Execution End\n- **End Time (UTC)**: $CURRENT_TIME\n" >> "$SUB_LOG"
    echo "Subagent state finalized."

else
    echo "Unknown action: $ACTION. Valid actions: main_start, main_end, sub_start, sub_end"
    exit 1
fi
