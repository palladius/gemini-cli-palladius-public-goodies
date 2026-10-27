#!/usr/bin/env bash
# chumbia_audit.sh — Non-destructive readiness & cleanup audit for the 'chumbia' skill.
# Also manages the '<GIT_ROOT>/.chumbia.touch' breadcrumb lock so 'git-disk-cleanup'
# can detect interrupted or incomplete '/chumbia' runs.
#
# Usage:
#   bash scripts/chumbia_audit.sh [repo_path]              # Start audit & write .chumbia.touch
#   bash scripts/chumbia_audit.sh --complete [repo_path]   # Remove .chumbia.touch upon Phase 4 completion

set -euo pipefail

MODE="audit"
if [ "${1:-}" = "--complete" ] || [ "${1:-}" = "--clear" ]; then
  MODE="complete"
  shift
fi

TARGET_DIR="${1:-.}"
cd "$TARGET_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "⚠️  Not inside a Git repository."
  exit 0
fi

GIT_ROOT="$(git rev-parse --show-toplevel)"
TOUCH_FILE="$GIT_ROOT/.chumbia.touch"

if [ "$MODE" = "complete" ]; then
  if [ -f "$TOUCH_FILE" ]; then
    rm -f "$TOUCH_FILE"
    echo "✅ Removed breadcrumb lock: $TOUCH_FILE (Chumbia completed cleanly!)"
  else
    echo "ℹ️  No $TOUCH_FILE present (already clean)."
  fi
  exit 0
fi

echo "=== 💃🕺🎺 CHUMBIA READINESS AUDIT ==="
echo "📂 Git Root: $GIT_ROOT"

if [ -f "$TOUCH_FILE" ]; then
  echo "🚨 WARNING: Found leftover $TOUCH_FILE from a previous interrupted/failed Chumbia run!"
  cat "$TOUCH_FILE" | sed 's/^/   /'
fi

BRANCH="$(git branch --show-current || echo 'DETACHED')"
cat > "$TOUCH_FILE" <<EOF
status: IN_PROGRESS
started_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
branch: $BRANCH
workdir: $(pwd)
pid: $$
EOF
echo "📌 Created breadcrumb lock: $TOUCH_FILE (will be removed in Phase 4 via --complete)"

git fetch --prune origin 2>/dev/null || true

echo "🌿 Current branch: $BRANCH"

echo ""
echo "--- 1. Working Tree Status ---"
# Ignore .chumbia.touch itself when checking porcelain status
STATUS_OUT="$(git status --porcelain | grep -v '\.chumbia\.touch$' || true)"
if [ -z "$STATUS_OUT" ]; then
  echo "✅ Working tree is clean."
else
  echo "🛑 Modified/untracked files present:"
  echo "$STATUS_OUT"
fi

if [ -d "$GIT_ROOT/.git/sequencer" ] || [ -f "$GIT_ROOT/.git/CHERRY_PICK_HEAD" ] || [ -f "$GIT_ROOT/.git/REBASE_HEAD" ]; then
  echo "🛑 Stale or active sequencer/cherry-pick/rebase state detected in .git/!"
fi

echo ""
echo "--- 2. Upstream & Merge Status ---"
if git show-ref --verify --quiet refs/remotes/origin/main; then
  MAIN_REF="origin/main"
elif git show-ref --verify --quiet refs/remotes/origin/master; then
  MAIN_REF="origin/master"
else
  MAIN_REF=""
fi

if [ -n "$MAIN_REF" ]; then
  UNPUSHED="$(git rev-list --count "${MAIN_REF}..HEAD" 2>/dev/null || echo 0)"
  if [ "$UNPUSHED" -eq 0 ]; then
    echo "✅ HEAD is merged into $MAIN_REF (0 unmerged commits)."
  else
    echo "🛑 HEAD has $UNPUSHED commit(s) NOT in $MAIN_REF!"
  fi
fi

echo ""
echo "--- 3. Git Worktrees ---"
git worktree list

echo ""
echo "--- 4. Merged Local & Remote Branches Eligible for Cleanup ---"
if [ -n "$MAIN_REF" ]; then
  echo "Local merged branches (excluding main/master):"
  git branch --merged "$MAIN_REF" | grep -vE '^\*|^\s*(main|master|gh-pages)$' || echo "  (none)"
  echo "Remote merged branches on origin (excluding main/master/gh-pages):"
  git branch -r --merged "$MAIN_REF" | grep -vE 'HEAD|origin/(main|master|gh-pages|production|release)' || echo "  (none)"
fi

echo ""
echo "--- 5. Justfile 'clean' Recipe & node_modules Check ---"
if [ -f justfile ] && command -v just >/dev/null 2>&1; then
  if just -l 2>/dev/null | grep -qE '^\s*clean\b'; then
    echo "🧹 'just clean' recipe IS available in justfile."
  else
    echo "ℹ️  No 'clean' recipe in justfile."
  fi
fi

find . -maxdepth 3 -name "node_modules" -type d -prune 2>/dev/null | while read -r nm; do
  echo "📦 Found node_modules: $nm ($(du -sh "$nm" 2>/dev/null | cut -f1))"
done
