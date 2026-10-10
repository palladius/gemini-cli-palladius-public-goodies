---
name: install-jev-for-antigravity
description: (💛) Guide and automation procedures to install and configure TypeSafe Jev (System One classification & decision engine) for Google Antigravity CLI and IDE, including both the skill plugin and the MCP proxy server.
compatibility: Gemini CLI, Antigravity, Claude Code
metadata:
  version: 0.1.0
---

# Install Jev for Google Antigravity ⚡️🧠

A comprehensive guide and checklist for installing, configuring, and verifying **TypeSafe Jev** within **Google Antigravity** (both CLI and IDE/Desktop) and **Gemini CLI**.

---

## 🎯 What is TypeSafe Jev?

**Jev** is a **System One decision model** from TypeSafe AI. Unlike text-generation LLMs (System Two reasoning/coding), Jev evaluates state against atomic, typed questions and returns:
- Calibrated probabilities ($0.0 \le P \le 1.0$)
- Categorical choices with confidence scores
- Rubric-based scores

It is designed for rapid (100–200 ms), high-accuracy classification, triage, routing, guardrail verification, and gating without generating conversational text.

---

## 🧩 The Two Layers in Antigravity

To leverage Jev in Antigravity, two distinct components are used:

| Layer | Repository / Source | Purpose |
|---|---|---|
| **1. Skill / Design Patterns** | [`aaddrick/building-with-typesafe-jev`](https://github.com/aaddrick/building-with-typesafe-jev) | Teaches the agent prompt shapes, primitives (`Choice`, `Score`, `Noul`), anti-patterns, and prior art. |
| **2. MCP Tool Proxy** | [`altregubov/jev-antigravity-mcp`](https://github.com/altregubov/jev-antigravity-mcp) | Exposes executable runtime tools (`jev_evaluate`, `jev_choice`, `jev_noul`, `jev_score`) so the agent can execute live Jev calls. |

---

## 🛠️ Installation Instructions

### Step 1: Install the Skill Plugin (Antigravity CLI)

In your terminal:
```bash
agy plugin install https://github.com/aaddrick/building-with-typesafe-jev
```

Verify installation:
```bash
agy plugin list
agy plugin validate ~/.gemini/config/plugins/building-with-typesafe-jev
```

Ensure the plugin is enabled:
```bash
agy plugin enable building-with-typesafe-jev
```

---

### Step 2: Configure the MCP Server (`jev-proxy`)

#### Option A: Antigravity CLI (Zero-Install with `uvx`)
Run the following command in terminal:
```bash
agy mcp add --env TYPESAFE_API_KEY="$TYPESAFE_API_KEY" jev-proxy uvx --from git+https://github.com/altregubov/jev-antigravity-mcp jev-mcp
```

Verify the configured MCP servers:
```bash
agy mcp list
```

#### Option B: Antigravity Desktop / IDE Configuration
Add the server entry to `~/.gemini/antigravity/mcp_config.json`:
```json
{
  "mcpServers": {
    "jev-proxy": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/altregubov/jev-antigravity-mcp",
        "jev-mcp"
      ],
      "env": {
        "TYPESAFE_API_KEY": "YOUR_TYPESAFE_API_KEY"
      }
    }
  }
}
```

---

## 🔑 API Key Management

1. Obtain your API key from [TypeSafe AI Console](https://console.typesafe.ai/keys).
2. Export the key in your shell configuration (`~/.bashrc`, `~/.zshrc`, or local environment):
   ```bash
   export TYPESAFE_API_KEY="apikey_your_key_here"
   ```
3. Never hardcode API keys in repositories or chat sessions.

---

## 🔍 Verification & Smoke Test

### Test 1: Verify MCP Tools Availability
Inside an Antigravity session with MCP enabled, check that the following tools are available:
- `jev_evaluate`: Batch router for evaluating state against multiple questions.
- `jev_choice`: Categorical rubric selection with confidence.
- `jev_noul`: Binary yes/no calibrated probability.
- `jev_score`: Multi-level rubric scoring.

### Test 2: Quick Command-Line Probe (Python)
```bash
python3 -c "
import os
import httpx

api_key = os.environ.get('TYPESAFE_API_KEY')
if not api_key:
    print('TYPESAFE_API_KEY is not set')
    exit(1)

res = httpx.post(
    'https://api.typesafe.ai/v1/systemone',
    headers={'Authorization': f'Bearer {api_key}'},
    json={
        'state': 'Antigravity test payload',
        'questions': {
            'is_test': {'type': 'noul', 'instructions': 'Is this a test message?'}
        }
    }
)
print('Status:', res.status_code)
print('Response:', res.json())
"
```

---

## 📚 References & Resources

- [TypeSafe AI Documentation](https://docs.typesafe.ai)
- [Jev AI Tools Catalog](https://jevaitools.com/tools/jev-antigravity-mcp)
- [Building with TypeSafe Jev (Plugin)](https://github.com/aaddrick/building-with-typesafe-jev)
- [Jev Antigravity MCP Server](https://github.com/altregubov/jev-antigravity-mcp)
