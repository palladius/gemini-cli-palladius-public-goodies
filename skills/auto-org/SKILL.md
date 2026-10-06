---
name: auto-org
description: Use when Desktop or Downloads are cluttered with unorganized files, screenshots, receipts, trip documents, or stale installers. Safely categorizes files into ~/Auto.org/ subfolders, stages obsolete items in 'vecchiume', generates markdown triage logs with auto-tagging, and connects to Obsidian.
version: 1.0.0
author: Riccardo Carlesso & Ermete Bottazzi
license: Apache-2.0
compatibility: Gemini CLI, Hermes Agent, Antigravity
metadata:
  version: 1.0.0
  hermes_tags: "productivity, cleanup, files, macos, triage, desktop, downloads, obsidian"
  hermes_related_skills: "carlessian-obsidian, ocr-and-documents"
---

# Auto.org File Organizer & Triage Skill 🚛📂

Organize cluttered `~/Desktop` and `~/Downloads` directories intelligently by inspecting file names, types, ages, and travel heuristics, moving items into structured `~/Auto.org/` subfolders while staging obsolete files into a non-destructive `vecchiume` quarantine area.

---

## 🎯 When to Use
- User has dozens or hundreds of loose screenshots, PDFs, installers, or downloads on `~/Desktop` or `~/Downloads`.
- User asks to clean up, sort, or reorganize loose files into categorized folders (`Auto.org`).
- User needs an audit trail of moved files with rationale and markdown tags (`#screenshot`, `#scontrino`, `#viaggi`, `#vecchiume`).
- User asks for a summary of old, stale files to consider for deletion without risking silent data loss.

**Do NOT use for:**
- Destructive one-line shell purges (`rm -rf ~/Downloads/*`).
- System-managed library directories (`~/Library`, Photos.app library, iCloud container internals).

---

## 📁 Classification Taxonomy

All files are classified and safely moved into `~/Auto.org/` subdirectories:

| Subfolder | Classification Rules & Triggers | Tags |
|---|---|---|
| `screenshots/` | macOS screen grabs (`Screen Shot*`, `Screenshot*`, `Schermata*`, `CleanShot*`) | `#screenshot` |
| `scontrini/` | Invoices, expense receipts, tax slips (`scontrino`, `fattura`, `receipt`, `invoice`, `rechnung`, `coop`, `migros`, `amazon_order`) | `#scontrino`, `#spese` |
| `viaggi/` | Active/recent flight tickets, boarding passes, train bookings (`volo`, `flight`, `boarding`, `easyjet`, `volotea`, `trenitalia`, `sbb`, `hotel`, `airbnb`) | `#viaggi`, `#<vettore>` |
| `presentazioni/` | Slide decks and keynotes (`.key`, `.pptx`, `.slides`, `*deck*`, `*presentation*`) | `#presentazioni`, `#deck` |
| `idee/` | Architecture sketches, mind maps, drafts (`.drawio`, `.excalidraw`, `.sketch`, `*idea*`, `*bozza*`) | `#idee`, `#progetti` |
| `documenti/` | Generic PDFs, office documents, spreadsheets (`.pdf`, `.docx`, `.pages`, `.xlsx`, `.csv`) | `#documenti` |
| `media/` | Camera photos, personal videos, audio recordings (excluding screenshots) | `#media` |
| `vecchiume/` | **Staging area for candidate deletion:** stale installers (`.dmg`, `.pkg` >14 days), past flights/events (>7 days ago), files untouched >90 days | `#vecchiume`, `#stale` |

---

## 🛡️ The Non-Destructive "Vecchiume" Staging Rule

1. **NEVER silently delete files**: The agent and script must never run `rm` on user files.
2. **Move to Staging**: Outdated installers (`.dmg`, `.pkg`), obsolete boarding passes of already completed trips, and stale temp downloads are moved to `~/Auto.org/vecchiume/`.
3. **Report to User**: Present an explicit summary:
   > *"Hai 27 file nel vecchiume (il più vecchio di 6 mesi fa, il più recente di 92 giorni fa). Vuoi esaminarli prima della rimozione manuale?"*
4. **Collision Proof**: If a file with the same name already exists in the target directory, it automatically appends a numbered suffix `(1)`, `(2)`, preventing any overwrite.

---

## 📝 Markdown Audit Log & Obsidian Integration

Every triage run automatically updates:
1. `~/Auto.org/TRIAGE_LOG.md`: Chronological log with run date, counts per category, vecchiume alert, and per-file migration rationale with tags.
2. `~/Documents/PBTPersonalSync/System/AutoOrg/Triage_History.md` (if Obsidian vault exists): Synced copy formatted for Obsidian backlinks and Dataview querying.

---

## 🚀 CLI Commands & Recipes

The skill comes with a built-in Python triage engine:

```bash
# Preview what would be organized without moving files (Dry Run)
$SKILL_DIR/scripts/auto_org.py

# Limit preview to first 10 files
$SKILL_DIR/scripts/auto_org.py --limit 10

# Execute actual moves
$SKILL_DIR/scripts/auto_org.py --execute

# Scan only Desktop (or only Downloads)
$SKILL_DIR/scripts/auto_org.py --source ~/Desktop --execute

# Custom stale thresholds (e.g. 60 days for stale, 7 days for installers)
$SKILL_DIR/scripts/auto_org.py --days-stale 60 --days-installer 7 --execute

# Output JSON for programmatic tooling
$SKILL_DIR/scripts/auto_org.py --json
```

---

## ⚠️ Common Pitfalls

1. **Running without `--execute` when the user expected files to move**: Always run dry-run first to inspect, report results to the user, and use `--execute` to apply.
2. **Hardcoding absolute usernames in script paths**: Always use `os.path.expanduser("~")` or `Path.home()` to ensure portability across machines.
3. **Overwriting files with identical names**: Always rely on `get_safe_destination()` to append sequence numbers.
4. **Treating recent flight tickets as vecchiume**: Ensure flight dates are checked. A flight for *next week* belongs in `viaggi/`, only flights from *the past* belong in `vecchiume/`.

---

## ✅ Verification Checklist

- [ ] File exists at `skills/auto-org/SKILL.md`
- [ ] Valid YAML frontmatter with `name`, `description`, `version`, `author`, `license`
- [ ] `scripts/auto_org.py` is executable (`chmod +x`) and passes syntax / lint checks
- [ ] Dry-run tested successfully against local `~/Desktop` and `~/Downloads`
- [ ] Non-destructive `vecchiume` logic properly stages old items without deletion
- [ ] Triage log written in markdown with proper tags
