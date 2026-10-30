---
name: a2ui
description: >-
  (💛) Build and render portable, framework-agnostic Generative UI with Google A2UI v0.9 (Agent-to-User Interface). Use when creating AI agents that emit declarative UI widgets (<a2ui> Express DSL or Direct JSON), integrating the Python a2ui-agent-sdk / a2ui-adk, defining custom component catalogs, or rendering A2UI surfaces across Web (React, Lit, Angular, Web-Core) and Flutter.
compatibility: Gemini CLI
metadata:
  version: "0.9.0"
---

# A2UI v0.9 (Agent-to-User Interface) Skill

**A2UI** ([a2ui.org](https://a2ui.org/) | [github.com/google/A2UI](https://github.com/google/A2UI)) is Google's open-source protocol and SDK family for **portable, framework-agnostic Generative UI**. Instead of generating untrusted executable HTML/JS, agents stream declarative UI intent against a pre-approved **Component Catalog** (`basic` or custom design systems).

## Quick Start: Python Agent SDK (`a2ui-agent-sdk` v0.9)

Install the official SDK ( plus optional ADK / A2A extensions):

```bash
pip install a2ui-agent-sdk
# Optional framework extensions:
# pip install a2ui-adk a2ui-a2a
```

### 5-Step Agent Integration Pattern

```python
from a2ui.core.schema import ProtocolVersion
from a2ui.processor.catalog_config import CatalogConfig
from a2ui.processor.generator import A2uiGenerator

# Step 1: Define your catalog ('basic' or custom JSON schema) + optional few-shot examples
my_catalog = CatalogConfig.from_path(
    name="basic",
    catalog_path="file:///path/to/catalog.json",
    examples_path="path/to/examples/*.json",  # optional
)

# Step 2: Initialize the A2UI Generator / Request Processor for v0.9
generator = A2uiGenerator(
    version=ProtocolVersion.V0_9,
    catalogs=[my_catalog],
)
processor = generator.create_processor()

# Step 3: Generate the System Prompt (injects A2UI grammar + catalog signatures)
system_instruction = processor.prompt_generator.generate(
    role_description="You are a helpful assistant that generates interactive UI surfaces.",
    include_schema=True,
    include_examples=True,
)

# Step 4: Pass system_instruction to your ADK / Gemini / AG2 agent
# my_agent = LlmAgent(name="ui_agent", model="gemini-2.5-flash", instruction=system_instruction)

# Step 5: Parse or stream LLM response into validated A2UI message parts
def handle_turn(llm_response_text: str):
    parts = processor.parser.parse_response(llm_response_text)
    return {"is_task_complete": True, "parts": parts}
```

### Exporting Portable `SKILL.md` Files from Any Catalog (`SkillGenerator`)

A2UI v0.9 includes a built-in `SkillGenerator` that compiles any `InferenceFormat` (`Express` or `DirectJson`) and bound `Catalog` into standalone `SKILL.md` files:

```python
from a2ui.skill_generator import SkillGenerator

skill_gen = SkillGenerator(processor.format)
# Unified monolithic skill (a2ui/SKILL.md):
mono_skill = skill_gen.generate_skill(name="a2ui")
# Or modular skillset (a2ui-core/SKILL.md + a2ui-<catalog>/SKILL.md):
skillset = skill_gen.generate_skillset()
skillset.export_to_directory(".agents/skills")
```

## Core A2UI v0.9 Protocol Concepts

1. **Surface Lifecycle Actions** (`version: "0.9"`):
   - `createSurface`: Initializes a named UI surface (`surfaceId`, `catalogId`).
   - `updateComponents`: Streams or updates components in the surface's flat adjacency list (`id`, `type`, `props`).
   - `updateDataModel`: Populates or mutates reactive state bound via JSON Pointers (`$/path/to/key`).
   - `deleteSurface`: Tears down a surface by `surfaceId`.
2. **Two Inference Formats**:
   - **Direct JSON (`<a2ui-json>...</a2ui-json>`)**: Incremental, self-healing JSON streaming (`processor.parser.open_stream()`) for low-latency live UI rendering.
   - **A2UI Express DSL (`<a2ui>...</a2ui>`)**: Concise positional/keyword constructor syntax (`root = Card(Column([Text("Hello"), Button("Save", action=Event("save"))]))`) compiled by the host into A2UI JSON envelopes.
3. **Client-Defined Functions & Validation (`?rule`)**:
   - Built-in functions: `formatString`, `formatNumber`, `formatCurrency`, `formatDate`, `pluralize`, `openUrl`, `and`, `or`, `not`.
   - Validation rules prefixed with `?` in Express DSL: `?required("Field is required")`, `?email()`, `?numeric(min=0, max=100)`, `?regex("^[0-9]{5}$", "Must be 5 digits")`.

## Rendering A2UI Surfaces in Antigravity Chat (`generative_ui`)

When asked to preview or render an A2UI surface directly inside Antigravity:
1. Emit the declarative A2UI v0.9 payload (`createSurface` / `updateComponents` / `updateDataModel` or `<a2ui>` Express block).
2. If the user wants a live interactive preview inline in chat, compile the A2UI component tree (`Card`, `Row`, `Column`, `Text`, `TextField`, `Button`, `ChoicePicker`, `Slider`, `Tabs`, `Modal`) into a self-contained HTML artifact in `<appDataDir>/brain/<conversation-id>/` using the Antigravity Tailwind script (`https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js`) and embed it via `<agent-embed src="file:///..."></agent-embed>`.

## Full Express DSL & `basic` Catalog Reference

Read `$SKILL_DIR/references/express_basic_catalog.md` whenever you need the exact positional/keyword component signatures (`AudioPlayer`, `Button`, `Card`, `CheckBox`, `ChoicePicker`, `Column`, `DateTimeInput`, `Divider`, `Icon`, `Image`, `List`, `Modal`, `Row`, `Slider`, `Tabs`, `Text`, `TextField`, `Video`), function signatures, or grammar rules for A2UI v0.9.

## Key Links

- **Announcement Blog**: [A2UI v0.9: The New Standard for Portable, Framework-Agnostic Generative UI](https://developers.googleblog.com/a2ui-v0-9-generative-ui/)
- **Documentation & Spec**: [a2ui.org](https://a2ui.org/)
- **GitHub Repository**: [github.com/google/A2UI](https://github.com/google/A2UI)
- **CopilotKit / AG-UI Starter**: `npx copilotkit@latest create my-app --framework a2ui`
