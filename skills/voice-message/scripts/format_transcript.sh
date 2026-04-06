#!/bin/bash

# Default values
LANGUAGE=""
TRANSCRIPT=""

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --lang) LANGUAGE="$2"; shift ;;
        --transcript) TRANSCRIPT="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Validate input
if [ -z "$LANGUAGE" ] || [ -z "$TRANSCRIPT" ]; then
    echo "Usage: $0 --lang [it|en] --transcript \"...text...\""
    exit 1
fi

# Set emoji based on language
EMOJI=""
if [ "$LANGUAGE" = "it" ]; then
    EMOJI="🇮🇹"
elif [ "$LANGUAGE" = "en" ]; then
    EMOJI="🇬🇧"
else
    echo "Unsupported language: $LANGUAGE. Please use 'it' or 'en'."
    exit 1
fi

# Output the formatted transcript
echo "\`\`\`"
echo "---"
echo "$EMOJI $TRANSCRIPT $EMOJI"
echo "---"
echo "\`\`\`"
