#!/usr/bin/env python3
"""Zero-dependency OS Desktop Toast helper for Level-1 Focusless Browser Use.

Warns the user when an agent begins controlling a background tab (and asks them not to focus
that window or rely on shared clipboard during copy/paste), then releases responsibility with
a Hitchhiker's Guide to the Galaxy completion toast once finished.

Platform Support:
  - Linux: Verified via `notify-send` (libnotify-bin).
  - macOS: Best-effort via `osascript` (untested / ?).
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import platform
import shutil
import subprocess
import sys


def send_desktop_notification(title: str, body: str, urgency: str = "normal") -> bool:
    try:
        system = platform.system().lower()
        if system == "darwin" and shutil.which("osascript"):
            script = f"display notification {json.dumps(body)} with title {json.dumps(title)}"
            subprocess.run(["osascript", "-e", script], check=False, timeout=3.0)
            return True
        if shutil.which("notify-send") and (
            os.environ.get("DISPLAY")
            or os.environ.get("WAYLAND_DISPLAY")
            or os.environ.get("DBUS_SESSION_BUS_ADDRESS")
        ):
            subprocess.run(
                [
                    "notify-send",
                    "--app-name=focusless-browser",
                    "--urgency",
                    urgency,
                    "--expire-time=9000",
                    title,
                    body,
                ],
                check=False,
                timeout=3.0,
            )
            return True
    except Exception:
        pass
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Level-1 Focusless Browser OS notification helper.")
    parser.add_argument("phase", choices=["start", "done", "error"])
    parser.add_argument("--user", default=getpass.getuser() or os.environ.get("USER") or "human")
    parser.add_argument("--identity", default="authenticated-profile")
    parser.add_argument("--task", default="browser automation")
    parser.add_argument("--url", default="https://example.com")
    args = parser.parse_args()

    if args.phase == "start":
        ok = send_desktop_notification(
            "🤖 Focusless Browser Use — Active",
            f"Hi {args.user}, I'm controlling your browser ({args.identity}) to run '{args.task}' "
            f"on {args.url}. Please don't focus that window — copy/paste may briefly interfere until I tell you I'm done!",
        )
    elif args.phase == "done":
        ok = send_desktop_notification(
            "🌌 Done! Don't Panic — Over to You",
            f"I'm done with {args.identity}! Don't Panic — the SEP (Somebody Else's Problem) field has disengaged, "
            f"so {args.url} is now 100% your responsibility. So long, and thanks for all the fish 🐬",
        )
    else:
        ok = send_desktop_notification(
            "⚠️ Focusless Browser Use — Stopped",
            f"Hit a snag while driving {args.identity} on {args.url} — releasing browser focus & clipboard back to {args.user}. Don't Panic!",
            urgency="critical",
        )

    return 0 if ok else 0


if __name__ == "__main__":
    sys.exit(main())
