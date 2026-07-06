# Riccardo's Public Antigravity & Gemini CLI Goodies 💡 (💛)

Self: https://github.com/palladius/gemini-cli-palladius-public-goodies

This repository contains Riccardo's personal public Antigravity plugins and agent skills. Feel free to look for inspiration, but these are tailored to Riccardo's specific needs and preferences (e.g., "Riccardo knows Ruby but not JavaScript"), and are not intended for general installation.

## Plugin & Extension Compatibility

This repository functions as a native plugin/extension across multiple agent ecosystems:

### 1. Antigravity UI & `agy` CLI
*   **Workspace-Level**: Clone or symlink this directory into `.agents/plugins/palladius-public-goodies/` at the root of your workspace.
*   **Global-Level**: Clone or symlink this directory into `~/.gemini/config/plugins/palladius-public-goodies/`.
*   **Verification**: Check active plugins and skills inside the CLI/UI using:
    ```bash
    agc plugins
    agc skills
    ```

### 2. Claude Code
*   **Workspace-Level**: Place or symlink this repository folder inside `.claude/plugins/palladius-public-goodies/` at the root of your workspace.
*   **Global-Level**: Run Claude Code with the plugin directory flag pointing to this repo:
    ```bash
    claude --plugin-dir /path/to/gemini-cli-palladius-public-goodies
    ```
*   Claude Code will automatically recognize `.claude-plugin/plugin.json` and load the skills under the `/palladius-public-goodies:` namespace.

### 3. OpenAI Codex
*   This extension is fully Codex-compatible (uses the `.codex-plugin/plugin.json` manifest).

### 4. Legacy: Gemini CLI
*   Installable via the classic extension system (requires Gemini CLI v`0.4.0` or newer):
    ```bash
    gemini extensions install https://github.com/palladius/gemini-cli-palladius-public-goodies
    ```

## Skills

This extension includes the following **[Agent Skills](https://antigravity.google/docs/skills)**:

*   **`add-to-portfolio-app`**: Adds a new Talk or Article to Riccardo's personal portfolio application.
*   **`adk-python`**: Create and manage AI agents using Google's Agent Development Kit (ADK) for Python.
*   **`article-creator`**: (🥑) Expert guide for authoring, building, testing, and publishing technical articles to ricc.rocks and Medium.
*   **`carlessian-gog`**: Google Workspace CLI managed the Carlesso way—featuring isolated configurations, selective read-only security, and daily workflows (Gmail, Calendar, Drive).
*   **`carlessian-obsidian`**: (💛) Expert guide for interacting with Riccardo's Obsidian vault (The Carlessian Vault).
*   **`create-cli-best-practices`**: Rules to create and maintain a GOOD CLI. Do not use for GUI-only design rules, web apps, or backend REST APIs.
*   **`demo-agentic-video`**: Record browser-based video demos from YAML storyboards using shot-scraper.
*   **`devrel-cfp-generator`**: Craft high-quality Call for Papers (CFP) applications for tech conferences.
*   **`drawio`**: Generate and edit diagrams using draw.io via local files or the MCP service.
*   **`drensin-reasoning`**: (💛) Implementation of the Elephant-Goldfish Model (EGM) by Ben Drensin. Used for deep reasoning, intent design, and intent validation before coding.
*   **`gemini-finops`**: Monitor and analyze GenAI expenditure on Google Cloud (Vertex AI/Gemini).
*   **`git-coding`**: (💛) Core guidelines for interacting with git repositories, updating CHANGELOGs, and safely bumping versions.
*   **`git-repo-documenter`**: (💛) Auto-documents any Git repository: creates ABOUT.md, generates project hero images via nanobanana, and builds deep diagrams.
*   **`google-stt`**: Transcribe audio files using Google Gemini 1.5 Flash.
*   **`imagen-milan-demo`**: (💛) A skill for generating images with a Milanese twist (🍌🇮🇹). It adds a "Panettone" cameo to your image prompts.
*   **`imagen-zurich-demo`**: (💛) A skill for generating images with a Zurich twist (🍌🇨🇭). It adds a "Swiss Flag" cameo to your image prompts.
*   **`learn-german-hummerli`**: (🦞) Your personal Swiss Citizenship (Zürich) tutor. Speaks easy B1 German and helps you prep for the exam.
*   **`lyria2-music-generation`**: Generate music using Google's Lyria (v2) model via Vertex AI.
*   **`nano-banana-ricc`**: (💛) Generate or edit images via Gemini 3 Pro Image (🍌 Nano Banana Pro) with Riccardo character consistency.
*   **`openclaudio-host-monitoring`**: Installs a lightweight CPU and RAM monitoring cron job and visualization script for agents on the local machine.
*   **`openclaudio-update-advisor`**: Analisi acida e basata sui fatti della stabilità delle release di OpenClaudio.
*   **`python-coding`**: (💛) Opinionated Python coding practices and standards.
*   **`riccardo-at-the-computer`**: Determine if Riccardo is active on his desktop.
*   **`ruby-coding`**: (💛) Opinionated Ruby coding practices and standards.
*   **`take-screenshot`**: Cross-platform screenshot utility for Linux Wayland and macOS.
*   **`tmux-renamer`**: Audits and renames tmux sessions based on their active content.
*   **`typescript-coding`**: (💛) Opinionated TypeScript practices (for Ruby lovers).
*   **`veo`**: Generate short videos from text or image prompts.
*   **`voice-message`**: Formats the transcript of a voice message with a standardized, fixed-width layout.
*   **`zurich-badi-info`**: (💛) Real-time water temperatures, open status of Zurich badis (lakes, river/Letten, pools), outside weather recommendations for family trips, and Limmat canotto/dinghy flow safety alerts.

### Cross-Links:
*   [General-Purpose Gemini CLI Custom Commands](https://github.com/palladius/gemini-cli-custom-commands)
*   [Riccardo's Private Gemini CLI Goodies](https://github.com/palladius/gemini-cli-palladius-private-goodies) (private, not for general consumption)
