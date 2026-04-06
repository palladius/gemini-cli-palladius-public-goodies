#!/bin/bash
# 🦞 Hummerli Pronunciation Script (with Workflow target support)

VOICE=""
TEXT=""
OCTTS="$HOME/.openclaw/workspace/bin/octts"

# Default target for Hummerli (Workflow channel)
export OCTTS_TARGET="${OCTTS_TARGET:-""}"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --male) VOICE="de-DE-ConradNeural"; shift ;;
        --female) VOICE="de-DE-KatjaNeural"; shift ;;
        -p) TEXT="$2"; shift 2 ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
done

if [[ -z "$VOICE" ]] || [[ -z "$TEXT" ]]; then
    echo "Usage: $0 [--male|--female] -p \"text to pronounce\""
    exit 1
fi

if [[ ! -x "$OCTTS" ]]; then
    echo "Error: octts not found at $OCTTS"
    exit 1
fi

# Call octts with the German voice
"$OCTTS" "$VOICE" "$TEXT"
