#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys

# 🦞 Hummerli Portable TTS Script (Python Edition)

def main():
    parser = argparse.ArgumentParser(description="Hummerli Pronunciation Script")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--male", action="store_true", help="Use Conrad (Rijckard - Translator Clone)")
    group.add_argument("--female", action="store_true", help="Use Frau Blücher 🐎 (Tutor)")
    parser.add_argument("-p", "--prompt", required=True, help="Text to pronounce")
    parser.add_argument("-s", "--speed", default="-10%", help="TTS Speed (default: -10%%)")
    parser.add_argument("-t", "--target", help="Override chat ID")

    args = parser.parse_args()

    # Voices
    voice = "de-DE-KatjaNeural" if args.female else "de-DE-ConradNeural"
    
    # Environment Setup
    env = os.environ.copy()
    if args.target:
        env["OCTTS_TARGET"] = args.target
    elif "OCTTS_TARGET" not in env:
        # Default target placeholder - update for your instance
        env["OCTTS_TARGET"] = "" 

    # Look for octts in the skill's scripts directory first, then fallback
    base_dir = os.path.dirname(os.path.abspath(__file__))
    octts_path = os.path.join(base_dir, "octts")
    
    if not os.path.exists(octts_path):
        # Fallback to system-wide openclaw location
        octts_path = os.path.expanduser("~/.openclaw/workspace/bin/octts")
    
    if not os.path.exists(octts_path):
        print(f"Error: octts utility not found in {base_dir} or standard location.", file=sys.stderr)
        sys.exit(1)

    # Call the core octts utility
    cmd = [octts_path, voice, args.speed, args.prompt]
    print(f"🎙️ Running: {' '.join(cmd)} (using {octts_path})")
    subprocess.run(cmd, env=env)

if __name__ == "__main__":
    main()
