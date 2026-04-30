#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
import sys
import re
import os

def validate(filepath):
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
        return

    abstract_text = abstract_match.group(1).strip()
    char_count = len(abstract_text)
    char_count_no_spaces = len(abstract_text.replace(" ", "").replace("\n", ""))
    word_count = len(abstract_text.split())

    print("\n📈 Abstract Stats:")
    print(f"   Characters (with spaces):    {char_count}")
    print(f"   Characters (without spaces): {char_count_no_spaces}")
    print(f"   Words:                       {word_count}")

    print("\n💡 Tip: Cross-check these stats against your conference constraints!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ./validate_proposal.py <proposal_markdown_file>")
        sys.exit(1)
    validate(sys.argv[1])