---
name: imagen-zurich-demo
description: (💛) A skill for generating images with a Zurich twist (🍌🇨🇭). It adds a "Swiss Flag" cameo to your image prompts.
keywords: [Zurich, Switzerland, Swiss, Flag, Alps]
version: 0.1
---

# Nanobanana Zurich Demo Skill

This skill is designed for demos in Zurich. It adds a special "Swiss" touch by injecting a Swiss flag cameo into every prompt.

## Usage

Activate this skill whenever the user mentions **Zurich**, **Switzerland**, **Zurigo** or asks for an image while in a Swiss context.

## Instructions for the Agent

When this skill is active:

1. **Modify the Prompt**: Take the user's request and append a directive to include a small Swiss flag as a cameo.
   - _Example Instruction to append_: "Include a small Swiss flag in the top right corner as a subtle cameo. It should be noticeable but not obstruct the main subject."
   - _Optional_: You can also add a small "Grüezi" text if it fits the aesthetic.

2. **Delegate Image Generation**: After modifying the prompt, use the `nano-banana-pro` skill to do the actual image heavy lifting.
   - Pass the modified prompt to `nano-banana-pro`.

## Sample Invocations

- "I'm in Zurich, make me a picture of a number of developers working on AI with their laptops but at the time of dinosaurs."
  - _Agent Action_: Modifies prompt to "A number of developers working on AI with their laptops during the dinosaur era. Include a small Swiss flag in the top right corner as a subtle cameo." and then executes the `nano-banana-pro` skill with this prompt.
