---
name: Git Coding Best Practices
description: (💛) Core guidelines for interacting with git repositories, updating CHANGELOGs, and safely bumping versions. Use this skill whenever proposing or executing git commits, pushing code, or making destructive file changes.
tags: git, development, best-practices
version: 0.0.2
---

# Git Coding Best Practices

## Overview
This skill provides the mandatory guidelines for executing git operations, ensuring safe repository management, and correctly formatting commits and releases.

## Core Mandates

### 1. No Destructive Commands

**NEVER** use destructive git commands such as `git clean -fd`, `git reset --hard`, or `git push --force`.
Untracked files may contain active, uncommitted work by the user or other agents.
- **Rule of Thumb:** If you need to revert or clean up, only use surgical `rm` commands on the exact files you created. If you are unsure about untracked files, always ask the user before deleting them.

### 2. The Pre-Commit Checklist

Before proposing or executing any `git commit`, you must perform the following two actions in the repository:
1. **Bump Version:** Find the main configuration file containing the version (e.g., `gemini-extension.json`, `package.json`, etc.) and increment it according to Semantic Versioning (usually a patch bump, like `0.1.4` -> `0.1.5`).
2. **Update CHANGELOG.md:** Add a new entry to the `CHANGELOG.md` file documenting the changes under the new version header. Follow the `[Keep a Changelog]` format.

### 3. Commit Message Formatting
- Start by gathering context: `git status`, `git diff HEAD`, and `git log -n 3` to match the existing commit style.
- Prefer commit messages that are clear, concise, and focused more on "why" than "what".
- If the repository uses `gitmoji`, use the appropriate emoji in the commit title (e.g., 🐛 for bugs, ✨ for features,  chore, etc.).

### 4. Push Etiquette
- **NEVER** push changes to a remote repository automatically unless explicitly requested by the user.

### 5. Renaming

* prefer `git mv` to `mv` if file is under version control.

## Workflow Example

When asked to "commit the recent changes":

1. Check `git status` and `git diff`.
2. Find the version file and bump it.
3. Add the changes to `CHANGELOG.md`.
4. Stage the files (`git add ...`).
5. Propose the commit message to the user or execute it if given permission.
6. Ensure to attach GH issue if available the messages. If so also comment on the issue post-commit/push with a digest of what has been done. It reads nicely.
