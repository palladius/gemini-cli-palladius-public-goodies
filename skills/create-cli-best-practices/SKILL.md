---
description: Rules to create and maintain a GOOD CLI
name: create-cli-best-practices
---

TODO(make this well)

A good CLI should be implemented in `rust` or `go`.
A carlessian CLI should also be doucmented in $GIC/ under installables.

# Convention on CLI

* Prefer smaller files to a single big monolithic file. It'll be harder to manage in rebases :) 
* honour NO_COLOR env var!
* Make sure it works well in `watch` scenarios.


All commands should have:

* --help/-h: shows this help
* --version/-v: show version. Should also be able to check if version is latest at beginning, if this can be ascertained FAST (eg default local version file in local FS! or curl from public GH).
* --dry-run/-n: Allow to see what WOULD happen witheout the mutatio actually happening - whenever possible!

# Riccardo specific tules

1. I love colors, make it colorful! If an important thing has to be done often, use WHITE or YELLOW. A fancy small thing, use CYAN.
2. Use linux standards, so green for exec files, blue for folders , ...
3. Use emojis to signify a complex thing in a single charactet, eg FOLDER emoji, COLOR bullet points for good/bad or high/low priority, and so on.
4. Remember some emojis dont render well, eg nation flags are horrble on most ocmputers, but some are "SAFE". Also remember that some emoji consume 1-2-3 chars in visualization so they can "SPAIARE" the column/tab rendering
5. Ensure tab rendering is IMMAULCATE in lisying

# AI-friendly

Make the CLI AI friendly, ultimately an AI is going to use it more than a human.


* `--format json/yaml/csv`, whatever it makes sense. Humans find YAML more readable, AIs find JSON more digestable, allow them all. Of course allow to disable color via ENV[NO_COLOR] or simply --no-color
* Support pagination. AI will love it for it, eg allow to "show me page 2 with pagesize 50".

# LLM Support

We should NOT use/bake LLM functionality randomly. I don't want my CLI to hand indefinitely for a Gemini call going rogue. This needs to respect the POLA principle of least astonishment. Every invokation of LLM should be signified by one of these convention:

* `--llm-classify` Explicityly stating LLM
* `--long-running-summarization` Explicitly stating long-running.

Useer should KNOW they need to expect long running time.