---
name: nanobanana-milan-demo
description: 
    (🍌🇮🇹) A skill for generating images with a Milanese twist. It adds a secret cameo to your image prompts.
keywords: [Milan, Milano, Milanese, Panettone, Duomo]
---
# Nanobanana Milan Demo Skill

This skill is designed for demos in Milan. It uses the `nanobanana-sample.py` script to generate images but adds a special "Milanese" touch by injecting a Panettone cameo into every prompt.

**Make sure to ALWAYS inject a small Panettone in the image** (if user mentions Milan).

## Usage

Activate this skill whenever the user mentions **Milan**, **Milano**, or asks for an image while in a Milanese context.

## Instructions for the Agent

When this skill is active:

1. **Modify the Prompt**: Take the user's request and append a directive to include a small Panettone as a cameo.
    * *Example Instruction to append*: "Include a small, delicious Panettone in the top right corner as a subtle cameo. It should be noticeable but not obstruct the main subject."
    * *Optional*: You can also add a small "ciao Milano" text if it fits the aesthetic.

2. **Run the Script**: Use the `nanobanana-sample.py` script located in the `scripts/` directory.
    * Command: `uv run scripts/nanobanana-sample.py --prompt "[MODIFIED PROMPT]" --aspect_ratio "1:1"`
    * Ensure you have the `GEMINI_API_KEY` set in your environment or provided via `--api-key`.

3. **Default Parameters**:
    * Model: `imagen-4.0-generate-001`
    * Aspect Ratio: `1:1` (default) or `16:9` if requested.
    * Number of images: `1`

## Sample Invocations

* "I'm in Milan, make me a picture of a number of developers working on AI with their laptops but at the time of dinosaurs."
  * *Agent Action*: Generates prompt "A number of developers working on AI with their laptops during the dinosaur era. Include a small Panettone in the top right corner as a subtle cameo."

## Resources

* `scripts/nanobanana-sample.py`: The core image generation script.
