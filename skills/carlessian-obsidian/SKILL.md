---
name: carlessian-obsidian
description: "💛 Expert guide for interacting with Riccardo's Obsidian vault (The Carlessian Vault)."
---

# Carlessian Obsidian

This skill provides the knowledge and workflows to interact with your Obsidian vault, primarily in a headless or CLI environment.

## The Vault Structure

- **Path**: Usually `~/obsidian-pbt/` or similar.
- **Inbox**: New ideas or quick notes go into `Inbox/`.
- **Diary**: Daily logs are located in `Diary/YYYY-MM-DD.md`.

## Key Workflows

### 1. Adding a Daily Entry
To add a quick note to today's diary entry:
```bash
# Example script or manual append
date_today=$(date +%Y-%m-%d)
echo "- $(date +%H:%M) - My new entry" >> ~/obsidian-pbt/Diary/${date_today}.md
```

### 2. Processing the Inbox
Quick notes captured via mobile or other tools often land in `Inbox/`.
```bash
ls ~/obsidian-pbt/Inbox/
```

## Tools

### Obsidian Headless CLI
Used for syncing the vault on machines without a GUI.
```bash
# Sync the vault
ob sync --path ~/obsidian-pbt/
```

### Future Automation
Additional scripts for obsidian-related tasks can be found (or should be placed) in the `scripts/` subdirectory of this skill.

## Riccardo's Configuration
- **Primary Vault Name**: PBTPersonalSync
- **Default Path**: `~/obsidian-pbt/`

## Carlessian Conventione

* Generic TODOs should be characterized under `TODOs.md`
* Try to fit todos by computer in which they're given to you (hostname or Pixel 10, ... under Computers/)
* When something relevant happens on a computer (eg Riccardo installs a package, or a functionality, or changes something,) its IMPORTANT that you **log** it.

### Logging event on a computer

To log an event for cmputer HOSTANEM, find or create the `Computers/HOSTNAME.md` (dont use FQDN for brevity).
* Ensure the FQDN is on top of the note  `Computers/HOSTNAME.md` 
* Add a `Computers/HOSTNAME/log.md` if doesnt exist.
* Add on top (reverse append) a bullet point line with:

```
* `YYYYMMDD HH:MM` [YOUR_EMOJI] `[AGENT_NAME]` Line that you want to log, and maybe details on how you got this (did Riccardo tell you? Did Riccardo tell you write it, or it told you soemthing else and you decided this was relevant?). Keep it short but still meaningful
```

* YOUR_EMOJI should be your personality, a lobster if you're openclaw, or a Gemini zodiac sign if you're Gemini, or 🛰 if you're AntiGravity.
* AGENT_NAME should be in backticks and should be your program, to separate from a human: Gemini CLI, Antigravity, Lobby, Gamberone, or whatever fits best. IT's the agent name.