#!/usr/bin/env python3
"""
agy2t3 — Helper to inspect Antigravity CLI sessions and prepare T3 handover briefs.
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

HOME = Path.home()
CLI_DIR = HOME / ".gemini" / "antigravity-cli"
AG2_DIR = HOME / ".gemini" / "antigravity"
EMORR_DIR = HOME / ".emorr-agy"


def get_session_info(cid_prefix: str) -> dict | None:
    db_path = CLI_DIR / "conversation_summaries.db"
    if not db_path.is_file():
        return None

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM conversation_summaries WHERE conversation_id LIKE ? ORDER BY last_modified_time DESC LIMIT 1",
        (f"{cid_prefix}%",),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    cid = row["conversation_id"]
    tpath = CLI_DIR / "brain" / cid / ".system_generated" / "logs" / "transcript.jsonl"
    steps = []
    if tpath.is_file():
        try:
            with open(tpath, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.strip():
                        steps.append(json.loads(line))
        except Exception:
            pass

    return {
        "id": cid,
        "short_id": cid[:8],
        "title": row["title"] or "",
        "preview": row["preview"] or "",
        "workspace_uris": row["workspace_uris"] or "[]",
        "last_modified": row["last_modified_time"],
        "step_count": len(steps),
        "steps": steps,
    }


def archive_session(cid: str, title: str = "") -> None:
    t = title or "Transferred to T3"
    content = f'title: "{t} (Transferred to T3)"\narchived: true\narchived:true\n'

    # 1. Write CLI annotation
    annot_cli = CLI_DIR / "annotations"
    annot_cli.mkdir(parents=True, exist_ok=True)
    (annot_cli / f"{cid}.pbtxt").write_text(content, encoding="utf-8")

    # 2. Write AG2UI annotation
    annot_ag2 = AG2_DIR / "annotations"
    annot_ag2.mkdir(parents=True, exist_ok=True)
    (annot_ag2 / f"{cid}.pbtxt").write_text(content, encoding="utf-8")

    # 3. Write emorr-agy cache to mark not worth resuscitating
    cache_dir = EMORR_DIR / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{cid}.json"
    cache_file.write_text(
        json.dumps(
            {
                "about": f"{t} (Transferred to T3)",
                "user_input_pending": False,
                "worth_resuscitate": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # 4. Remove stale lock
    lock_file = CLI_DIR / "presence" / f"{cid}.lock"
    if lock_file.exists():
        lock_file.unlink()

    print(f"🪦 Session {cid[:8]} archived across CLI, AG2UI, and emorr-agy successfully.")


def main():
    parser = argparse.ArgumentParser(description="Antigravity CLI to T3 Code Bridge")
    sub = parser.add_subparsers(dest="cmd")

    inspect_p = sub.add_parser("inspect", help="Inspect a CLI session")
    inspect_p.add_argument("cid", help="Conversation ID or prefix")

    archive_p = sub.add_parser("archive", help="Archive a CLI session")
    archive_p.add_argument("cid", help="Conversation ID or prefix")
    archive_p.add_argument("--title", default="", help="Optional title")

    args = parser.parse_args()

    if args.cmd == "inspect":
        info = get_session_info(args.cid)
        if not info:
            print(f"Session not found: {args.cid}", file=sys.stderr)
            sys.exit(1)
        print(f"ID: {info['id']}")
        print(f"Title: {info['title']}")
        print(f"Steps: {info['step_count']}")
        print(f"Last Modified: {info['last_modified']}")
        print(f"Workspace: {info['workspace_uris']}")
        print("\nLast 3 steps:")
        for s in info["steps"][-3:]:
            print(f"  [{s.get('type')}] status={s.get('status')} content={str(s.get('content'))[:80]}")
    elif args.cmd == "archive":
        info = get_session_info(args.cid)
        cid = info["id"] if info else args.cid
        title = info["title"] if info else args.title
        archive_session(cid, title)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
