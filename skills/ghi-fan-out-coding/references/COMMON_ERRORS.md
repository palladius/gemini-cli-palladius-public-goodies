# Common Errors & Solutions

This document serves as a knowledge base for agents executing the `ghi-fan-out-coding` skill. 
If you encounter a blocking error, check this list to see if a known solution exists before failing the issue.

## 1. `app_not_running`
**Description**: The local rails application or dev server is not running (e.g., connection refused on port 8080, or another service is answering).
**Solution**: As an agent, you are explicitly instructed *not* to start long-running servers manually unless strictly necessary. If tests require the app to be running and it is not, you MUST fail and request the human operator to start the application (e.g., using `just dev` or `bin/dev`) before executing UI tests.

## 2. `missing_playwright`
**Description**: The agent attempted to run UI tests or verify frontend changes but failed because it fell back to basic HTTP tools like `curl` and `web_fetch`, which cannot execute JavaScript or interact with the page.
**Solution**: Ensure you are using the correct browser tools. If the task requires UI interaction (clicking, waiting for elements, taking screenshots), you must use the `browser_subagent` or Playwright MCP instead of basic HTTP fetching.

## 3. `missing_context`
**Description**: The issue requests creating documents (Google Docs, slide decks) or fixing a bug with an extremely vague description (e.g., "first chat unresponsive") without providing templates, content, or reproduction steps.
**Solution**: These tasks require human intervention. You cannot guess the context. You must immediately add the `fanout-couldnt-complete` label, fail the issue, and leave a comment asking the author to provide links to templates, specify where documents should be created, or provide clear reproduction steps/error logs.
