#!/usr/bin/env python3
"""
bike_weather.py - Zurich Hourly Cycling Weather, Lake Temperature & "Zona T-Shirt" Forecaster
Fetches verified hourly weather data for Zurich (lat: 47.3769, lon: 8.5417)
via Open-Meteo high-resolution model and computes bike clothing tiers:
  - < 13°C: 🥶 Troppo freddo per pedalata leggera
  - 13°C - 19.9°C: 🧥 Maglione lungo / Giacca antivento
  - >= 20°C: 👕 ZONA T-SHIRT (Colnago ready)
Also queries Stadt Zürich Open Data (WSP Mythenquai/Tiefenbrunnen via tecdottir / Range CSV) for live Lake Zurich water temp.
"""

import argparse
import csv
import json
import ssl
import sys
import urllib.request
from datetime import datetime, timedelta

# Create SSL context tolerant of macOS missing certifi bundle
ssl_ctx = ssl.create_default_context()
try:
    ssl_ctx.check_hostname = True
except Exception:
    pass
unverified_ctx = ssl._create_unverified_context() if hasattr(ssl, "_create_unverified_context") else None

def safe_urlopen(req, timeout=10):
    try:
        return urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx)
    except Exception:
        if unverified_ctx:
            return urllib.request.urlopen(req, timeout=timeout, context=unverified_ctx)
        raise

LAT_ZURICH = 47.3769
LON_ZURICH = 8.5417

def get_zurich_weather(forecast_days=2):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT_ZURICH}&longitude={LON_ZURICH}"
        f"&hourly=temperature_2m,apparent_temperature,precipitation_probability,precipitation,windspeed_10m"
        f"&timezone=Europe%2FZurich&forecast_days={forecast_days}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "ZurichBikeWeather/1.0"})
    with safe_urlopen(req) as resp:
        return json.loads(resp.read().decode())

def get_lake_temperature(station="mythenquai"):
    """
    Fetches real-time lake water temperature from Stadt Zürich Open Data (WSP)
    via tecdottir API, HTTP Range request on CSV, or Stadt Zürich Bath XML feed.
    """
    # 1. Primary: tecdottir API (live JSON proxy for Stadt Zürich WSP stations)
    try:
        base_url = f"https://tecdottir.herokuapp.com/measurements/{station}"
        req_meta = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})
        with safe_urlopen(req_meta, timeout=5) as resp:
            meta = json.loads(resp.read().decode())
            total = meta.get("total_count", 0)
        if total > 0:
            req_latest = urllib.request.Request(f"{base_url}?offset={total - 1}", headers={"User-Agent": "Mozilla/5.0"})
            with safe_urlopen(req_latest, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                res = data.get("result", [])
                if res:
                    latest = res[-1]
                    vals = latest.get("values", {})
                    water_t = vals.get("water_temperature", {}).get("value")
                    ts = latest.get("timestamp")
                    if water_t is not None:
                        return {"station": station, "water_temp_c": float(water_t), "timestamp": ts}
    except Exception:
        pass

    # 2. HTTP Range request on Open Data CSV
    url = f"https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen/download/messwerte_{station}_seit2007-heute.csv"
    req = urllib.request.Request(url, headers={"Range": "bytes=-2000", "User-Agent": "curl/7.88.1"})
    try:
        with safe_urlopen(req, timeout=5) as resp:
            lines = resp.read().decode("utf-8", errors="ignore").strip().splitlines()
            for line in reversed(lines):
                parts = line.split(",")
                if len(parts) >= 4 and parts[3]:
                    try:
                        water_t = float(parts[3])
                        ts = parts[1]
                        return {"station": station, "water_temp_c": water_t, "timestamp": ts}
                    except ValueError:
                        continue
    except Exception:
        pass

    # 3. Fallback to Stadt Zürich live baths XML feed
    try:
        import xml.etree.ElementTree as ET
        bath_url = "https://www.stadt-zuerich.ch/stzh/bathdatadownload"
        req_baths = urllib.request.Request(bath_url, headers={"User-Agent": "Mozilla/5.0"})
        with safe_urlopen(req_baths, timeout=5) as resp:
            tree = ET.fromstring(resp.read())
            target_names = ["Seebad Utoquai", "Strandbad Mythenquai", "Strandbad Tiefenbrunnen", "Seebad Enge"]
            baths = {b.findtext("title"): b for b in tree.findall(".//bath")}
            for name in target_names:
                b = baths.get(name)
                if b is not None:
                    temp_txt = b.findtext("temperatureWater")
                    ts = b.findtext("dateModified")
                    if temp_txt:
                        return {"station": name, "water_temp_c": float(temp_txt), "timestamp": ts}
    except Exception:
        pass

    # 4. Fallback to wiewarm.ch API (Reliable in off-season/autumn/winter for Tiefenbrunnen & Mythenquai)
    try:
        w_url = "https://wiewarm.ch/api/v1/bad.json"
        req_w = urllib.request.Request(w_url, headers={"User-Agent": "Mozilla/5.0"})
        with safe_urlopen(req_w, timeout=5) as resp:
            bads = json.loads(resp.read().decode())
            for item in bads:
                if str(item.get("badid")) == "14":  # Zürichsee
                    beck = item.get("becken", {})
                    chosen_station = "Tiefenbrunnen" if "tiefenbrunnen" in station.lower() else "Mythenquai"
                    if chosen_station not in beck and beck:
                        chosen_station = next(iter(beck.keys()))
                    if chosen_station in beck:
                        temp_str = beck[chosen_station].get("temp")
                        date_str = beck[chosen_station].get("date")
                        if temp_str:
                            return {"station": f"Zürichsee ({chosen_station})", "water_temp_c": float(temp_str), "timestamp": date_str}
    except Exception:
        pass

    # 5. Direct Tecson live station HTML (Wasserschutzpolizei origin telemetry)
    try:
        import re
        station_slug = "tiefenbrunnen" if "tiefenbrunnen" in station.lower() else "mythenquai"
        t_url = f"https://www.tecson-data.ch/zurich/{station_slug}/index.php"
        req_t = urllib.request.Request(t_url, headers={"User-Agent": "Mozilla/5.0"})
        with safe_urlopen(req_t, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            idx = html.find("Wassertemperatur</span></a>")
            if idx != -1:
                chunk = html[idx:idx + 1200]
                m = re.search(r'>\s*([0-9]+(?:[\.,][0-9]+)?)\s*(&nbsp;)?\s*C\s*<', chunk)
                if m:
                    temp_val = float(m.group(1).replace(",", "."))
                    return {"station": f"Zürichsee ({station_slug.capitalize()})", "water_temp_c": temp_val, "timestamp": "live (tecson)"}
    except Exception:
        pass

    # 6. Eawag Alplakes API (Swiss Federal Institute of Aquatic Science and Technology - Delft3D 3D Simulation & Forecast)
    try:
        now_utc = datetime.utcnow()
        t_start = (now_utc - timedelta(hours=3)).strftime("%Y%m%d%H00")
        t_end = (now_utc + timedelta(hours=3)).strftime("%Y%m%d%H00")
        alp_url = f"https://alplakes-api.eawag.ch/simulations/point/delft3d-flow/zurich/{t_start}/{t_end}/0.5/47.345/8.545"
        req_alp = urllib.request.Request(alp_url, headers={"User-Agent": "Mozilla/5.0"})
        with safe_urlopen(req_alp, timeout=5) as resp:
            alp_data = json.loads(resp.read().decode())
            temps = alp_data.get("variables", {}).get("temperature", {}).get("data", [])
            times = alp_data.get("time", [])
            if temps:
                latest_t = float(temps[-1])
                latest_ts = times[-1] if times else now_utc.isoformat()
                return {"station": "Zürichsee (Eawag Alplakes)", "water_temp_c": round(latest_t, 1), "timestamp": latest_ts}
    except Exception:
        pass

    return None

def classify_tier(temp, rain_prob, wind_kmh):
    if rain_prob > 30:
        return "🌧️ Rischio Pioggia"
    if temp >= 20.0:
        return "👕 ZONA T-SHIRT"
    elif temp >= 13.0:
        return "🧥 Maglione / Maniche lunghe"
    else:
        return "🥶 Troppo freddo"

def main():
    parser = argparse.ArgumentParser(description="Zurich Bike & Lake Weather Forecaster")
    parser.add_argument("--format", choices=["table", "csv", "json"], default="table")
    parser.add_argument("--day", choices=["today", "tomorrow"], default="today", help="Forecast day (today or tomorrow)")
    parser.add_argument("--afternoon-only", action="store_true", help="Show only 12:00 to 20:00")
    parser.add_argument("--lake", action="store_true", default=True, help="Include Zürichsee water temperature")
    args = parser.parse_args()

    data = get_zurich_weather(forecast_days=2)
    hourly = data["hourly"]
    times = hourly["time"]
    temps = hourly["temperature_2m"]
    apparents = hourly["apparent_temperature"]
    precips = hourly["precipitation_probability"]
    winds = hourly["windspeed_10m"]

    # Determine target date string YYYY-MM-DD
    target_dt = datetime.now()
    if args.day == "tomorrow":
        target_dt += timedelta(days=1)
    target_date_str = target_dt.strftime("%Y-%m-%d")

    rows = []
    for t, temp, app, p, w in zip(times, temps, apparents, precips, winds):
        date_str, time_str = t.split("T")
        if date_str != target_date_str:
            continue
        hour_str = time_str[:5]
        hour_num = int(hour_str.split(":")[0])
        if args.afternoon_only and not (12 <= hour_num <= 20):
            continue
        tier = classify_tier(temp, p, w)
        rows.append({
            "data": date_str,
            "ora": hour_str,
            "temp_c": temp,
            "temp_percepita_c": app,
            "pioggia_pct": p,
            "vento_kmh": w,
            "comfort_bici": tier
        })

    lake_info = get_lake_temperature("mythenquai") if args.lake else None

    if args.format == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=["data", "ora", "temp_c", "temp_percepita_c", "pioggia_pct", "vento_kmh", "comfort_bici"])
        writer.writeheader()
        writer.writerows(rows)
    elif args.format == "json":
        res = {"date": target_date_str, "hourly": rows, "lake": lake_info}
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        if lake_info:
            print(f"🌊 Zürichsee ({lake_info['station'].capitalize()}): {lake_info['water_temp_c']}°C (aggiornato al {lake_info['timestamp']})\n")
        print(f"Data: {target_date_str}")
        print(f"{'Ora':<7} | {'Temp (°C)':<9} | {'Percepita':<9} | {'Pioggia':<7} | {'Vento':<10} | {'Abbigliamento Consigliato'}")
        print("-" * 75)
        for r in rows:
            print(f"{r['ora']:<7} | {r['temp_c']:<9.1f} | {r['temp_percepita_c']:<9.1f} | {r['pioggia_pct']}%{'':<4} | {r['vento_kmh']:<6.1f}km/h | {r['comfort_bici']}")

if __name__ == "__main__":
    main()
