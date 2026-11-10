#!/usr/bin/env bash
# chumbia_audit.sh — Non-destructive readiness & cleanup audit for the 'chumbia' skill.
# Supports human-readable output, --json machine-readable output for MCP/JEV auto-archive,
# and --complete for clearing the breadcrumb lock.
#
# Usage:
#   bash scripts/chumbia_audit.sh [repo_path]              # Start audit & write .chumbia.touch (Human output)
#   bash scripts/chumbia_audit.sh --json [repo_path]        # Machine-readable JSON output (exit 0 if ready, exit 1 if not)
#   bash scripts/chumbia_audit.sh --complete [repo_path]    # Remove .chumbia.touch upon Phase 4 completion

set -euo pipefail

FORMAT="human"
MODE="audit"
TARGET_DIR="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --complete|--clear)
      MODE="complete"
      shift
      ;;
    --json)
      FORMAT="json"
      shift
      ;;
    *)
      TARGET_DIR="$1"
      shift
      ;;
  esac
done

cd "$TARGET_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [ "$FORMAT" = "json" ]; then
    echo '{"chumbia_ready": false, "error": "Not inside a Git repository", "exit_code": 1}'
  else
    echo "⚠️  Not inside a Git repository."
  fi
  exit 1
fi

GIT_ROOT="$(git rev-parse --show-toplevel)"
GIT_DIR="$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)"
GIT_COMMON="$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)"
IS_WORKTREE=false
if [ "$GIT_DIR" != "$GIT_COMMON" ]; then
  IS_WORKTREE=true
fi

TOUCH_FILE="$GIT_ROOT/.chumbia.touch"

if [ "$MODE" = "complete" ]; then
  if [ -f "$TOUCH_FILE" ]; then
    rm -f "$TOUCH_FILE"
    if [ "$FORMAT" = "json" ]; then
      echo '{"status": "completed", "touch_file_removed": true}'
    else
      echo "✅ Removed breadcrumb lock: $TOUCH_FILE (Chumbia completed cleanly!)"
    fi
  else
    if [ "$FORMAT" = "json" ]; then
      echo '{"status": "already_clean", "touch_file_removed": false}'
    else
      echo "ℹ️  No $TOUCH_FILE present (already clean)."
    fi
  fi
  exit 0
fi

BRANCH="$(git branch --show-current || echo 'DETACHED')"

# Manage breadcrumb touch file
cat > "$TOUCH_FILE" <<TOUCH_EOF
status: IN_PROGRESS
started_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
branch: $BRANCH
workdir: $(pwd)
is_worktree: $IS_WORKTREE
pid: $$
TOUCH_EOF

git fetch --prune origin 2>/dev/null || true

# Determine Main ref
if git show-ref --verify --quiet refs/remotes/origin/main; then
  MAIN_REF="origin/main"
elif git show-ref --verify --quiet refs/remotes/origin/master; then
  MAIN_REF="origin/master"
else
  MAIN_REF=""
fi

# Gate 1: Working tree
STATUS_OUT="$(git status --porcelain | grep -v '\.chumbia\.touch$' || true)"
WORKING_TREE_CLEAN=true
if [ -n "$STATUS_OUT" ]; then
  WORKING_TREE_CLEAN=false
fi

# Gate 2: Sequencer
SEQUENCER_CLEAN=true
if [ -d "$GIT_ROOT/.git/sequencer" ] || [ -f "$GIT_ROOT/.git/CHERRY_PICK_HEAD" ] || [ -f "$GIT_ROOT/.git/REBASE_HEAD" ]; then
  SEQUENCER_CLEAN=false
fi

# Gate 3: Upstream merge/ancestor check
MERGED_TO_MAIN=false
UNPUSHED_COMMITS=0
CHERRY_UNMERGED_COUNT=0

if [ -n "$MAIN_REF" ]; then
  UNPUSHED_COMMITS="$(git rev-list --count "${MAIN_REF}..HEAD" 2>/dev/null || echo 0)"
  if [ "$UNPUSHED_COMMITS" -eq 0 ]; then
    MERGED_TO_MAIN=true
  else
    # Fallback for squashed or cherry-picked worktrees
    CHERRY_UNMERGED_COUNT="$(git cherry -v "$MAIN_REF" HEAD 2>/dev/null | grep -v '^-' | wc -l || echo 99)"
    if [ "$CHERRY_UNMERGED_COUNT" -eq 0 ]; then
      MERGED_TO_MAIN=true
    fi
  fi
fi

# Gate 4: Test suite (if just test exists)
HAS_TEST_RECIPE=false
if [ -f justfile ] && command -v just >/dev/null 2>&1; then
  if just -l 2>/dev/null | grep -qE '^\s*test\b'; then
    HAS_TEST_RECIPE=true
  fi
fi

# Overall readiness decision
CHUMBIA_READY=false
if [ "$WORKING_TREE_CLEAN" = true ] && [ "$SEQUENCER_CLEAN" = true ] && [ "$MERGED_TO_MAIN" = true ]; then
  CHUMBIA_READY=true
fi

if [ "$FORMAT" = "json" ]; then
  cat <<JSON_EOF
{
  "chumbia_ready": $CHUMBIA_READY,
  "git_root": "$GIT_ROOT",
  "branch": "$BRANCH",
  "is_worktree": $IS_WORKTREE,
  "main_ref": "$MAIN_REF",
  "gates": {
    "working_tree_clean": $WORKING_TREE_CLEAN,
    "sequencer_clean": $SEQUENCER_CLEAN,
    "merged_to_main": $MERGED_TO_MAIN,
    "unpushed_commits": $UNPUSHED_COMMITS,
    "cherry_unmerged_count": $CHERRY_UNMERGED_COUNT,
    "has_test_recipe": $HAS_TEST_RECIPE
  },
  "lockfile": "$TOUCH_FILE"
}
JSON_EOF
  if [ "$CHUMBIA_READY" = true ]; then
    exit 0
  else
    exit 1
  fi
fi

# Human-readable format
echo "=== 💃🕺🎺 CHUMBIA READINESS AUDIT ==="
echo "📂 Git Root: $GIT_ROOT"
echo "🌿 Current branch: $BRANCH (is_worktree: $IS_WORKTREE)"
echo ""
echo "--- 1. Working Tree & Sequencer ---"
if [ "$WORKING_TREE_CLEAN" = true ]; then
  echo "✅ Working tree is clean."
else
  echo "🛑 Modified/untracked files present:"
  echo "$STATUS_OUT"
fi

if [ "$SEQUENCER_CLEAN" = true ]; then
  echo "✅ Sequencer clean (no stale rebase/cherry-pick)."
else
  echo "🛑 Stale or active sequencer state detected in .git/!"
fi

echo ""
echo "--- 2. Upstream & Merge Status ($MAIN_REF) ---"
if [ "$MERGED_TO_MAIN" = true ]; then
  echo "✅ HEAD is merged into $MAIN_REF."
else
  echo "🛑 HEAD has unmerged commits ($UNPUSHED_COMMITS unpushed, $CHERRY_UNMERGED_COUNT unpatched)."
fi

echo ""
echo "--- 3. Git Worktrees ---"
git worktree list

echo ""
echo "========================================"
if [ "$CHUMBIA_READY" = true ]; then
  echo "🎉 CHUMBIA READY: TRUE (Tutti i gate superati!)"
else
  echo "🛑 CHUMBIA READY: FALSE (Completare i gate pendenti prima di chiudere)"
fi
echo "========================================"
