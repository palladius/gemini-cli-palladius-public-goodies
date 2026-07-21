---
name: carlessian-obsidian
description: "💛 Expert guide for interacting with Riccardo's Obsidian vault (The Carlessian Vault). (Includes TODOs and CLI setup)"
compatibility: Gemini CLI
metadata:
  version: 1.0.0
tags: Lobby
---
# Carlessian Obsidian

This skill provides the knowledge and workflows to interact with your Obsidian vault, primarily in a headless or CLI environment.

## The Vault Structure

- **Path**: Usually `~/obsidian-pbt/` or similar.
- **Inbox**: New ideas or quick notes go into `Inbox/`.
- **Diary**: Daily logs are located in `Diary/YYYY-MM-DD.md`.
- **TODOs**: The canonical to-do list is located at `TODOs/TODOz.md` or `Computers/COMPUTER_NAME/TODOs.md`.

## Key Workflows

### 1. Adding a Daily Entry
To add a quick note to today's diary entry:
```bash
date_today=$(date +%Y-%m-%d)
echo "- $(date +%H:%M) - My new entry" >> ~/obsidian-pbt/Diary/${date_today}.md
```

### 2. Processing the Inbox
Quick notes captured via mobile or other tools often land in `Inbox/`.
```bash
ls ~/obsidian-pbt/Inbox/
```

### 3. Riccardo's To-Do Management Protocol
When managing To-Do lists:
1. Target File: `~/obsidian-pbt/TODOs/TODOz.md`. For computer-specific tasks, use `Computers/HOSTNAME/TODOs.md`.
2. Find or Create: If not exists, create with title `# Riccardo's To-Do List`.
3. Date Heading: Check if `## YYYY-MM-DD` exists for today. If not, prepend it below the main title.
4. Format: `[PRIORITY] - [ ] [TASK_DESCRIPTION] [TAGS]`
   * **Priority Emoji:** 🔴 `Red` (Urgent), 🟠 `Orange` (High), 🟡 `Yellow` (Medium), 🟢 `Green` (Low), ⚪️ `White` (Default)
   * **Category Tags:** `#salute`, `#lavoro`, `#casa`
   * **Emojis:** 🦞 `Lobby` (Lobby-related), 🧑‍⚕️ `Health`, 💻 `Tech`.

### 4. Logging event on a computer
To log an event for computer HOSTNAME, find or create `Computers/HOSTNAME/log.md`:
* Ensure the FQDN is on top of the note `Computers/HOSTNAME.md`
* Reverse append a bullet point with:
  `* YYYYMMDD HH:MM [YOUR_EMOJI] [AGENT_NAME] Short meaningful description.`
* YOUR_EMOJI: 🦞 for Openclaw/Lobby, 🛰 for Antigravity, or Gemini sign. Sign yourself as Lobby unless obvious.

## Tools

### Agent Obsidian Plugins
As an agent, you have access to the newly installed `obsidian-skills` plugin (including `obsidian-cli`, `defuddle`, and `json-canvas`) to programmatically manage notes, extract web content, and parse canvas files in this vault.

### Obsidian Headless CLI (obsidian-headless)
For machines without a GUI:
```bash
npm install -g obsidian-headless
ob login --email palladiusbonton@gmail.com
ob sync-setup --vault PBTPersonalSync --path ~/obsidian-pbt/
ob sync --path ~/obsidian-pbt/
```

## Carlessian Conventions

* **Universal Router:** Consult `carlessian-harness-tool` before executing complex tasks.
* Try to fit todos by computer in which they're given to you (under Computers/).
* If it's related with my health, put it under `Salute/`.
* Proactively propose fixes for deduplication or inconsistencies.
* Ensure `.bashrc` has `CARLESSIAN_OBSIDIAN_PATH` pointing to the real path. If `~/obsidian-pbt` doesn't exist, create it as a symlink to the original path.
