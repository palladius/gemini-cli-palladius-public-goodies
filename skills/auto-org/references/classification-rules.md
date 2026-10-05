# Auto.org Classification & Heuristic Rules Reference

This document describes the classification taxonomy, heuristic triggers, metadata detection, and age policies used by `auto-org`.

## 1. Directory Taxonomy under `~/Auto.org/`

| Folder | Intended Content | Detection Signals |
|---|---|---|
| `screenshots/` | Desktop screen grabs, UI crops, window recordings | Filename patterns matching macOS defaults (`Screen Shot*`, `Screenshot*`, `Schermata*`, `CleanShot*`), image files with timestamp patterns |
| `scontrini/` | Expense receipts, retail invoices, order confirmations | Keywords: `scontrino`, `fattura`, `receipt`, `invoice`, `rechnung`, `quittance`, `bolletta`, `ordine`, `amazon_order`, `migros`, `coop`, `apple_invoice`, `google_invoice`, `uber_receipt` |
| `viaggi/` | Boarding passes, flight itineraries, train tickets, bookings | Keywords: `volo`, `flight`, `boarding`, `boardingpass`, `carta_imbarco`, `easyjet`, `ryanair`, `volotea`, `swiss`, `lufthansa`, `trenitalia`, `italo`, `sbb`, `booking`, `airbnb`, `pkpass` |
| `presentazioni/` | Slide decks, keynotes, talk materials | Extensions: `.key`, `.pptx`, `.ppt`, `.slides`; or keywords: `presentation`, `presentazione`, `deck`, `slides`, `keynote`, `talk` |
| `idee/` | Brainstorms, sketches, mind maps, drafts | Extensions: `.drawio`, `.excalidraw`, `.sketch`, `.fig`, `.mindnode`; or keywords: `idea`, `bozza`, `draft`, `sketch`, `appunto`, `wireframe` |
| `documenti/` | Generic documents, spreadsheets, certificates | Extensions: `.pdf`, `.docx`, `.pages`, `.xlsx`, `.numbers`, `.csv`, `.txt` |
| `media/` | Camera photos, personal videos, audio recordings | Non-screenshot image formats (`.jpg`, `.jpeg`, `.heic`), video (`.mp4`, `.mov`), audio (`.mp3`, `.wav`, `.m4a`) |
| `vecchiume/` | **Staging area for obsolete / candidate-for-deletion files** | (1) Software installers (`.dmg`, `.pkg`, `.iso`, `.exe`) older than 14 days; (2) Past travel documents (flight/ticket date > 7 days in the past); (3) Generic files unedited/untouched > 90 days |

## 2. Non-Destructive Vecchiume Policy

1. **Zero Silent Deletions**: Under no circumstances does `auto-org` delete files automatically with `rm` or unlinking.
2. **Quarantine / Staging**: Files deemed obsolete or stale are moved into `~/Auto.org/vecchiume/`.
3. **Audit Log & Summary Prompt**: Every execution outputs the count, age range, and total disk space consumed in `vecchiume/`. The agent presents this summary to the user:
   > *"Hai N file nel vecchiume (il più vecchio di X mesi fa). Vuoi esaminarli prima della rimozione manuale?"*
4. **Human in the Loop**: Only after explicit human confirmation can files staged in `vecchiume/` be purged.

## 3. Auto-Tagging & Obsidian Sync

When an Obsidian vault is present (e.g. `~/Documents/PBTPersonalSync`):
- Entries are recorded with inline tags: `#screenshot`, `#scontrino`, `#viaggi`, `#presentazioni`, `#idee`, `#vecchiume`.
- Receipts and tickets can be cross-referenced with Travel logs in the Obsidian vault.
- Log runs append to `System/AutoOrg/Triage_History.md`.
