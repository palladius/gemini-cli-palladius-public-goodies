# Common Errors & Solutions

This document serves as a knowledge base for agents executing the `ghi-fan-out-coding` skill. 
If you encounter a blocking error, check this list to see if a known solution exists before failing the issue.

## 1. `app_not_running`
**Description**: The local rails application or dev server is not running (e.g., connection refused on port 8080, or another service is answering).
**Solution**: As an agent, you are explicitly instructed *not* to start long-running servers manually unless strictly necessary. If tests require the app to be running and it is not, you MUST fail and request the human operator to start the application (e.g., using `just dev` or `bin/dev`) before executing UI tests. If you DO need to start a server, use a deterministic port (see `port_occupied` below).

## 2. `port_occupied`
**Description**: Port 8080 (or another common port) is already in use, typically because the main app or another concurrent subagent is already bound to it.
**Solution**: When running a web app from a worktree, you MUST use a **deterministic port** based on the issue number to avoid collisions:
```
PORT = 48000 + ISSUE_NUMBER
```
For example: GHI #25 → port `48025`, GHI #123 → port `48123`. This ensures all concurrent subagents get a unique, predictable port. Use this port when starting any dev server (e.g., `rails server -p 48025`, `npm run dev -- --port 48123`).

## 3. `missing_playwright`
**Description**: The agent attempted to run UI tests or verify frontend changes but failed because it fell back to basic HTTP tools like `curl` and `web_fetch`, which cannot execute JavaScript or interact with the page.
**Solution**: Use the `scripts/playwright_hello.js` template from this skill as a starting point. Copy it into your worktree, adapt it for your GHI, and run it with `node`. Install dependencies first with `npm install playwright && npx playwright install chromium`. This works on both macOS and Linux without needing MCP configuration. Remember to use the deterministic port (`48000 + ISSUE_NUMBER`) when navigating. If login is needed, pass `--user` and `--pass` flags — check `.env` for `PLAYWRIGHT_USERNAME` and `PLAYWRIGHT_PASSWORD`.

## 4. `missing_context`
**Description**: The issue requests creating documents (Google Docs, slide decks) or fixing a bug with an extremely vague description (e.g., "first chat unresponsive") without providing templates, content, or reproduction steps.
**Solution**: These tasks require human intervention. You cannot guess the context. You must immediately add the `fanout-couldnt-complete` label, fail the issue, and leave a comment asking the author to provide links to templates, specify where documents should be created, or provide clear reproduction steps/error logs.
