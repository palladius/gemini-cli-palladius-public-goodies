#!/usr/bin/env bash
# security_review.sh
# Reviews an existing repository to ensure it has Romin's security goodies.

REPO_DIR="${1:-.}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🛡️ Starting Romin Security Review for $REPO_DIR"

if ! command -v pre-commit &> /dev/null || ! command -v gitleaks &> /dev/null; then
    echo "⚠️  Missing required tools: pre-commit and/or gitleaks"
    echo "Please install them first:"
    echo "  Mac:   brew install pre-commit gitleaks"
    echo "  Linux: brew install pre-commit gitleaks # (or use apt/pacman/etc)"
    echo ""
fi
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "⚠️ Not a git repository. Please run inside a git repo."
    exit 1
fi

MISSING=0

check_file() {
    local file=$1
    if [ ! -f "$REPO_DIR/$file" ]; then
        echo "❌ Missing: $file"
        MISSING=1
    else
        echo "✅ Found: $file"
    fi
}

check_file ".gitignore"
check_file ".gitleaks.toml"
check_file ".pre-commit-config.yaml"
check_file ".env.example"
check_file ".github/workflows/security-scan.yml"

if grep -q "gitleaks" "$REPO_DIR/.pre-commit-config.yaml" 2>/dev/null; then
    echo "✅ gitleaks is configured in .pre-commit-config.yaml"
else
    echo "❌ gitleaks is missing from .pre-commit-config.yaml"
    MISSING=1
fi

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "⚠️ Your repository is missing some of Romin's security goodies."
    echo "You can copy them from the template folder: $SKILL_DIR/template"
    echo "Command to copy all goodies into your repo:"
    echo "cp -r $SKILL_DIR/template/.* $SKILL_DIR/template/* \"$REPO_DIR/\" 2>/dev/null || true"
else
    echo ""
    echo "🎉 Your repository looks secure with all the goodies!"
fi
