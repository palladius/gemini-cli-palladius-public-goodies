#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
import sys
import os
import re
import xml.etree.ElementTree as ET
import urllib.request
import json
import argparse
import time
from datetime import datetime

CACHE_DIR = os.path.expanduser("~/.cache/zurich-badi-info")
CACHE_TTL = 600  # 10 minuti

FAVORITES = {
    "utoquai": {
        "name": "Seebad Utoquai",
        "keywords": ["utoquai"],
        "desc": "Nuotata Ironman mattutina (7:00 AM, 1.5 km)",
        "emoji": "🏞️"
    },
    "heuried": {
        "name": "Freibad Heuried",
        "keywords": ["heuried"],
        "desc": "Piscina famiglia (consigliata nel tardo pomeriggio se temperatura > 25°C)",
        "emoji": "🏊"
    },
    "mythenquai": {
        "name": "Strandbad Mythenquai",
        "keywords": ["mythenquai"],
        "desc": "Spiaggia lago per famiglie (tardo pomeriggio o weekend)",
        "emoji": "🏞️"
    },
    "tiefenbrunnen": {
        "name": "Strandbad Tiefenbrunnen",
        "keywords": ["tiefenbrunnen"],
        "desc": "Spiaggia lago per famiglie (tardo pomeriggio o weekend)",
        "emoji": "🏞️"
    }
}

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def get_cached_data(filename):
    filepath = os.path.join(CACHE_DIR, filename)
    if os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
        if time.time() - mtime < CACHE_TTL:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
    return None

def set_cached_data(filename, content):
    ensure_cache_dir()
    filepath = os.path.join(CACHE_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        sys.stderr.write(f"Warning: Impossibile scrivere la cache per {filename}: {e}\n")

def fetch_url(url, cache_filename=None, force=False, is_weather=False):
    if not force and cache_filename:
        cached = get_cached_data(cache_filename)
        if cached:
            return cached

    try:
        ua = "curl/7.64.1" if is_weather else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) zurich-badi-info/1.0"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": ua}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            if cache_filename:
                set_cached_data(cache_filename, content)
            return content
    except Exception as e:
        sys.stderr.write(f"Errore nel caricamento dell'URL {url}: {e}\n")
        if cache_filename:
            filepath = os.path.join(CACHE_DIR, cache_filename)
            if os.path.exists(filepath):
                sys.stderr.write("Utilizzo dei dati in cache scaduti come fallback.\n")
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        return None

def get_badi_data(force=False):
    xml_content = fetch_url("https://www.stadt-zuerich.ch/stzh/bathdatadownload", "baths.xml", force)
    if not xml_content:
        return []

    try:
        root = ET.fromstring(xml_content)
        baths = []
        for bath in root.findall(".//bath"):
            title = bath.find("title").text if bath.find("title") is not None else None
            temp = bath.find("temperatureWater").text if bath.find("temperatureWater") is not None else None
            status = bath.find("openClosedTextPlain").text if bath.find("openClosedTextPlain") is not None else None
            date_mod = bath.find("dateModified").text if bath.find("dateModified") is not None else None
            url = bath.find("urlPage").text if bath.find("urlPage") is not None else None
            
            title_str = title.strip() if title else "Badi Sconosciuta"
            temp_str = temp.strip() if temp else "N/D"
            status_str = status.strip() if status else "N/D"
            date_mod_str = date_mod.strip() if date_mod else "N/D"
            url_str = url.strip() if url else ""
            
            baths.append({
                "title": title_str,
                "temperature": temp_str,
                "status": status_str,
                "date_modified": date_mod_str,
                "url": url_str
            })
        return baths
    except Exception as e:
        sys.stderr.write(f"Errore nel parsing dell'XML delle Badi: {e}\n")
        return []

def get_limmat_data(force=False):
    url = "https://api.existenz.ch/apiv1/hydro/latest?locations=2099&app=zurich-badi-info"
    json_content = fetch_url(url, "limmat_data.json", force)
    if not json_content:
        return None, None
    try:
        data = json.loads(json_content)
        payload = data.get("payload", [])
        flow = None
        height = None
        for item in payload:
            if item.get("par") == "flow":
                flow = item.get("val")
            elif item.get("par") == "height":
                height = item.get("val")
        return flow, height
    except Exception as e:
        sys.stderr.write(f"Errore nel parsing del JSON della Limmat: {e}\n")
    return None, None

def get_outside_temperature(force=False):
    text_content = fetch_url("https://wttr.in/Zurich?format=%t", "weather.txt", force, is_weather=True)
    if not text_content:
        return None
    text_content = re.sub(r'<[^>]*>', '', text_content).strip()
    match = re.search(r'([+-]?\d+)', text_content)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return None

def determine_type(badi):
    title = badi["title"].lower()
    url = badi["url"].lower()
    if "flussbad" in title or "letten" in title or "limmat" in title or "au-hoengg" in url:
        return "Fiume"
    elif "seebad" in title or "strandbad" in title or "utoquai" in title or "mythenquai" in title or "tiefenbrunnen" in title:
        return "Lago"
    else:
        return "Piscina"

def print_table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(str(cell)))
    
    header_str = " | ".join(f"{str(cell).ljust(widths[idx])}" for idx, cell in enumerate(headers))
    print(header_str)
    print("-+-".join("-" * w for w in widths))
    
    for row in rows:
        row_str = " | ".join(f"{str(cell).ljust(widths[idx])}" for idx, cell in enumerate(row))
        print(row_str)

def get_favorites_statuses(baths):
    fav_statuses = {}
    for fav_id, fav_info in FAVORITES.items():
        matched_bath = None
        for bath in baths:
            if any(kw in bath["title"].lower() for kw in fav_info["keywords"]):
                matched_bath = bath
                break
        
        if matched_bath:
            fav_statuses[fav_id] = {
                "title": matched_bath["title"],
                "temperature": matched_bath["temperature"],
                "status": matched_bath["status"],
                "date_modified": matched_bath["date_modified"],
                "url": matched_bath["url"],
                "desc": fav_info["desc"],
                "emoji": fav_info.get("emoji", "🏖️")
            }
        else:
            fav_statuses[fav_id] = {
                "title": fav_info["name"],
                "temperature": "N/D",
                "status": "Sconosciuto",
                "date_modified": "N/D",
                "url": "",
                "desc": fav_info["desc"],
                "emoji": fav_info.get("emoji", "🏖️")
            }
    return fav_statuses

def get_temp_emoji(temp_str):
    if not temp_str or temp_str == "N/D" or temp_str == "N/A":
        return "⚪"
    try:
        val = float(temp_str)
        if val < 18:
            return "🔴"
        elif 18 <= val <= 19:
            return "🟠"
        elif 20 <= val <= 24:
            return "🟡"
        else:  # 25+
            return "🟢"
    except ValueError:
        return "⚪"

def log_to_csv(baths, out_temp, flow, height, csv_path=None):
    if csv_path is None:
        default_obsidian = os.path.expanduser("~/obsidian-pbt")
        if os.path.isdir(default_obsidian):
            csv_path = os.path.join(default_obsidian, "zurich_badi_history.csv")
        else:
            csv_path = os.path.join(CACHE_DIR, "zurich_badi_history.csv")
            
    headers = [
        "Timestamp", "Temp Esterna (C)", 
        "Utoquai Temp (C)", "Utoquai Stato",
        "Heuried Temp (C)", "Heuried Stato",
        "Mythenquai Temp (C)", "Mythenquai Stato",
        "Tiefenbrunnen Temp (C)", "Tiefenbrunnen Stato",
        "Letten Temp (C)", "Limmat Flusso (m3/s)", "Limmat Altezza (m ü. M.)", "Limmat Delta (cm)"
    ]
    
    favs = get_favorites_statuses(baths)
    letten_temp = "N/D"
    for bath in baths:
        if "oberer letten" in bath["title"].lower():
            letten_temp = bath["temperature"]
            break
            
    delta_cm = ""
    if height is not None:
        delta_cm = f"{(height - 399.80) * 100:.0f}"
        
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        str(out_temp) if out_temp is not None else "N/D",
        favs["utoquai"]["temperature"],
        translate_status(favs["utoquai"]["status"]),
        favs["heuried"]["temperature"],
        translate_status(favs["heuried"]["status"]),
        favs["mythenquai"]["temperature"],
        translate_status(favs["mythenquai"]["status"]),
        favs["tiefenbrunnen"]["temperature"],
        translate_status(favs["tiefenbrunnen"]["status"]),
        letten_temp,
        str(flow) if flow is not None else "N/D",
        f"{height:.2f}" if height is not None else "N/D",
        delta_cm
    ]
    
    file_exists = os.path.exists(csv_path)
    try:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write(",".join(headers) + "\n")
            f.write(",".join(row) + "\n")
        print(f"\n📝 Dati storici salvati automaticamente in: {csv_path}")
    except Exception as e:
        sys.stderr.write(f"Errore nella scrittura del file CSV: {e}\n")

def translate_status(status_str):
    if not status_str:
        return "Sconosciuto"
    status_lower = status_str.lower()
    if status_lower == "offen" or status_lower == "open" or status_lower == "aperto":
        return "Aperto"
    elif status_lower == "geschlossen" or status_lower == "closed" or status_lower == "chiuso":
        return "Chiuso"
    return status_str

def cmd_summary(args):
    baths = get_badi_data(args.no_cache)
    flow, height = get_limmat_data(args.no_cache)
    out_temp = get_outside_temperature(args.no_cache)
    
    print("🇨🇭 ================= REPORT BADI & TEMPERATURE ACQUA ZURIGO ================= 🇨🇭")
    if out_temp is not None:
        print(f"🌡️  Temperatura Esterna Attuale: {out_temp}°C")
    else:
        print("🌡️  Temperatura Esterna Attuale: Sconosciuta")
        
    print("\n⭐ LE TUE BADI PREFERITE:")
    favs = get_favorites_statuses(baths)
    for fav_id, fav in favs.items():
        temp_str = f"{fav['temperature']}°C" if fav['temperature'] != "N/D" else "N/D"
        temp_emoji = get_temp_emoji(fav['temperature'])
        status_symbol = "🟢" if fav['status'].lower() in ["offen", "open", "aperto"] else "🔴" if fav['status'].lower() in ["geschlossen", "closed", "chiuso"] else "⚪"
        translated_stat = translate_status(fav['status'])
        print(f"  {status_symbol}  {fav['emoji']}  {fav['title'].ljust(25)} | Temp: {temp_str.rjust(6)} {temp_emoji} | Stato: {translated_stat}")
        
        # Recommendations
        if fav_id == "utoquai":
            print(f"      ↳ 🏊‍♂️ Allenamento Ironman: {fav['desc']}. Temperatura acqua: {temp_str} {temp_emoji}!")
        elif fav_id == "heuried":
            if out_temp is not None:
                if out_temp >= 25:
                    print(f"      ↳ 👨‍👩‍👧‍👦 Consiglio Piscina Famiglia: 🟢 SI VÀ! Fuori ci sono {out_temp}°C (> 25°C).")
                else:
                    print(f"      ↳ 👨‍👩‍👧‍👦 Consiglio Piscina Famiglia: 🟡 EVITARE? Fuori ci sono {out_temp}°C (sotto i 25°C).")
            else:
                print(f"      ↳ 👨‍👩‍👧‍👦 Piscina Famiglia: {fav['desc']}.")
        elif fav_id in ["mythenquai", "tiefenbrunnen"]:
            now = datetime.now()
            is_weekend = now.weekday() >= 5
            if is_weekend:
                print(f"      ↳ 🏖️ Consiglio Lago Famiglia: 🟢 Il weekend è il momento perfetto per andare a {fav['title']}!")
            else:
                print(f"      ↳ 🏖️ Lago Famiglia: {fav['desc']}.")

    # Geographic / Microclimate Note
    print("\n💡 CONSIGLIO MICROCLIMA LAGO DI ZURIGO:")
    print("  - La sponda OVEST (Seebad Enge / Strandbad Mythenquai) è solitamente più calda")
    print("    di 1-2°C rispetto alla sponda EST (Seebad Utoquai / Strandbad Tiefenbrunnen)")
    print("    a causa dei venti locali e delle correnti! (Anche se la sponda EST è sempre la migliore! 😜)")
    print("  - Le piscine isolate dal lago (come Freibad Heuried) hanno un ciclo termico differente,")
    print("    guidato fortemente dall'irradiazione solare e dalla temperatura dell'aria anziché")
    print("    dall'inerzia termica del lago, scaldandosi e raffreddandosi molto più rapidamente!")

    # Calculate Delta T Warnings
    west_temps = []
    east_temps = []
    river_temp = None
    
    for bath in baths:
        title_lower = bath["title"].lower()
        try:
            temp_val = float(bath["temperature"])
        except ValueError:
            continue
            
        if "seebad enge" in title_lower or "mythenquai" in title_lower:
            west_temps.append(temp_val)
        elif "utoquai" in title_lower or "tiefenbrunnen" in title_lower:
            east_temps.append(temp_val)
        elif "oberer letten" in title_lower:
            river_temp = temp_val
            
    west_avg = sum(west_temps) / len(west_temps) if west_temps else None
    east_avg = sum(east_temps) / len(east_temps) if east_temps else None
    lake_avg = sum(west_temps + east_temps) / len(west_temps + east_temps) if (west_temps + east_temps) else None
    
    warnings = []
    if west_avg is not None and east_avg is not None:
        actual_we_delta = west_avg - east_avg
        if actual_we_delta > 1.0:
            warnings.append(
                f"⚠️ ATTENZIONE: La sponda Ovest è insolitamente calda! Delta T: {actual_we_delta:.1f}°C (delta previsto Ovest-Est: 1.0°C)."
            )
            
    if lake_avg is not None and river_temp is not None:
        actual_lr_delta = lake_avg - river_temp
        if actual_lr_delta > 2.0:
            warnings.append(
                f"⚠️ ATTENZIONE: La Limmat è insolitamente fredda! Il fiume è più freddo del lago di {actual_lr_delta:.1f}°C (delta previsto Lago-Fiume: 2.0°C)."
            )
            
    if warnings:
        print("\n🚨 ALLERTA DELTA TEMPERATURE:")
        for w in warnings:
            print(f"  {w}")

    # River / Canotto Check
    print("\n🛶 REPORT DISCESA IN CANOTTO SULLA LIMMAT:")
    letten_temp_str = "N/D"
    letten_temp_val = None
    for bath in baths:
        if "oberer letten" in bath["title"].lower():
            letten_temp_str = f"{bath['temperature']}°C"
            letten_temp_val = bath["temperature"]
            break
    letten_emoji = get_temp_emoji(letten_temp_val)
    print(f"  🌊 Temperatura Fiume (Oberer Letten): {letten_temp_str} {letten_emoji}")
    
    if flow is not None:
        print(f"  📊 Portata della Corrente (Flusso):  {flow} m³/s (BAFU Zürich-Unterhard)")
        if height is not None:
            delta_cm = (height - 399.80) * 100
            delta_sign = "+" if delta_cm >= 0 else ""
            delta_text = f"{delta_sign}{delta_cm:.0f} cm rispetto al riferimento di 399.80m"
            print(f"  📏 Livello Altezza Acqua (Pegel):     {height:.2f} m ü. M. ({delta_text})")
            if delta_cm < 0:
                print(f"  🪨  ALLERTA LIVELLO BASSO:           ⚠️ SECCA! Il livello è di {delta_cm:.0f} cm sotto il riferimento.")
                print(f"      ↳ Alto rischio di urtare le pietre con il canotto! Indossare calzature adatte (es. Crocs).")
            elif delta_cm < 5:
                print(f"  🪨  STATO ACQUA:                     🟡 Basso fondale ({delta_cm:+.0f} cm). Navigare con prudenza!")
            else:
                print(f"  📏 STATO ACQUA:                     🟢 Altezza ottimale ({delta_cm:+.0f} cm). Margine sicuro sopra i sassi.")
                
        now = datetime.now()
        is_weekend = now.weekday() >= 5
        
        if flow > 100:
            print("  🚨 VALUTAZIONE CANOTTO:               🔴 ALLERTA PERICOLO ROSSO!")
            print(f"      ↳ La corrente è troppo forte ({flow} m³/s > 100 m³/s). Estremamente pericoloso. Non scendere in acqua!")
        else:
            if is_weekend:
                print("  🚨 VALUTAZIONE CANOTTO:               🟢 VIA LIBERA!")
                print(f"      ↳ La corrente è sicura ({flow} m³/s <= 100 m³/s) ed è weekend! Buon divertimento in canotto! 🛶")
            else:
                print("  🚨 VALUTAZIONE CANOTTO:               🟡 SICURO MA INFRASETTIMANALE")
                print(f"      ↳ La corrente è sicura ({flow} m³/s <= 100 m³/s). Tienilo a mente per il weekend!")
    else:
        print("  📊 Portata della Corrente (Flusso):  Sconosciuta (dati BAFU non disponibili)")

    open_count = sum(1 for b in baths if b["status"].lower() == "offen")
    print(f"\nℹ️  Badi Totali: {len(baths)} | Attualmente Aperte: {open_count}")
    
    # Registra i dati storici in CSV
    log_to_csv(baths, out_temp, flow, height, args.csv)

def cmd_list(args):
    baths = get_badi_data(args.no_cache)
    if not baths:
        print("Nessun dato trovato per le Badi.")
        return

    filtered = []
    for b in baths:
        b_type = determine_type(b)
        if args.type != "all" and b_type.lower() != args.type.lower():
            continue
        if args.open and b["status"].lower() != "offen":
            continue
        filtered.append(b)

    headers = ["Nome", "Tipo", "Temp Acqua", "Stato", "Ultima Modifica"]
    rows = []
    for b in filtered:
        rows.append([
            b["title"],
            determine_type(b),
            f"{b['temperature']}°C" if b['temperature'] != "N/D" else "N/D",
            translate_status(b["status"]),
            b["date_modified"]
        ])
    print_table(headers, rows)

def cmd_search(args):
    baths = get_badi_data(args.no_cache)
    query = args.query.lower()
    filtered = [b for b in baths if query in b["title"].lower()]
    
    if not filtered:
        print(f"🔍 Nessuna Badi corrisponde a '{args.query}'")
        return
        
    headers = ["Nome", "Tipo", "Temp Acqua", "Stato", "Ultima Modifica", "Link Info"]
    rows = []
    for b in filtered:
        rows.append([
            b["title"],
            determine_type(b),
            f"{b['temperature']}°C" if b['temperature'] != "N/D" else "N/D",
            translate_status(b["status"]),
            b["date_modified"],
            b["url"]
        ])
    print_table(headers, rows)

def main():
    parser = argparse.ArgumentParser(description="Monitor delle Temperature delle Badi e dei Fiumi di Zurigo (Solo Sistema Metrico)")
    parser.add_argument("--no-cache", action="store_true", help="Forza il caricamento dei dati in tempo reale ignorando la cache")
    parser.add_argument("--csv", help="Specifica il percorso di un file CSV per registrare i dati storici (es. in Obsidian)")
    
    subparsers = parser.add_subparsers(dest="command", help="Sotto-comandi")
    
    # summary
    subparsers.add_parser("summary", help="Mostra il report riassuntivo personalizzato per nuoto Ironman, consigli meteo e canotto sulla Limmat")
    
    # list
    list_p = subparsers.add_parser("list", help="Elenca tutte le badi")
    list_p.add_argument("--type", choices=["lake", "river", "pool", "all"], default="all", help="Filtra per tipo di Badi")
    list_p.add_argument("--open", action="store_true", help="Mostra solo le Badi attualmente aperte")
    
    # search
    search_p = subparsers.add_parser("search", help="Cerca una Badi specifica per nome")
    search_p.add_argument("query", help="Termine di ricerca (es. Utoquai)")
    
    args = parser.parse_args()
    if not args.command:
        args.command = "summary"
        
    if args.command == "summary":
        cmd_summary(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "search":
        cmd_search(args)

if __name__ == '__main__':
    main()
