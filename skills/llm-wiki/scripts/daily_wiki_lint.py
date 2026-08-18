#!/usr/bin/env uv run
# /// script
# dependencies = [
#   "rich",
# ]
# ///

import os
import sys
import re
import datetime
from rich.console import Console
from rich.panel import Panel

# Karpathy-style Wiki Librarian (Version 2.0 - Riccardo Edition)
# Pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

OBSIDIAN_VAULT = os.environ.get("OBSIDIAN_VAULT") or os.environ.get("OBSIDIAN_PBT_DIR") or os.path.expanduser("~/obsidian-pbt/") or os.path.expanduser("~/obsidian/")
KARPATHY_INDEX = os.path.join(OBSIDIAN_VAULT, "karpathy_index.md")
GEMINI_POLICY = os.path.join(OBSIDIAN_VAULT, "GEMINI.md")
console = Console()

# Policy: Avoid Root! Use these folders.
TRASH_DIR = os.path.join(OBSIDIAN_VAULT, ".trash")

FOLDER_MAP = {
    "ror": "Software Ideas",
    "rails": "Software Ideas",
    "banca": "Banca",
    "todo": "TODOs",
    "idea": "Software Ideas",
    "family": "Family",
}

def honor_gemini_policy():
    if os.path.exists(GEMINI_POLICY):
        console.print("📖 [bold magenta]Reading GEMINI.md policies...[/bold magenta]")
        with open(GEMINI_POLICY, "r") as f:
            content = f.read()
            if "No Emojis in Filenames" in content:
                console.print("🚫 [yellow]Policy active: No emojis in filenames.[/yellow]")
            if "Mutation Logging" in content:
                console.print("📝 [yellow]Policy active: Mutation logging required.[/yellow]")
        return True
    return False

def get_smart_path(link_name):
    """Determines where a new note should live based on its name."""
    link_lower = link_name.lower()
    for key, folder in FOLDER_MAP.items():
        if key in link_lower:
            return os.path.join(OBSIDIAN_VAULT, folder)
    return os.path.join(OBSIDIAN_VAULT, "Reference") # Default fallback to avoid Root

def move_to_trash(filepath):
    """Moves a file to the vault's .trash folder instead of deleting it."""
    if not os.path.exists(TRASH_DIR):
        os.makedirs(TRASH_DIR, exist_ok=True)
    
    filename = os.path.basename(filepath)
    # Add timestamp to avoid collisions in trash
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
    trash_path = os.path.join(TRASH_DIR, timestamp + filename)
    
    console.print(f"🗑️  [yellow]Moving to trash:[/yellow] {os.path.relpath(filepath, OBSIDIAN_VAULT)}")
    os.rename(filepath, trash_path)

def main():
    console.print(Panel("[bold yellow]🦞 Lobby's Karpathy-Style Wiki Librarian v2[/bold yellow]", expand=False))
    honor_gemini_policy()

    # Step 1: Fix broken links and create stubs in SMART FOLDERS
    console.print("🔍 [cyan]Scanning for broken links and creating smart stubs...[/cyan]")
    
    # Just checking Main.md for now as a test
    main_md = os.path.join(OBSIDIAN_VAULT, "Main.md")
    if os.path.exists(main_md):
        with open(main_md, "r") as f: content = f.read()
        links = re.findall(r"\[\[(.*?)\]\]", content)
        for link in links:
            target = link.split("|")[0]
            if not target or "/" in target or "http" in target: continue
            
            # If it doesn't exist in root or anywhere else
            full_target_path = os.path.join(OBSIDIAN_VAULT, target + ".md")
            if not os.path.exists(full_target_path):
                # Search if it exists elsewhere
                found = False
                for root, dirs, files in os.walk(OBSIDIAN_VAULT):
                    if target + ".md" in files:
                        found = True
                        break
                
                if not found:
                    # Create stub in SMART FOLDER
                    folder = get_smart_path(target)
                    os.makedirs(folder, exist_ok=True)
                    stub_path = os.path.join(folder, target.replace(" 🐧🧳", "").replace(" 🍼", "") + ".md")
                    if not os.path.exists(stub_path):
                        with open(stub_path, "w") as sf:
                            sf.write(f"# {target}\n\nStub created by Lobby 🦞.\n\nPath: {os.path.relpath(stub_path, OBSIDIAN_VAULT)}")
                        console.print(f"✨ Created stub: [green]{os.path.relpath(stub_path, OBSIDIAN_VAULT)}[/green]")

    # Step 2: Refresh Index
    console.print("📚 [cyan]Refreshing karpathy_index.md...[/cyan]")
    
    notes = []
    for root, dirs, files in os.walk(OBSIDIAN_VAULT):
        if ".git" in root or ".trash" in root or "node_modules" in root: continue
        for file in files:
            if file.endswith(".md") and file != "karpathy_index.md":
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, OBSIDIAN_VAULT)
                mtime = os.path.getmtime(path)
                last_updated = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                
                # Assign emoji based on folder
                emoji = "📄"
                category = "Other"
                for key, folder in FOLDER_MAP.items():
                    if folder.lower() in rel_path.lower():
                        category = folder
                        if category == "Banca": emoji = "💰"
                        elif category == "TODOs": emoji = "📝"
                        elif category == "Family": emoji = "👨‍👩‍👦‍👦"
                        elif category == "Software Ideas": emoji = "💻"
                        break
                
                notes.append({
                    "emoji": emoji,
                    "category": category,
                    "name": file,
                    "path": rel_path,
                    "mtime": mtime,
                    "updated": last_updated
                })
    
    # Sort by update date (descending)
    notes.sort(key=lambda x: x["mtime"], reverse=True)
    
    with open(KARPATHY_INDEX, "w") as f:
        f.write("# 📚 Karpathy Wiki Index\n\n")
        f.write(f"✍️ **Written by:** `~/.openclaw/workspace/bin/daily_wiki_lint.py`  \n")
        f.write(f"📅 **Last Updated:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}` 🦞\n\n")
        f.write("> 💡 Inspired by: [Andrej Karpathy's LLM Wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)\n")
        f.write("## 🏛️ Central Repository\n\n")
        f.write("| Emoji | Category | Note | Last Updated |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for n in notes[:50]: # Top 50 most recent
            f.write(f"| {n['emoji']} | {n['category']} | [[{n['path']}|{n['name']}]] | {n['updated']} |\n")

    console.print("✅ [bold green]Librarian v2 pass complete.[/bold green]")

if __name__ == "__main__":
    main()
