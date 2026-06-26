## [0.5.5] - 2026-06-26

- 📖 Docs: Highly suggested Bubble Tea for Go CLIs in the `create-cli-best-practices` skill and bumped version to 0.5.5.

## [0.5.4] - 2026-06-26

- 📖 Docs: Added Golang CLI recommendations from Daniela (Cobra, Viper, Bubble Tea) to the `create-cli-best-practices` skill.

## [0.5.3] - 2026-06-25

- 📖 Docs: Added `--ai-help` best practice to `create-cli-best-practices` skill and updated TODO.md.

## [0.5.2] - 2026-06-25

- 📖 Docs: Added Alies Lapatsin reference link to `create-cli-best-practices` skill and updated the version to 0.5.2.

## [0.5.1] - 2026-06-25

- 📖 Docs: Updated `create-cli-best-practices` skill with AI-friendly CLI design guidelines (idempotence, dry-run, bare quiet output, actionable errors, non-interactive TTY detection) and added reference links.

## [0.5.0] - 2026-06-25

- ✨ Feat: Added `gemini-finops` skill to monitor and analyze GenAI expenditure on Google Cloud (Vertex AI/Gemini).
- 🐛 Bugfix: Renamed `skills/gcp-finops` to `skills/gemini-finops` to resolve folder/specification mismatch validation errors.
- 🧪 Unit Tests: Refactored `skills/nano-banana-ricc/scripts/generate_image.py` to extract `auto_detect_resolution` and `choose_output_resolution` to pass the 8 pytest unit tests.

## [0.4.16] - 2026-06-17

- 🤖 Maintenance run by gc-skillume-bot-v0_2.
- 🧹 Routine checks and minor updates.

## [0.4.15] - 2026-06-16

- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.
- 🧹 Routine checks and minor updates.

## [0.4.14] - 2026-06-13

- 🤖 Routine audit: verified 25 skills, all tests passed.
- 🚀 Bumped version to 0.4.14.

## [0.4.13] - 2026-06-01

- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.
- 📝 Corrected README.md to actually include missing skills: `carlessian-gog` and `git-repo-documenter` (fixing incomplete 0.4.12 sync).

## [0.4.12] - 2026-05-31

- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.
- 📝 Updated README.md to include missing skills: `carlessian-gog`, `git-repo-documenter`, and `zurich-badi-info`.

## [0.4.11] - 2026-05-30

- 🏖️ Added `zurich-badi-info` skill providing real-time water temperatures, open/closed status for Zurich outdoor pools, lakes, and Limmat/Letten river. Includes custom family weather recommendations (>25°C), morning Ironman swim highlights, and safety advice for Limmat canotto floating.
- 💡 Integrated Lake Zurich West vs. East side microclimate observations into the skill logic.
- 📝 Translated the entire CLI script output and documentation into Italian, and added a baseline comparison system for Pegel water height with SECCA alerts.
- 📓 Automatically detects and saves daily reports directly into the active Obsidian vault.

## [0.4.10] - 2026-05-29

- 🛑 Added a critical agent guardrail warning in caps lock to protect user safety and restrict hazardous automated operations.

## [0.4.9] - 2026-05-29

- ✨ Added `carlessian-gog` skill containing Carlesso-opinionated safety setup and daily workflows (Gmail, Calendar, Drive).
- 🔗 Symlinked the `carlessian-gog` skill into GIC workspace.

## [0.4.8] - 2026-05-27


- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.
- 🧹 Routine checks and minor updates.

## [0.4.7] - 2026-05-26

- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.
- 🧹 Routine checks and minor updates.

## [0.4.6] - 2026-05-25

- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.
- 🛠️ Routine checks and minor updates.

## [0.4.5] - 2026-05-24

- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.
- 🛠️ Routine checks and minor updates.

## [0.4.4] - 2026-05-22

- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.
- 🛠️ Routine checks and minor updates.

## [0.4.3] - 2026-05-21

- 📝 Updated README.md to include the `tmux-renamer` skill.
- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.

## [0.4.2] - 2026-05-18

- 🎙️ Updated `google-stt` to use `gemini-3.1-flash-lite` model for faster/cheaper transcription.
- ✨ Feat: Added multi-account support for `openclaw message send` in `learn-german-hummerli` skill.
- 🚚 Added specific instruction to `nano-banana-ricc` for Hermes (Ermete Bottazzi).
- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.

## [0.4.1] - 2026-05-16

- ✨ Feat: Added multi-account support for `openclaw message send` in `learn-german-hummerli` skill.

## [0.4.0] - 2026-05-11

- ✨ Feat: Added `tmux-renamer` skill to audit and rename tmux sessions.

## [0.3.10] - 2026-05-08
- 🖼️ Added new pixar demo images to `nano-banana-ricc` skill.
- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.

## [0.3.9] - 2026-05-07
- 🤖 Maintenance run by `gc-skillume-bot-v0_2`: Fixed typos in `GEMINI.md`.

## [0.3.8] - 2026-05-04

- 📝 Updated README.md with missing `lyria2-music-generation` skill.
- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.

## [0.3.7] - 2026-05-03

- ✨ Feat: Added `lyria2-music-generation` skill to generate music using Google's Lyria model.

## [0.3.6] - 2026-05-03

- 🔒 Security: Removed hardcoded OpenAI API key from `octts` script.
- 🐛 Bugfix: Added environment variable check for `OPENAI_API_KEY` in `octts`.

## [0.3.5] - 2026-05-01
3 updated hummerli

## [0.3.4] - 2026-05-01

- ✨ Added `take-screenshot` skill to the main CHANGELOG.
- 🐛 Fixed invalid YAML frontmatter in `devrel-cfp-generator/SKILL.md`.
- 📝 Updated README.md with the full list of available skills.
- 🤖 Maintenance run by `gc-skillume-bot-v0_2`.

## [0.3.3] - 2026-04-30

- ✨ Added `devrel-cfp-generator` skill (v0.0.1) to create highly structured and validated conference proposals.

## [0.3.2] - 2026-04-30

- 🤖 Maintenance run and version bump -- gc-skillume-bot-v0_2.

## [0.3.1] - 2026-04-29

- 🧠 Implemented reasoning loop with Interrogator, Elephant, and Goldfish phases.
- 🤖 Auto-populated by Lobby 🦞.

## [0.2.2] - 2026-04-27
