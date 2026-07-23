# GHI Fan-Out Coding Skill 🚀

Welcome to the **GHI Fan-Out Coding** skill! This skill gives your AI agent the superpower to work on multiple GitHub Issues (GHIs) at the very same time.

Think of it like hiring a team of junior developers. You are the boss, you tell the manager (the "Main Agent") to get to work, and the manager hires a bunch of workers ("Subagents") to fix all the bugs in parallel!

## How to use this skill

Using this skill is incredibly simple. Just follow these steps:

### Step 1: Navigate to your code
Open your terminal and `cd` into the repository you want to fix.
```bash
cd /path/to/your/repo
```

### Step 2: Start a new AI session
Start a fresh AI session using your Gemini CLI (or Antigravity).

### Step 3: Use the Magic Prompt! 🪄
Simply copy and paste this exact sentence to the AI:

> **Use the `ghi-fan-out-coding` skill to start a parallel resolution bonanza for all open GHIs in this repository.**

### What happens next?
1. The AI will switch into **Main Agent** mode (the manager).
2. It will look at all the open GitHub Issues in your repository.
3. It will spawn a **Subagent** (a worker) for *each* issue in the background.
4. Each worker will create its own `git worktree`, write tests, fix the code, and submit a Pull Request!
5. While they work, the Main Agent will wait. Once everyone is done, it will give you a neat summary of what was accomplished and any problems that occurred.

## Where are the logs?
Curious what the workers are doing? All logs and forensic metadata are stored safely inside your repository under:
`.gemini/execution_logs/<UUID>/`

Each issue gets its very own folder, like:
`.gemini/execution_logs/<UUID>/ghi-42/state.md`

Sit back, relax, and watch the PRs roll in! 🍿

## Future Enhancements

- 🛡️ [Real-time command guardrails via Python SDK hooks](https://github.com/palladius/gemini-cli-palladius-public-goodies/issues/3) — Block dangerous commands (`git add .`, `rm -rf .gemini`) in real-time instead of post-hoc auditing.
