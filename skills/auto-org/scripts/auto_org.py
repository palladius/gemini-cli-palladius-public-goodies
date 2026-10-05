#!/usr/bin/env python3
"""
auto_org.py - Intelligent Desktop & Downloads file triage tool.

Scans cluttered folders (e.g. ~/Desktop and ~/Downloads), categorizes files based on
name heuristics, timestamps, and content types into ~/Auto.org/<category>/, moves them safely,
and maintains an audit log with auto-tags. Includes a non-destructive 'vecchiume' staging
area for candidate cleanup review.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CATEGORIES = [
    "screenshots",
    "scontrini",
    "viaggi",
    "presentazioni",
    "idee",
    "documenti",
    "media",
    "vecchiume",
]

INSTALLER_EXTS = {".dmg", ".pkg", ".iso", ".exe", ".msi", ".deb", ".rpm"}
PRESENTATION_EXTS = {".key", ".pptx", ".ppt"}
IDEA_EXTS = {".drawio", ".excalidraw", ".sketch", ".fig", ".mindnode", ".xmind"}
DOC_EXTS = {".pdf", ".docx", ".doc", ".pages", ".xlsx", ".xls", ".numbers", ".csv", ".txt", ".rtf"}
MEDIA_EXTS = {
    ".jpg", ".jpeg", ".heic", ".png", ".gif", ".webp", ".tiff", ".svg",
    ".mp4", ".mov", ".m4v", ".mkv", ".avi",
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"
}

SCREENSHOT_PATTERNS = [
    re.compile(r"^(screen\s*shot|screenshot|schermata|cleanshot|capture\s*d’écran|bildschirmfoto)", re.IGNORECASE),
    re.compile(r"^schermata\s*\d{4}-\d{2}-\d{2}", re.IGNORECASE),
    re.compile(r"^screenshot\s*\d{4}-\d{2}-\d{2}", re.IGNORECASE),
]

SCONTRINI_KEYWORDS = [
    "scontrino", "fattura", "ricevuta", "receipt", "invoice", "rechnung", "quittance",
    "bolletta", "order_summary", "ordine_amazon", "amazon_order", "migros", "coop_pronto",
    "apple_invoice", "google_invoice", "uber_receipt", "taxi_receipt"
]

VIAGGI_KEYWORDS = [
    "boarding", "boardingpass", "boarding-pass", "carta_imbarco", "carta-imbarco",
    "volo", "flight", "itinerary", "itinerario", "booking", "prenotazione",
    "easyjet", "ryanair", "volotea", "swiss", "lufthansa", "trenitalia", "italo",
    "sbb", "airbnb", "hotel", "pkpass"
]

PRESENTAZIONI_KEYWORDS = [
    "presentation", "presentazione", "slides", "slide_deck", "deck", "keynote", "talk"
]

IDEE_KEYWORDS = [
    "idea", "idee", "bozza", "draft", "sketch", "appunto", "brainstorm", "wireframe", "diagramma"
]

IGNORE_NAMES = {
    ".DS_Store", "desktop.ini", ".localized", ".Trash", "$RECYCLE.BIN"
}

IGNORE_EXTENSIONS = {
    ".crdownload", ".download", ".part", ".tmp"
}


def human_size(n_bytes: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n_bytes < 1024.0:
            return f"{n_bytes:.1f} {unit}" if unit != "B" else f"{int(n_bytes)} B"
        n_bytes /= 1024.0
    return f"{n_bytes:.1f} PB"


def extract_date_from_string(text: str) -> Optional[datetime.date]:
    """Attempts to find YYYY-MM-DD or YYYYMMDD in a filename."""
    m = re.search(r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})", text)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    return None


def get_safe_destination(dest_dir: Path, filename: str) -> Path:
    dest_path = dest_dir / filename
    if not dest_path.exists():
        return dest_path

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def classify_file(path: Path, days_stale: int = 90, days_installer: int = 14) -> Tuple[str, str, List[str]]:
    """
    Returns (category, reason, tags).
    """
    name = path.name
    lower_name = name.lower()
    suffix = path.suffix.lower()

    now = datetime.datetime.now()
    mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
    age_days = (now - mtime).days

    # 1. Installers check (Vecchiume candidate if older than days_installer)
    if suffix in INSTALLER_EXTS:
        if age_days >= days_installer:
            return (
                "vecchiume",
                f"Vecchio installer/disco immagine ({suffix}, {age_days} giorni fa)",
                ["#vecchiume", "#installer"]
            )
        return (
            "documenti",
            f"Installer recente ({suffix}, {age_days} giorni fa)",
            ["#software", "#installer"]
        )

    # 2. Check for screenshot patterns
    for pat in SCREENSHOT_PATTERNS:
        if pat.search(name):
            return (
                "screenshots",
                f"Pattern screenshot macOS/CleanShot rilevato nel nome",
                ["#screenshot"]
            )

    # 3. Scontrini / Spese
    for kw in SCONTRINI_KEYWORDS:
        if kw in lower_name:
            return (
                "scontrini",
                f"Keyword scontrino/spesa '{kw}' trovata nel nome",
                ["#scontrino", "#spese"]
            )

    # 4. Viaggi
    for kw in VIAGGI_KEYWORDS:
        if kw in lower_name:
            # Check if this trip document is in the past
            doc_date = extract_date_from_string(lower_name)
            if doc_date and (datetime.date.today() - doc_date).days > 7:
                # Travel document with date > 7 days ago -> candidate for vecchiume
                return (
                    "vecchiume",
                    f"Documento di viaggio passato ({kw}, data {doc_date.isoformat()}, oltre 7 giorni fa)",
                    ["#vecchiume", "#viaggio_passato", f"#{kw}"]
                )
            if age_days > 60:
                # Or file modified > 60 days ago
                return (
                    "viaggi",
                    f"Documento di viaggio ('{kw}', archiviato da {age_days} giorni)",
                    ["#viaggi", f"#{kw}"]
                )
            return (
                "viaggi",
                f"Documento di viaggio/volo recente '{kw}'",
                ["#viaggi", f"#{kw}"]
            )

    # 5. Presentazioni
    if suffix in PRESENTATION_EXTS or any(kw in lower_name for kw in PRESENTAZIONI_KEYWORDS):
        return (
            "presentazioni",
            f"Presentazione o slide deck ({suffix or 'keyword presentation'})",
            ["#presentazioni", "#deck"]
        )

    # 6. Idee e Progetti
    if suffix in IDEA_EXTS or any(kw in lower_name for kw in IDEE_KEYWORDS):
        return (
            "idee",
            f"Bozza, schema o idea ({suffix or 'keyword idea'})",
            ["#idee", "#progetti"]
        )

    # 7. Stale generic files -> Vecchiume
    if age_days >= days_stale:
        return (
            "vecchiume",
            f"File non modificato da oltre {age_days} giorni (soglia stale: {days_stale}gg)",
            ["#vecchiume", "#stale"]
        )

    # 8. Media (audio / video / generic photos)
    if suffix in MEDIA_EXTS:
        return (
            "media",
            f"File multimediale ({suffix})",
            ["#media"]
        )

    # 9. Generic documents
    if suffix in DOC_EXTS:
        return (
            "documenti",
            f"Documento di testo/archivio ({suffix})",
            ["#documenti"]
        )

    # Fallback to documenti
    return (
        "documenti",
        f"File generico ({suffix or 'senza estensione'})",
        ["#generico"]
    )


def plan_and_triage(
    sources: List[Path],
    dest_base: Path,
    dry_run: bool = True,
    days_stale: int = 90,
    days_installer: int = 14,
    limit: Optional[int] = None
) -> Dict:
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "dry_run": dry_run,
        "scanned_count": 0,
        "actions": [],
        "categories": {cat: 0 for cat in CATEGORIES},
        "vecchiume_details": []
    }

    scanned_files: List[Path] = []
    for src in sources:
        if not src.exists() or not src.is_dir():
            continue
        for entry in src.iterdir():
            if entry.is_dir():
                continue
            if entry.name in IGNORE_NAMES or entry.name.startswith("."):
                continue
            if entry.suffix.lower() in IGNORE_EXTENSIONS:
                continue
            scanned_files.append(entry)

    results["scanned_count"] = len(scanned_files)
    if limit:
        scanned_files = scanned_files[:limit]

    for file_path in scanned_files:
        cat, reason, tags = classify_file(
            file_path,
            days_stale=days_stale,
            days_installer=days_installer
        )
        cat_dir = dest_base / cat
        safe_target = get_safe_destination(cat_dir, file_path.name)
        file_stat = file_path.stat()
        file_size = file_stat.st_size
        mtime = datetime.datetime.fromtimestamp(file_stat.st_mtime)

        action = {
            "source": str(file_path),
            "filename": file_path.name,
            "category": cat,
            "target": str(safe_target),
            "reason": reason,
            "tags": tags,
            "size_bytes": file_size,
            "size_human": human_size(file_size),
            "mtime": mtime.strftime("%Y-%m-%d %H:%M"),
            "age_days": (datetime.datetime.now() - mtime).days
        }

        if not dry_run:
            cat_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(safe_target))

        results["actions"].append(action)
        results["categories"][cat] = results["categories"].get(cat, 0) + 1

        if cat == "vecchiume":
            results["vecchiume_details"].append(action)

    return results


def write_triage_log(dest_base: Path, triage_data: Dict, obsidian_vault: Optional[Path] = None):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode_str = "DRY-RUN (nessun file spostato)" if triage_data["dry_run"] else "LIVE EXECUTION (file spostati)"

    lines = [
        f"\n## Auto.org Triage Run: {now_str} [{mode_str}]\n",
        f"- **File analizzati:** {triage_data['scanned_count']}",
        f"- **File processati:** {len(triage_data['actions'])}",
        "- **Ripartizione per categoria:**"
    ]

    for cat, count in triage_data["categories"].items():
        if count > 0:
            lines.append(f"  - `{cat}`: {count}")

    vecchiume = triage_data["vecchiume_details"]
    if vecchiume:
        total_v_size = sum(item["size_bytes"] for item in vecchiume)
        oldest_days = max(item["age_days"] for item in vecchiume)
        newest_days = min(item["age_days"] for item in vecchiume)
        lines.append(f"\n### 🗑️ Vecchiume Alert")
        lines.append(
            f"Trovati **{len(vecchiume)} file** nel vecchiume ({human_size(total_v_size)} totali). "
            f"Il più vecchio risale a **{oldest_days} giorni fa**, il più recente a **{newest_days} giorni fa**."
        )
        lines.append("*Nota: Nessun file è stato rimosso o distrutto. Verifica manuale consigliata.*")

    lines.append("\n### 📋 Dettaglio Azioni")
    for act in triage_data["actions"]:
        tags_str = " ".join(act["tags"])
        lines.append(
            f"- `{act['filename']}` ➔ `{act['category']}/` "
            f"({act['size_human']}, {act['age_days']}gg fa) — *{act['reason']}* {tags_str}"
        )

    log_content = "\n".join(lines) + "\n"

    # Write to ~/Auto.org/TRIAGE_LOG.md
    dest_base.mkdir(parents=True, exist_ok=True)
    triage_log_file = dest_base / "TRIAGE_LOG.md"
    with open(triage_log_file, "a", encoding="utf-8") as f:
        f.write(log_content)

    # Optional: mirror or link into Obsidian vault
    if obsidian_vault and obsidian_vault.exists():
        obs_dir = obsidian_vault / "System" / "AutoOrg"
        obs_dir.mkdir(parents=True, exist_ok=True)
        obs_log = obs_dir / "Triage_History.md"
        with open(obs_log, "a", encoding="utf-8") as f:
            f.write(log_content)


def print_summary(triage_data: Dict):
    dry = triage_data["dry_run"]
    print("=" * 60)
    print(f"🚛 AUTO.ORG TRIAGE REPORT {'[SIMULAZIONE DRY-RUN]' if dry else '[ESEGUITO]'}")
    print("=" * 60)
    print(f"File analizzati: {triage_data['scanned_count']}")
    print(f"Operazioni:      {len(triage_data['actions'])}")
    print("\nSuddivisione per cartella di destinazione:")
    for cat, count in triage_data["categories"].items():
        if count > 0:
            print(f"  • {cat.ljust(15)} : {count}")

    vecchiume = triage_data["vecchiume_details"]
    if vecchiume:
        total_v_size = sum(item["size_bytes"] for item in vecchiume)
        oldest_days = max(item["age_days"] for item in vecchiume)
        newest_days = min(item["age_days"] for item in vecchiume)
        print("\n" + "-" * 60)
        print("🗑️ VECCHIUME STAGING REPORT:")
        print(f"  Totale file: {len(vecchiume)} ({human_size(total_v_size)})")
        print(f"  Età file: da {newest_days} a {oldest_days} giorni fa")
        print("  Proposta: Valuta la cancellazione manuale dei file obsoleti in Auto.org/vecchiume/")
        print("-" * 60)

    if dry:
        print("\n💡 Per eseguire i movimenti effettivi, rilancia con il flag: --execute")
    else:
        print("\n✅ File spostati con successo in Auto.org. Registro aggiornato in TRIAGE_LOG.md.")


def main():
    parser = argparse.ArgumentParser(
        description="Auto.org triage tool: safely reorganize Desktop & Downloads files."
    )
    parser.add_argument(
        "--source",
        action="append",
        help="Source directory to scan (default: ~/Desktop and ~/Downloads)"
    )
    parser.add_argument(
        "--dest",
        default=os.path.expanduser("~/Auto.org"),
        help="Destination root directory (default: ~/Auto.org)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually move files. Default is dry-run mode."
    )
    parser.add_argument(
        "--days-stale",
        type=int,
        default=90,
        help="Days of inactivity after which files are staged into vecchiume (default: 90)"
    )
    parser.add_argument(
        "--days-installer",
        type=int,
        default=14,
        help="Days after which installers (.dmg, .pkg, etc.) go to vecchiume (default: 14)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of files to process per run"
    )
    parser.add_argument(
        "--obsidian-vault",
        default=os.path.expanduser("~/Documents/PBTPersonalSync"),
        help="Path to Obsidian vault to mirror logs (default: ~/Documents/PBTPersonalSync if exists)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON format"
    )

    args = parser.parse_args()

    default_sources = [
        Path(os.path.expanduser("~/Desktop")),
        Path(os.path.expanduser("~/Downloads"))
    ]
    sources = [Path(os.path.expanduser(s)) for s in args.source] if args.source else default_sources
    dest_base = Path(os.path.expanduser(args.dest))
    obsidian_vault = Path(os.path.expanduser(args.obsidian_vault)) if args.obsidian_vault else None

    dry_run = not args.execute
    triage_data = plan_and_triage(
        sources=sources,
        dest_base=dest_base,
        dry_run=dry_run,
        days_stale=args.days_stale,
        days_installer=args.days_installer,
        limit=args.limit
    )

    write_triage_log(dest_base, triage_data, obsidian_vault=obsidian_vault)

    if args.json:
        print(json.dumps(triage_data, indent=2))
    else:
        print_summary(triage_data)


if __name__ == "__main__":
    main()
