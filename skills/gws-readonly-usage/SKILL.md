---
name: gws-readonly-usage
description: >-
  (💛) Google Workspace automation for extracting event details from readonly Gmail and creating Calendar events with the gws CLI.
compatibility: "gemini-cli, antigravity, openclaw"
metadata:
  version: "1.0.0"
---

# gws-readonly-usage 📬📅🦞

This skill provides a starting point for exploring and automating Google Workspace tasks using the `gws` CLI tool, specifically focusing on reading emails in read-only mode to automate calendar management safely.

## Workflows

### 1. Extracting Event Details from Emails (Read-Only Gmail)

Use `gws gmail +triage` or `gws gmail users messages list` to find relevant emails. Once you have a message ID, use `gws gmail users messages get` to extract details like:
- **Summary**: What is the event? (e.g., "Dinner at LUIGIA")
- **Date/Time**: When is it? (Check snippets or payload)
- **Location**: Where is it?
- **Attendees**: Who else is involved?

### 2. Creating Calendar Events

Once details are extracted, use `gws calendar +insert` to create the event:
- **Summary**: Title of the event
- **Start/End**: Use ISO 8601 format (e.g., `2026-03-06T20:00:00+01:00`)
- **Location**: Physical address or meeting link
- **Attendee**: Use `--attendee <EMAIL>` for each guest

## Best Practices
- **Readonly Gmail**: Always assume Gmail is read-only unless explicitly granted otherwise (blast-radius isolation against prompt injection).
- **Low-Risk Calendar**: Calendar additions are safe, reversible, and clearly tagged.
- **Security**: Never log sensitive email content to world-readable logs.

## Common Commands

```bash
# Last 20 emails:
$ gws gmail +triage --max 20 --query "is:anywhere"

# Search for restaurant reservation since a given date:
$ gws gmail +triage --query "LUIGIA after:2026-02-04" --max 50

# Events today and tomorrow:
$ gws calendar +agenda --days 2

# Events tomorrow:
$ gws calendar +agenda --tomorrow

# Events today and tomorrow cleaned up of recurring noise:
$ bash ./scripts/calendar-today-tomorrow.sh
```

### 🦞 Lobby's Event Creation Protocol
**Mandatory:** When creating a calendar event as an autonomous agent (e.g. Lobby 🦞), the summary (title) MUST always begin with an agent emoji (`🦞`) so the human user immediately recognizes agent-created events:
- **Correct:** `gws calendar +insert --summary "🦞 Dinner at Luigia"`
- **Incorrect:** `gws calendar +insert --summary "Dinner at Luigia"`

## Google Keep and Tasks

### Google Keep (Limited API Access)
The standard Google Keep API is primarily designed for enterprise management. For most personal or standard Workspace accounts, direct access via `gws keep` may return a `403 Forbidden` error (insufficient authentication scopes).

### Google Tasks Workaround
Many Keep reminders and notes are synced to Google Tasks:

```bash
# 1. Find the Task List ID
gws tasks tasklists list --format table

# 2. List tasks from a specific list (replace LIST_ID)
gws tasks tasks list --params '{"tasklist": "LIST_ID"}' --format table
```
