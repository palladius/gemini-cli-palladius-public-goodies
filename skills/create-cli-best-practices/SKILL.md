---
name: create-cli-best-practices
description: Rules to create and maintain a GOOD CLI. Do not use for GUI-only design rules, web apps, or backend REST APIs.
compatibility: Antigravity / Gemini CLI
metadata:
  version: 0.1.15
---

Implement the CLI in `rust` or `go`.
Document any carlessian CLI in $GIC/ under installables.

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
* **Execution Speed & Performance:** Build blazing fast Rust/Go CLIs (target <100ms startup) and keep list/default commands instantaneous (redirecting slow 10s+ default commands to help) by caching slow tasks locally (1h/1d duration) or placing long-running operations explicitly in the command name.

Ensure all commands support the following flags:

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
* **Pagination:** Support pagination parameters to help agents and humans navigate large data sets without blowing their context window or screen buffer. Use standard flags like `--max-items 100` and `--page 2` to retrieve the second batch (items 101-200).
* **Idempotency & exit codes:** Make commands idempotent (e.g., like `kubectl apply`). If a conflict exists, return unique exit codes (like `5` for "already exists") to facilitate programmatic recovery.
* **Composability (`--quiet` / `-q`):** Output bare values (one per line, no decorative borders, no tables) for easy piping into other commands or shell scripts.
* **Non-Interactive Bypasses (`--yes`, `--force`, or `--non-interactive`):** Allow bypassing human prompt queries. Always fail-fast or auto-bypass prompts when `stdin` is not a TTY (non-interactive terminals) to avoid hanging the agent. When a command requires interaction, explicitly document how to bypass it (e.g., "Warning: this part is interactive. To avoid interaction, ensure that `ENV[PINCO]` and `ENV[PALLO]` are set, or use `--force`").
* **Actionable Errors:** Ensure errors return machine-parseable strings (like `image_not_found` in the JSON/stderr payload), output the failing input, and provide suggestions/remediation commands.
* **AI-Specific Help (`--ai-help`):** Every CLI tool MUST have both a `--help` (for humans) and `--ai-help` (for AI). The `--ai-help` flag should output Markdown and provide:
  1. **Uses of the CLI for AI vs Human:** Explain how an AI should use the CLI differently from a human (e.g., advising the AI to call with `--json`, `--format=json | jq`, or `--quiet`).
  2. **Added Context:** Provide all relevant context in Markdown, such as where the script is located, where it is built, where additional context or documentation can be found, and references to any related skills.
  The standard `--help` output MUST mention the availability of `--ai-help` so agents can easily discover it.

# LLM Support

Do not run LLM calls implicitly or block executions indefinitely on rogue AI completions. Adhere to the Principle of Least Astonishment (POLA). Signify any LLM usage explicitly:

* `--llm-classify` or similar flags.
* `--long-running-summarization` to signal high execution latency to the user.

# Terminal Emoji Alignment

Based on lessons learned from the `obpbt` CLI, aligning emojis in tabular terminal layouts can be difficult due to variations in display widths.

## The Problem

Emojis have inconsistent terminal widths. While standard characters use 1 column, most emojis are wide and use 2 columns. However, some emojis (e.g., ⚔, 🛡, ⛏) are "narrow" (1 column). Furthermore, variation selectors (like U+FE0F, which forces emoji presentation) are often appended to narrow emojis, causing standard string length or terminal width calculators to miscount the visual width, breaking column alignment.

## The Solution

To ensure immaculate table and listing alignment when using emojis:
* **Measure Display Width:** Use standard libraries (like `unicode-width` in Rust or `go-runewidth` in Go) to measure the display width of a string rather than its character count.
* **Strip Variation Selectors:** Remove U+FE0F variation selectors before measuring the width, as they often confuse width-calculation libraries.
* **Provide a Padding Helper:** Create a reusable `pad_display(text, target_width)` helper function that calculates the visible width and pads with the exact number of spaces needed.
* **Swap Narrow Emojis:** Keep a list of known narrow-width emojis and avoid using them in columnar layouts. Swap narrow emojis for wide alternatives whenever possible.

## Golden Code Snippets

### Rust (using `unicode-width`)

First, ensure you have the dependency in `Cargo.toml`:

```toml
[dependencies]
unicode-width = "0.1.11"
```

Then, implement the padding helper:

```rust
use unicode_width::UnicodeWidthStr;

/// Returns the display width of a string, ignoring the U+FE0F variation selector.
pub fn display_width(s: &str) -> usize {
    // Strip the variation selector before calculating width
    let stripped = s.replace('\u{fe0f}', "");
    stripped.width()
}

/// Pads a string to a target display width.
pub fn pad_display(s: &str, target_width: usize) -> String {
    let width = display_width(s);
    if width >= target_width {
        s.to_string()
    } else {
        let padding = " ".repeat(target_width - width);
        format!("{}{}", s, padding)
    }
}
```

### Go (using `go-runewidth`)

```go
package main

import (
	"strings"

	"github.com/mattn/go-runewidth"
)

// DisplayWidth returns the visible width of a string in a terminal,
// stripping the U+FE0F variation selector first.
func DisplayWidth(s string) int {
	stripped := strings.ReplaceAll(s, "\ufe0f", "")
	return runewidth.StringWidth(stripped)
}

// PadDisplay pads a string with spaces to reach the target width.
func PadDisplay(s string, targetWidth int) string {
	width := DisplayWidth(s)
	if width >= targetWidth {
		return s
	}
	padding := strings.Repeat(" ", targetWidth-width)
	return s + padding
}
```

### Output Example

Before (broken alignment due to standard char counting):
```text
Item        Status
Sword ⚔️    Equipped
Shield 🛡️   Unequipped
Axe 🪓       Unequipped
```

After (using padding helpers and wide replacements):
```text
Item        Status
Sword 🗡️     Equipped
Shield 🏰   Unequipped
Axe 🪓      Unequipped
```

## Bad Emoji Database

The following emojis are known to be narrow (1 col) or cause width calculation issues due to variation selectors. Avoid them in aligned columns and use their wide (2 col) alternatives:

| Concept | Bad (Narrow / 1 col) | Good Alternative (Wide / 2 cols) |
|---|---|---|
| Sword / Attack | ⚔ (U+2694) | 🗡 (U+1F5E1) |
| Shield / Defense | 🛡 (U+1F6E1) | 🏰 (U+1F3F0) |
| Warning / Alert | ⚠ (U+26A0) | 🚨 (U+1F6A8) |
| Time / Clock | ⌚ (U+231A) | ⏰ (U+23F0) |
| Checkmark | ✔ (U+2714) | ✅ (U+2705) |
| Cross / X | ✖ (U+2716) | ❌ (U+274C) |
| Star | ⭐ (U+2B50) | 🌟 (U+1F31F) |
| Pickaxe | ⛏ (U+26CF) | 🪓 (U+1FA93) |

# Readings

* [Writing CLI Tools That AI Agents Actually Want to Use](https://dev.to/uenyioha/writing-cli-tools-that-ai-agents-actually-want-to-use-39no) (Ugo Enyioha)
* [Stop Wasting 89% of Your AI Agent's Tokens on CLI Noise](https://alies.dev/articles/cli-output-for-ai/) (Alies Lapatsin) — Useful, but not too much unless you write PHP.
* [no-color.org](https://no-color.org) — The `NO_COLOR` standard