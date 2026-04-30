#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
import sys
import re
import os
import argparse

def validate(filepath, max_chars=None, max_words=None):
    if not os.path.exists(filepath):
        print(f"❌ Error: File '{filepath}' not found.")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"📊 Validating Proposal: {filepath}\n")

    # Simple section extraction
    title_match = re.search(r'## 🏷️ Title\n(.*?)(?=##|$)', content, re.DOTALL)
    abstract_match = re.search(r'## 📝 Abstract\n(.*?)(?=##|$)', content, re.DOTALL)
    bio_match = re.search(r'## 🗣️ Bio\n(.*?)(?=##|$)', content, re.DOTALL)

    if not title_match:
        print("❌ Missing '## 🏷️ Title' section")
    else:
        print(f"✅ Title found: {title_match.group(1).strip()[:40]}...")

    if not bio_match:
        print("❌ Missing '## 🗣️ Bio' section")
    else:
        print("✅ Bio section found.")

    if not abstract_match:
        print("❌ Missing '## 📝 Abstract' section")
        sys.exit(1)

    abstract_text = abstract_match.group(1).strip()
    char_count = len(abstract_text)
    word_count = len(abstract_text.split())

    print("\n📈 Abstract Stats:")
    print(f"   Characters: {char_count}")
    print(f"   Words:      {word_count}")

    failed = False
    print("") # Empty line before pass/fail results
    if max_chars is not None:
        if char_count > max_chars:
            print(f"❌ FAIL: Character count ({char_count}) exceeds maximum allowed ({max_chars}).")
            failed = True
        else:
            print(f"✅ PASS: Character count ({char_count}) is within limit ({max_chars}).")

    if max_words is not None:
        if word_count > max_words:
            print(f"❌ FAIL: Word count ({word_count}) exceeds maximum allowed ({max_words}).")
            failed = True
        else:
            print(f"✅ PASS: Word count ({word_count}) is within limit ({max_words}).")

    if failed:
        sys.exit(1)

    print("\n💡 Tip: All constraints met! Good luck with your CFP! 🚀")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate CFP Proposal Markdown.")
    parser.add_argument("filepath", help="Path to the proposal markdown file")
    parser.add_argument("--max-chars", type=int, help="Maximum allowed characters in the abstract")
    parser.add_argument("--max-words", type=int, help="Maximum allowed words in the abstract")
    
    args = parser.parse_args()
    validate(args.filepath, args.max_chars, args.max_words)
