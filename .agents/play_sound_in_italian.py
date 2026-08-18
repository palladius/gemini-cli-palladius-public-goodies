#!/usr/bin/env python3
import sys
import os
import json
import datetime
import subprocess

def main():
    # 1. Say voice line in Italian
    spd_say_result = {}
    try:
        res = subprocess.run(
            ["spd-say", "-l", "it", "Sto uscendo da anti gravita permanente"],
            capture_output=True,
            text=True,
            check=False
        )
        spd_say_result = {
            "exit_code": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr
        }
    except Exception as e:
        spd_say_result = {
            "error": str(e)
        }
        sys.stderr.write(f"Failed to play sound: {e}\n")

    # 2. Print 'Chumbia!' to terminal
    print("Chumbia!")

    # 3. Read stdin payload (JSON) sent by Antigravity on Stop event
    stdin_data = ""
    try:
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
    except Exception as e:
        stdin_data = f"Error reading stdin: {e}"

    payload = {}
    if stdin_data:
        try:
            payload = json.loads(stdin_data)
        except Exception as e:
            payload = {"raw_stdin": stdin_data, "json_parse_error": str(e)}

    # 4. Generate timestamp and log filename
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M")
    filename = f".agy-terminated.{timestamp}.log"

    # 5. Gather session details and environment variables
    # Filter or serialize env vars safely
    env_vars = dict(os.environ)

    log_content = {
        "timestamp": now.isoformat(),
        "spd_say_result": spd_say_result,
        "session_details": payload,
        "environment_variables": env_vars
    }

    # 6. Write log file in current working directory
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(log_content, f, indent=2)
    except Exception as e:
        sys.stderr.write(f"Failed to write log file {filename}: {e}\n")

if __name__ == "__main__":
    main()
