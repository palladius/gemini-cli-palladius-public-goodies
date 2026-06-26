---
name: create-cli-best-practices
description: Rules to create and maintain a GOOD CLI
compatibility: Antigravity / Gemini CLI
metadata:
  version: 0.1.6
---

A good CLI should be implemented in `rust` or `go`.
A carlessian CLI should also be documented in $GIC/ under installables.

# Language-Specific Recommendations

## Golang (Go)

Recommended tools and libraries:
* **Flags & Config:** Use [Cobra](https://github.com/spf13/cobra) (potentially combined with [Viper](https://github.com/spf13/viper) for configuration management) if you want to have subcommands, multiple flags, config file support, etc.
* **Terminal UIs (TUIs):** [Bubble Tea](https://github.com/charmbracelet/bubbletea) from Charm is **highly suggested** if Go is the language you choose! It makes building beautiful, interactive terminal user interfaces extremely clean, structured, and easy (following the Elm architecture).

# Convention on CLI

* **Keep Files Small:** Prefer smaller files/modules to a single big monolithic file. It'll be harder to manage in rebases.
* **Honor NO_COLOR:** Always honor the `NO_COLOR` environment variable (as per [no-color.org](https://no-color.org)).
* **Watch Mode Compatibility:** Make sure the CLI works well in `watch` scenarios (e.g., handling rapid polling, disabling terminal clearing or color escape sequences if they break watch mode).
* **Deterministic Ordering:** Always sort outputs (sets/lists/fields) deterministically to prevent glitches in `watch <cli>` and noisy diffs in structured output (JSON/YAML).

All commands should have:

* `--help` / `-h`: Shows comprehensive usage and help.
* `--version` / `-v`: Shows the version. Ideally, check if the version is the latest at startup (if this can be done extremely fast, e.g., local version file or quick curl from public GitHub).
* `--dry-run` / `-n`: Allows users and agents to preview mutations without executing them. Output structured JSON detailing what would change.

# Riccardo-Specific Rules

1. **Colors:** Use colors! For frequently run or critical actions, use **WHITE** or **YELLOW**. For interesting/optional outputs, use **CYAN**.
2. **Terminal Standards:** Align with Linux directory coloring standards (e.g., green for executables, blue for directories).
3. **Emojis:** Use emojis to convey status and metadata (e.g., folder emojis, color status indicators for priorities).
4. **Emoji Safety:** Choose cross-platform emojis. Avoid flag emojis (which don't render well on some OSs) and be mindful that wide/multibyte emojis can disrupt tab/column alignment.
5. **Layout:** Ensure table and listing alignment is immaculate.

# AI-Friendly CLI Patterns

Since AI agents are prime consumers of command-line tools, design the CLI to be AI-friendly:

* **Format Options (`--format`):** Support structured output (`json`, `yaml`, `csv`). AIs parse JSON easily, while humans prefer YAML. Allow colors to be disabled via `--no-color` or `NO_COLOR=1`.
* **Pagination:** Support pagination parameters (e.g., page index and page size) to help agents navigate large data sets without blowing their context window.
* **Idempotency & exit codes:** Make commands idempotent (e.g., like `kubectl apply`). If a conflict exists, return unique exit codes (like `5` for "already exists") to facilitate programmatic recovery.
* **Composability (`--quiet` / `-q`):** Output bare values (one per line, no decorative borders, no tables) for easy piping into other commands or shell scripts.
* **Non-Interactive Bypasses (`--yes` / `--force`):** Allow bypassing human prompt queries. Always fail-fast or auto-bypass prompts when stdin is not a TTY (non-interactive terminals) to avoid hanging the agent.
* **Actionable Errors:** Errors should return machine-parseable strings (like `image_not_found` in the JSON/stderr payload), output the failing input, and provide suggestions/remediation commands.
* **AI-Specific Help (`--ai-help`):** Provide a dedicated help option designed specifically for AI agents (explaining API structures, schemas, integration constraints, and formatting rules). The standard `--help` output should mention the availability of `--ai-help` so agents can easily discover it.

# LLM Support

Do not run LLM calls implicitly or block executions indefinitely on rogue AI completions. Adhere to the Principle of Least Astonishment (POLA). Signify any LLM usage explicitly:

* `--llm-classify` or similar flags.
* `--long-running-summarization` to signal high execution latency to the user.

# Readings

* [Writing CLI Tools That AI Agents Actually Want to Use](https://dev.to/uenyioha/writing-cli-tools-that-ai-agents-actually-want-to-use-39no) (Ugo Enyioha)
* [Stop Wasting 89% of Your AI Agent's Tokens on CLI Noise](https://alies.dev/articles/cli-output-for-ai/) (Alies Lapatsin) — Useful, but not too much unless you write PHP.
* [no-color.org](https://no-color.org) — The `NO_COLOR` standard