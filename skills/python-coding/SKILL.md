---
name: Python Coding Best Practices
description: (💛) Opinionated Python coding practices and standards.
tags: python, development, best-practices
version: 0.2
# 9mar26 0.2 added dotenv and references the main fil which was NOT used in previous iteration...
# 6mar26 0.1 initial stesure
---

## Python Best Practices

- **UV for dependency management:** Always prefer `uv` for script management and dependencies.
- **PEP 723:** Use PEP 723 inline script metadata for standalone scripts.
- **Type Hinting:** Use standard Python type hints for all public functions.
- **Documentation:** Use Google-style docstrings.

## Riccardo opinionated ideas

Code needs to be readable an maintainable. Therefore:

- Be minimalistic.
- Break down code in multiple files which serve different purposes.
- I like the base folder to just contain main/cli and usually everything else to go under lib/ or similar. Don't shy out of folders, like lib/genai/... and lib/music/... and so on.
- I like a big multiline """file descritpion """ at the beginning of every file, after the imports. This will help me
- i like a single big constants.py containing all the constants as i dont want to go dig them in 20 different files. Do not hardcode a Gemini model version -> put it into constants. If we need one gemii model versions, one for images, one for summarization, create a SUMMARIZATION_GEMINI_MODEL and IMAGES_GEMINI_MODEL.
- Use standard naming, understood by Terraform/Pulumi, rather than random ones, like 'GOOGLE_CLOUD_PROJECT' is better than 'MY_PROJECT' or 'PROJECT_ID'.
- Riccardo likes it colorful and emoji-ful. I like `glow` outputs, and nice tables. I'm a CLI guy, but I still love beauty in a CLI.
- Beauty by default, but convenience also (maybe an output supports a nice good looking text but can also be served as --json to be parsed by jq or passed to an LLM).
- for CLI apps, use `dotenv` by default, as in the sample `main.py`: its easy to pick up gemini api keys and stuff! So its a life saver!
