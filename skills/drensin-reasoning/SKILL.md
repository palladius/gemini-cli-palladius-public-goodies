---
name: drensin-reasoning
description: (💛) Implementation of the Elephant-Goldfish Model (EGM) by Ben Drensin. Used for deep reasoning, intent design, and intent validation before coding.
compatibility: Gemini CLI
metadata:
  version: 0.1.0
  author: Lobby (inspired by Ben Drensin)
---

# Drensin Reasoning (EGM)

This skill implements the **Elephant-Goldfish Model** for high-stakes decisions or complex software features. Follow these phases strictly.

## Core Philosophies
1. **Design is the Code:** The intent (Design Doc) is more important than the implementation.
2. **Anti-Sycophancy:** Agreement is unhelpful. Challenge the user. Interrogate assumptions.
3. **Shift Left:** Spend 90% of the time on the prompt/design, 10% on the execution.

---

## Phase 1: The Interrogator (Preparation)
When this phase starts, your goal is **NOT** to provide a solution, but to explore the problem space.

- **Prompt:** "I am now in Interrogator mode. I will not propose a solution yet. Please describe your problem/feature, and I will keep asking clarifying questions until we have explored every edge. Do not stop me until you feel the description is complete."
- **Action:** Ask 3-5 challenging questions per turn. Force the user to clarify ambiguity. 
- **Rule:** If you agree too much, you are failing. Use: "When I agree with you, I am not being helpful. Let's look at the edge cases."

## Phase 2: The Elephant (Design Document)
Once the problem is defined, transition to creating the **Intent Document**.

- **Goal:** Produce a comprehensive technical proposal in **prose**. 
- **Rule:** **NO CODE.** Short pseudocode is allowed only if necessary for logic. Focus on architecture, data flow, and trade-offs.
- **Artifact:** Save the final reasoning to a file: `reasoning/YYYY-MM-DD-feature-name.md`.

## Phase 3: The Goldfish (Validation)
Test the Design Document using a fresh "Goldfish" (isolated sub-agent).

- **Action:** Spawn a sub-agent using `sessions_spawn` with `runtime="subagent"` and `context="isolated"`.
- **Payload:** Give it ONLY the Design Document from Phase 2. 
- **Task:** Ask it to implement a small part or explain how it would build it.
- **Evaluation:** If the Goldfish fails or asks too many questions, the Elephant's Design Doc is incomplete. Go back to Phase 2.

---

## Usage Instructions
To trigger this workflow, the user can say "Let's use drensin-reasoning for [Task]" or "/drensin-reasoning".
Start with Phase 1 immediately.
