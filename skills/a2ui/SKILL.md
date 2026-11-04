---
name: a2ui
description: >-
  (💛) Build and render portable, declarative Generative UIs with Google A2UI (Agent-to-User Interface). Use whenever the user asks to generate, design, or wire interactive UI widgets, cards, forms, or dashboards using A2UI.
compatibility: Gemini CLI
metadata:
  version: "1.0"
---

# A2UI (Agent-to-User Interface) Skill

Use **A2UI** ([a2ui.org](https://a2ui.org/) | [github.com/google/A2UI](https://github.com/google/A2UI)) to let AI agents generate rich, interactive user interfaces declaratively using a component catalog (`Card`, `Row`, `Column`, `Text`, `TextField`, `Button`, `ChoicePicker`, `Slider`, `Tabs`, `Modal`, `List`, `Image`), without emitting unsafe raw HTML/JS from the LLM.

## 1. Generating UI with A2UI Express DSL (`<a2ui>`)

When an agent needs to output a UI, wrap the component tree in `<a2ui>...</a2ui>` and assign the root widget to `root`:

```
<a2ui>
surface("main")
$/form/name = "Mario Rossi"
$/form/role = "Developer"

header = Text("Registrazione Utente", "h2")
nameField = TextField("Nome completo", $/form/name, "Inserisci il nome", "shortText", ?required("Il nome è obbligatorio"))
rolePicker = ChoicePicker("Ruolo", ["Developer", "SRE", "Designer"], $/form/role, "mutuallyExclusive")
submitBtn = Button("Salva", action=Event("save_profile", {name: $/form/name, role: $/form/role}), variant="primary")

root = Card(Column([header, nameField, rolePicker, submitBtn]))
</a2ui>
```

### Core Building Blocks (`basic` Catalog)
- **Layout**: `Card(child)`, `Column(children, justify?, align?)`, `Row(children, justify?, align?)`, `Tabs(tabs=[{title, child}])`, `Modal(trigger, content)`, `Divider()`, `List(children, direction?)`
- **Display**: `Text(text, variant="h1"|"h2"|"h3"|"body"|"caption")`, `Image(url, altText?, variant?)`, `Icon(name)`, `Video(url)`, `AudioPlayer(url)`
- **Inputs & Actions**:
  - `Button(label, action=Event("name", {...}), variant="primary"|"secondary"|"borderless")`
  - `TextField(label, value=$/path, placeholder?, variant="shortText"|"longText"|"number"|"obscured", checks?)`
  - `CheckBox(label, value=$/boolPath)`
  - `ChoicePicker(label, options, value=$/path, variant="mutuallyExclusive"|"multipleSelection")`
  - `Slider(label, min, max, value=$/numPath)`
  - `DateTimeInput(value=$/isoDatePath, enableDate=true, enableTime=true)`
- **Reactive State & Validation**:
  - Bindings: `$/path/to/data` (reactive JSON pointer in `dataModel`).
  - String interpolation: `formatString("Ciao ${/form/name}")`.
  - Checks: `?required("Messaggio")`, `?email()`, `?numeric(min=0, max=100)`, `?regex("^[0-9]+$", "Solo numeri")`.

*(For the complete list of component & function signatures, read `$SKILL_DIR/references/express_basic_catalog.md`.)*

## 2. Rendering Live A2UI Previews in Antigravity Chat

When the user asks to **see or interact with an A2UI UI right here in Antigravity**:
1. Write the `<a2ui>` spec (or JSON surface) so the declarative structure is clear.
2. Render it as a live interactive widget using a self-contained HTML artifact in `<appDataDir>/brain/<conversation-id>/` with Tailwind (`<script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>`) that maps each A2UI component (`Card`, `Column`, `Row`, `TextField`, `ChoicePicker`, `Slider`, `Button`) to reactive DOM controls, and embed it inline:
   ```html
   <agent-embed src="file:///<artifact_path>/a2ui_surface.html"></agent-embed>
   ```

## 3. Adding A2UI to an App or Agent

### Python Agent (`a2ui-agent-sdk`)
```bash
pip install a2ui-agent-sdk
```
```python
from a2ui.processor.catalog_config import CatalogConfig
from a2ui.processor.generator import A2uiGenerator

generator = A2uiGenerator(catalogs=[CatalogConfig.from_path(name="basic", catalog_path="file:///path/to/catalog.json")])
processor = generator.create_processor()

# 1. Inject A2UI instructions into your agent's system prompt
system_prompt = processor.prompt_generator.generate(
    role_description="Sei un assistente che risponde generando interfacce A2UI.",
    include_schema=True,
)

# 2. Parse the LLM output into A2UI UI parts for the frontend renderer
parts = processor.parser.parse_response(llm_output)
```

### Web / Frontend Quickstart (React / Lit / Angular / CopilotKit)
```bash
npx copilotkit@latest create my-app --framework a2ui
```
