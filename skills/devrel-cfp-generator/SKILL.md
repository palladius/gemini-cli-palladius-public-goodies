---
name: devrel-cfp-generator
description: A specialized workflow for crafting high-quality Call for Papers (CFP) applications. Use when the user wants to apply to a tech conference and needs to draft abstracts, outlines, and bios based on their existing work.
metadata:
  version: 0.0.3
compatibility: Gemini CLI
---

# 🎤 DevRel CFP Generator Skill

This skill guides you through a multi-phase process to create winning CFP applications. It leverages existing project documentation, past talk history, and conference-specific themes to craft tailored proposals.

## 🛠️ Reusable Resources
Before starting, familiarize yourself with these resources:
*   **Checklist:** Use `references/cfp_checklist.md` as your step-by-step guide. Follow the 4 phases strictly.
*   **Template:** Use `assets/proposal_template.md` as the deterministic format for your drafts.
*   **Bio Templates:** Use `assets/riccardo_bio_templates.md` for standard Riccardo bios.
*   **Validation Script:** Use `scripts/validate_proposal.py` to check character limits and section compliance.

## Workflow

When triggered, immediately copy `references/cfp_checklist.md` into the local project workspace (e.g., as `CFP_CHECKLIST.md`) so you can interactively check off items as they are completed. Then begin executing **Phase 1: Gathering Constraints**.

Do not proceed to Phase 2 until all constraints and Meta info (Demo, Duration) are gathered. Use the validation script in Phase 3 before presenting the final result.
