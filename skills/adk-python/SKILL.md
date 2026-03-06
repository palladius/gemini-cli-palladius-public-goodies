---
name: adk-python
description: (💛) Create and manage AI agents using Google's Agent Development Kit (ADK) for Python. Use when the user wants to build single or multi-agent systems, evaluate agents, or deploy them. Includes instructions for fetching fresh ADK documentation and links for TypeScript and Go development.
---
# ADK Python Skill

This skill helps you build AI agents using the **Agent Development Kit (ADK)** for Python.

## Core Workflows

### 1. Initialize ADK Knowledge
Always start by fetching the latest ADK documentation to ensure you have the most up-to-date patterns and API references.

- **Option A (Summary)**: Fetch `llms.txt` for a high-level overview and index.
- **Option B (Deep Dive)**: Fetch `llms-full.txt` for comprehensive documentation (large file).

Use the provided script to fetch these:
```bash
python3 scripts/fetch_context.py --type summary  # for llms.txt
python3 scripts/fetch_context.py --type full     # for llms-full.txt
```

### 2. Create an Agent
Basic pattern for a single agent:
```python
from google.adk.agents import Agent
from google.adk.tools import google_search

agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    instruction="Your instructions here",
    tools=[google_search]
)
```

### 3. Multi-Agent Systems
Use `LlmAgent` and `sub_agents` to compose systems:
```python
from google.adk.agents import LlmAgent

child_agent = LlmAgent(name="child", model="gemini-2.0-flash", ...)
parent_agent = LlmAgent(
    name="coordinator",
    model="gemini-2.0-flash",
    sub_agents=[child_agent]
)
```

## Cross-Language Development
If the user prefers TypeScript or Go, point them to these resources:
- **Go ADK**: [github.com/google/adk-go](https://github.com/google/adk-go)
- **TypeScript/Web ADK**: [github.com/google/adk-web](https://github.com/google/adk-web)
- **Java ADK**: [github.com/google/adk-java](https://github.com/google/adk-java)

## Reference Material
See [adk_links.md](references/adk_links.md) for a comprehensive list of ADK documentation and repositories.
