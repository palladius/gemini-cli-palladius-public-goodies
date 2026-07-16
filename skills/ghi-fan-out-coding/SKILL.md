---
name: ghi-fan-out-coding
description: Resolves open GitHub Issues in parallel by fanning out independent subagents and then fanning in to aggregate lessons learned.
metadata:
  author: Riccardo
  version: 1.7.0
---

# GHI Fan-Out Coding

This is a polymorphic skill. It acts as the orchestrator when invoked by the **Main Agent**, and acts as the worker when invoked by a **Subagent**.

## Role Determination

**Are you the Main Agent or a Subagent?**

1. If the user asked you to "resolve all GHIs in parallel", "start a resolution bonanza", or explicitly called you the Main Agent:
   👉 **You are the MAIN AGENT.**
   **Action**: Proceed immediately to read the detailed instructions in `references/MAIN_AGENT_CHECKLIST.md` using the `view_file` tool. **DO NOT** execute the subagent instructions.

2. If you were spawned by another agent with a prompt like "You are agent for GHI <#>" and given an execution UUID:
   👉 **You are a SUBAGENT.**
   **Action**: Proceed immediately to read the detailed instructions in `references/SUB_AGENT_CHECKLIST.md` using the `view_file` tool. **DO NOT** execute the main agent instructions.
