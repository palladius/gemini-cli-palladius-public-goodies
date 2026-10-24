---
name: harbor-atif-trajectory
description: >-
  (💛) Harbor & Agent Trajectory Interchange Format (ATIF-v1.8) capture, inspection, and FinOps telemetry skill. Standardizes agent trajectories across agy/Antigravity, Antigravity IDE, gemini-cli, and OpenClaw.
metadata:
  version: "1.0.0"
  standard: "Harbor RFC 0001 (ATIF-v1.8)"
  author: "RiccardinoCM26 🦖 & Jetski"
---

# Harbor ATIF Trajectory & FinOps Skill

This skill captures, validates, inspects, and analyzes agent execution trajectories using the open standard **ATIF (Agent Trajectory Interchange Format) v1.8** originating from the **Harbor Framework** (`harbor-framework/harbor`).

It bridges the gap between **Layer 1 (GCP Infrastructure & Cloud Monitoring FinOps)** and **Layer 2 (Client Harness Telemetry & Prompt Observability)** across Riccardo's agent fleet:
- **`agy` / Antigravity CLI / Jetski**
- **Antigravity IDE / CloudCode / OpenCode**
- **Gemini CLI**
- **OpenClaw (`pupurabbux`, `mini-mac-lobby`)**

---

## 🚀 Quick Start Commands

### 1. Export Active Session Trajectory
Export the current Jetski/Antigravity session into a standardized `trajectory.json`:
```bash
# Display summary in terminal
atif_export --current --summary

# Save to file
atif_export --current --output /tmp/my_session.trajectory.json
```

### 2. Export from Other Harnesses
```bash
# From a Gemini CLI session
atif_export --gemini-cli ~/.gemini/tmp/session-123.json -o trajectory.json

# From an OpenClaw conversation dump
atif_export --openclaw /path/to/openclaw/session.json -o trajectory.json
```

### 3. Check Gemini API Key FinOps & Token Spend
```bash
# Show daily token IN/OUT and USD spend for an API key or alias
gemini_finops key openclaw-pupurabbux --days 30

# Breakdown for a GCP project
gemini_finops project palladius-genai --days 30

# Global dashboard across fleet
gemini_finops summary

# View recipe for callerIp and userAgent audit logging
gemini_finops audit --project palladius-genai
```

---

## 📐 The ATIF-v1.8 Data Contract

An ATIF-v1.8 trajectory (`trajectory.json`) is a deterministic, self-contained JSON document:

- **Root Fields:**
  - `schema_version`: Must be `"ATIF-v1.8"`.
  - `session_id`: Run-scoped identifier (may be shared across subagents).
  - `trajectory_id`: Document-scoped unique identifier (e.g. `traj-<uuid>`).
  - `agent`: Agent metadata (`name`, `version`, `model_name`, `tools`).
  - `steps`: Array of sequential turn objects starting at `step_id: 1`.
  - `final_metrics`: Cumulative tokens (`prompt`, `completion`, `cached`, `reasoning`), `total_cost_usd`, and `total_steps`.
  - `subagent_trajectories`: Embedded child trajectories for hierarchical multi-agent tasks.

- **Step Fields:**
  - `step_id`: 1-based integer, strictly sequential.
  - `source`: `"user" | "agent" | "system"`.
  - `model_name`: Specific model used for the step.
  - `message`: Text string or array of `ContentPart` (for multimodal text, image, audio, video).
  - `reasoning_content`: Agent's internal thinking process or chain of thought.
  - `tool_calls`: Array of structured tool calls (`tool_call_id`, `function_name`, `arguments`).
  - `observation`: Feedback containing `results` paired via `source_call_id`.
  - `metrics`: `prompt_tokens`, `completion_tokens`, `cached_tokens`, `cost_usd`.
  - `llm_call_count`: Inferences in step (0 = deterministic tool dispatch, 1 = standard inference).

---

## 🛠️ Automated Scripts & Tooling

Located in `$GIC/bin/`:
- **`bin/atif_export`**: Universal CLI to extract and serialize sessions into ATIF-v1.8.
- **`bin/gemini_finops`**: Cloud Monitoring correlator attributing token usage and costs to specific API keys.

---

## 🛡️ Security & Privacy Guidelines

1. **Prompt Redaction:** By default, ATIF trajectories contain raw prompt and message text. When sharing trajectories externally or attaching them to public benchmarks, ensure secrets and private paths are redacted.
2. **`.env` Protection:** Under no circumstances should `.env` files be included in trajectories or written to disk.
3. **Audit Logging:** Google Cloud Audit Logging intentionally strips prompts for privacy. Prompts are captured exclusively through client-side ATIF recorders.
