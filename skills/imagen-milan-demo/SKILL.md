---
name: imagen-milan-demo
description: (💛) A skill for generating images with a Milanese twist (🍌🇮🇹). It adds a "Panettone" cameo to your image prompts.
keywords: [Milan, Milano, Milanese, Panettone, Duomo]
version: 0.2
# v0.2 10mar26 Removed the nano banana python logic (delegated to another script).
---

# Nanobanana Milan Demo Skill

This skill is designed for demos in Milan. It adds a special "Milanese" touch by injecting a Panettone cameo into every prompt.

## Usage

Activate this skill whenever the user mentions **Milan**, **Milano**, or asks for an image while in a Milanese context.

## Instructions for the Agent

When this skill is active:

1. **Modify the Prompt**: Take the user's request and append a directive to include a small Panettone as a cameo.
   - _Example Instruction to append_: "Include a small, delicious Panettone in the top right corner as a subtle cameo. It should be noticeable but not obstruct the main subject."
   - _Optional_: You can also add a small "ciao Milano" text if it fits the aesthetic.

2. **Delegate Image Generation**: After modifying the prompt, use the `nano-banana-pro` skill to do the actual image heavy lifting.
   - Pass the modified prompt to `nano-banana-pro`.

## Sample Invocations

- "I'm in Milan, make me a picture of a number of developers working on AI with their laptops but at the time of dinosaurs."
  - _Agent Action_: Modifies prompt to "A number of developers working on AI with their laptops during the dinosaur era. Include a small Panettone in the top right corner as a subtle cameo." and then executes the `nano-banana-pro` skill with this prompt.
