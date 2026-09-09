#!/usr/bin/env bash
set -euo pipefail

# preview_slide.sh
# Renders a specific slide from a Marp markdown presentation as a PNG image.
# Usage: ./preview_slide.sh <path-to-markdown> <slide-number> [output-image-path]

if [ $# -lt 2 ]; then
  echo "Usage: $0 <path-to-markdown> <slide-number> [output-png-path]" >&2
  echo "Example: $0 slides/index.md 3 /tmp/slide-3.png" >&2
  exit 1
fi

SLIDES_MD="$1"
SLIDE_NUM="$2"
OUTPUT_PNG="${3:-}"

if [ ! -f "$SLIDES_MD" ]; then
  echo "Error: Markdown file not found: $SLIDES_MD" >&2
  exit 1
fi

# Detect marp CLI
if command -v marp >/dev/null 2>&1; then
  MARP_BIN="marp"
elif command -v npx >/dev/null 2>&1; then
  MARP_BIN="npx -y @marp-team/marp-cli"
else
  echo "Error: Neither 'marp' nor 'npx' is available in PATH." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d -t marp-slide-preview-XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT

# Render all slides to numbered PNGs
# Notice: --allow-local-files is required when images/assets are referenced locally
$MARP_BIN "$SLIDES_MD" --images png --image-scale 1 --allow-local-files --html -o "$TMP_DIR/slide.png" >/dev/null 2>&1

# Zero-padded 3-digit index formatted by Marp (001, 002, 003, ...)
PADDED_NUM="$(printf "%03d" "$SLIDE_NUM")"
RENDERED_SLIDE="$TMP_DIR/slide.$PADDED_NUM.png"

if [ ! -f "$RENDERED_SLIDE" ]; then
  echo "Error: Slide $SLIDE_NUM does not exist in $SLIDES_MD (expected: $RENDERED_SLIDE)" >&2
  exit 2
fi

if [ -n "$OUTPUT_PNG" ]; then
  mkdir -p "$(dirname "$OUTPUT_PNG")"
  cp "$RENDERED_SLIDE" "$OUTPUT_PNG"
  echo "$OUTPUT_PNG"
else
  cat "$RENDERED_SLIDE"
fi
