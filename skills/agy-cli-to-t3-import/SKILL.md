---
name: agy-cli-to-t3-import
description: >-
  (💛) Import, resuscitate, and migrate historical or interrupted Antigravity CLI sessions (`agy --conversation <cid>`) into native T3 Code threads with standard title formatting `[agy2t3] 🪦 <Topic> (<short_cid>)` and context handoff.
compatibility: antigravity, t3-code
metadata:
  version: 0.1.0
---

# 🪦 agy-cli-to-t3-import

Migrates interrupted or historical sessions from **Antigravity CLI** (`~/.gemini/antigravity-cli`) into **T3 Code** threads, generating a structured context handover, launching the thread, and tombstoning/archiving the CLI session so it does not clutter terminal session managers (`herdr`, `emorr-agy`).

## 🏷️ Naming Convention

Every thread migrated from Antigravity CLI to T3 Code **MUST** follow this title standard:

```text
[agy2t3] 🪦 <Topic/Title> (<short_cid>)
```
*Example*: `[agy2t3] 🪦 Emorragy Feature Parity (96b7e2e7)`

- `[agy2t3]`: Identifies the origin and migration protocol.
- `🪦`: Tombstone emoji symbolizing the archived/deceased CLI session whose soul is reincarnated in T3.
- `<Topic/Title>`: Concise, human-readable summary of the work.
- `(<short_cid>)`: First 8 characters of the UUID to maintain traceability to `transcript.jsonl`.

---

## 🛠️ Migration Workflow

### 1. Locate the Source CLI Session
CLI sessions live in:
- SQLite Database: `~/.gemini/antigravity-cli/conversation_summaries.db`
- Per-session database: `~/.gemini/antigravity-cli/conversations/<cid>.db`
- Logs & Transcripts: `~/.gemini/antigravity-cli/brain/<cid>/.system_generated/logs/transcript.jsonl`

To inspect the last steps:
```python
import json
from pathlib import Path

cid = "96b7e2e7-ead7-41c2-b3ef-0072df5bb8a4"
tpath = Path.home() / ".gemini" / "antigravity-cli" / "brain" / cid / ".system_generated" / "logs" / "transcript.jsonl"
with open(tpath) as f:
    lines = [json.loads(l) for l in f if l.strip()]
print(f"Total steps: {len(lines)}")
for s in lines[-4:]:
    print(s.get("type"), s.get("status"), (s.get("content") or "")[:80])
```

### 2. Extract the Handover Context
Build an executive handover brief:
1. **Target Project**: Path to the repository on disk (e.g. `/home/riccardo/git/emorr-agy`).
2. **Track/Goal**: Original user request, feature goal, or conductor track.
3. **Exact Point of Interruption**:
   - What was the last action completed?
   - Was a tool call mid-flight (view_file, replace_file_content, run_command)?
   - What was the planned next step?
4. **Relevant Files**: Paths to files modified or under active review.

### 3. Launch the Thread in T3 Code
1. Match the workspace root to an existing T3 project via `t3_project_list`.
2. Launch the top-level thread via `t3_thread_launch`:
   - `projectId`: `<matched_project_id>`
   - `title`: `[agy2t3] 🪦 <Topic> (<short_cid>)`
   - `workspaceStrategy`: `{"type": "root"}`
   - `message`: The formatted handover Markdown prompt.
3. Read the launched thread via `t3_thread_read` to verify initialization.
4. Always reference the newly created thread using its verbatim Markdown link: `<t3-thread://v2/...>`.

### 4. Tombstone / Archive the CLI Session
To prevent the session from appearing in live lists or being accidentally re-opened:
1. Write or update the annotation file:
   ```protobuf
   # ~/.gemini/antigravity-cli/annotations/<cid>.pbtxt
   title: "<Topic> (Transferred to T3)"
   archived: true
   ```
2. Clean any stale lock files if present:
   ```bash
   rm -f ~/.gemini/antigravity-cli/presence/<cid>.lock
   ```

---

## 💻 CLI Helper Script

The bundled script `scripts/agy2t3.py` automates inspecting and generating handover prompts:

```bash
python3 scripts/agy2t3.py list
python3 scripts/agy2t3.py inspect <cid>
python3 scripts/agy2t3.py archive <cid>
```
