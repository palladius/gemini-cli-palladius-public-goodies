---
name: OpenClaw instance (Lobby) on pupurabbux (Only if hostname==pupurabbux)
description: (💛) 🔴 My Openclaw instance on Pupurabbux linux machine.
tags: openclaw, lobby, images, pixar
version: 0.2
---

If `hostname`=='pupurabbux', continue. Otherwise FORGET and LEAVE!

- Openclaw instance is called Lobby
- User speaks Italian to Lobby, via telegram

## Images

- Whenever user sends a picture, Lobby sends it back "pixarized".
- User ORIGINAL input images are under `/home/riccardo/.openclaw/media/inbound` (if lost they can also be found in Google Photos).
- Lobby Pixarized versions should be in `/home/riccardo/.openclaw/workspace/nano_banana`

You can cross-correlate the two in two ways:

1. (best effort) mappings should be in `banana_mapping.csv`. However Lobby often forgets to update it.
2. (deterministic) mapping can be seen with a `find` with `ctime` or `mtime` on both sides. Usually a few seconds pass between one and the other. Rarely more than 2 minutes.

## Example (from 2026-03-07)

**Pixarized Results (in `nano_banana`):**
- `2026-03-07-06-38-ale-mom-ski-pixar.png` (from `file_1173...jpg`)
- `2026-03-07-06-40-boy-with-skis-pixar.png` (from `file_1170...jpg`)
- `2026-03-07-06-40-two-brothers-ski-pixar.png` (from `file_1175...jpg`)

## Automation

Use the provided script to find and correlate images:
`./scripts/find_yesterday_images.rb`
