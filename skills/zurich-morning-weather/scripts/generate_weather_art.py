#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
#     "requests>=2.28.0",
# ]
# ///
"""
Zurich Morning Weather Artwork Generator
Fetches live Zurich weather conditions + Lake Zurich (Zürichsee) water temperature
and generates an isometric 3D miniature cartoon diorama of Zurich with integrated
weather and top-centered typography using Gemini 3 Pro Image (Nano Banana Pro).
Supports vertical 3:4 portrait and deterministic lake temperature overlay.
"""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import sys
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont

WMO_WEATHER_MAP = {
    0: {
        "condition": "crisp clear sunny skies",
        "condition_it": "sole splendente e cielo terso",
        "atmosphere": "bright golden morning sun, long soft shadows, and crystal-clear visibility towards the distant Alps",
        "icon": "radiant golden 3D sun with soft glowing light beams",
        "umbrella": False,
        "label_it": "☀️ Sole"
    },
    1: {
        "condition": "mainly clear skies with scattered light clouds",
        "condition_it": "prevalentemente sereno con qualche velatura",
        "atmosphere": "soft warm morning sunlight with a few small fluffy white clouds drifting overhead",
        "icon": "golden 3D sun peeking out from behind a small fluffy white cloud",
        "umbrella": False,
        "label_it": "🌤️ Quasi sereno"
    },
    2: {
        "condition": "partly cloudy weather",
        "condition_it": "parzialmente nuvoloso",
        "atmosphere": "gentle golden ambient light, delicate wisps of clouds, and cozy morning atmosphere",
        "icon": "partly cloudy 3D weather icon with a golden sun emerging from behind soft puffy white clouds",
        "umbrella": False,
        "label_it": "⛅ Parzialmente nuvoloso"
    },
    3: {
        "condition": "overcast atmospheric cloudy skies",
        "condition_it": "coperto con nuvole diffuse",
        "atmosphere": "soft, diffused ambient lighting casting gentle, smooth shadows across the city",
        "icon": "soft, puffy layered 3D grey and white clouds",
        "umbrella": False,
        "label_it": "☁️ Coperto"
    },
    45: {
        "condition": "morning autumn fog and mist",
        "condition_it": "nebbia e foschia mattutina",
        "atmosphere": "delicate low-lying mist floating above the Limmat river and lake, with church spires rising gracefully through the haze",
        "icon": "stylized 3D cloud with horizontal mist and fog lines",
        "umbrella": False,
        "label_it": "🌫️ Nebbia"
    },
    48: {
        "condition": "frosty rime fog",
        "condition_it": "nebbia con galaverna / brina",
        "atmosphere": "frost-dusted rooftops and trees with cool ethereal morning mist",
        "icon": "cool 3D winter cloud with glistening frost crystals",
        "umbrella": False,
        "label_it": "❄️ Brina e nebbia"
    },
    51: {
        "condition": "light gentle drizzle",
        "condition_it": "pioggerellina leggera",
        "atmosphere": "glistening wet cobblestones with reflections of streetlights and church towers, and tiny micro-raindrops",
        "icon": "soft 3D cloud with tiny delicate blue raindrops and a small open umbrella icon",
        "umbrella": True,
        "label_it": "🌦️ Pioggerellina"
    },
    53: {
        "condition": "moderate drizzle",
        "condition_it": "pioggia fine intermittente",
        "atmosphere": "wet reflective streets, delicate drizzle drops, and soft grey clouds",
        "icon": "3D cloud with light blue rain streaks and a red umbrella icon",
        "umbrella": True,
        "label_it": "🌧️ Pioggia fine"
    },
    55: {
        "condition": "dense drizzle",
        "condition_it": "pioggia fine fitta",
        "atmosphere": "dense drizzle coating roofs and bridges in mist",
        "icon": "dense 3D rain cloud with falling drops and an umbrella icon",
        "umbrella": True,
        "label_it": "🌧️ Pioggerella fitta"
    },
    61: {
        "condition": "gentle rain",
        "condition_it": "pioggia debole / moderata",
        "atmosphere": "wet reflective streets, subtle ripple rings across the surface of the Limmat river, and moody atmospheric clouds",
        "icon": "3D rain cloud with neat parallel falling rain streaks and a cute 3D umbrella",
        "umbrella": True,
        "label_it": "🌧️ Pioggia"
    },
    63: {
        "condition": "moderate rain",
        "condition_it": "pioggia battente",
        "atmosphere": "glossy wet cobblestone reflections, cozy indoor glows in city windows, and rhythmic rain ripples on the lake",
        "icon": "darker 3D rain cloud with bold falling raindrops and a 3D umbrella",
        "umbrella": True,
        "label_it": "🌧️ Pioggia battente"
    },
    65: {
        "condition": "heavy rain",
        "condition_it": "pioggia forte",
        "atmosphere": "heavy rain splashing on cobblestones, dramatic rainy sky, warm glowing windows",
        "icon": "heavy dark 3D rain cloud with dense falling rain and an umbrella",
        "umbrella": True,
        "label_it": "⛈️ Pioggia forte"
    },
    71: {
        "condition": "light winter snowfall",
        "condition_it": "nevicata leggera",
        "atmosphere": "fresh white snow gently coating church roofs, bridges, and trees, with soft floating snowflakes in the air",
        "icon": "3D cloud with delicate white snowflakes falling",
        "umbrella": True,
        "label_it": "🌨️ Nevicata leggera"
    },
    73: {
        "condition": "winter snow",
        "condition_it": "neve moderata",
        "atmosphere": "picturesque winter wonderland with snowy rooftops, a snow-dusted tram, and frosty riverbanks",
        "icon": "3D snow cloud with intricate crystalline snowflakes",
        "umbrella": True,
        "label_it": "❄️ Neve"
    },
    75: {
        "condition": "heavy winter snowfall",
        "condition_it": "forte nevicata",
        "atmosphere": "thick blanket of snow over Grossmünster and Limmat, swirling snowflakes",
        "icon": "heavy 3D snow cloud with sparkling snowflakes",
        "umbrella": True,
        "label_it": "❄️ Forte nevicata"
    },
    80: {
        "condition": "scattered rain showers",
        "condition_it": "rovesci sparsi",
        "atmosphere": "intermittent rain showers alternating with dramatic cloud breaks and wet cobblestones",
        "icon": "3D cloud with rain showers and a small sunbeam",
        "umbrella": True,
        "label_it": "🌦️ Rovesci sparsi"
    },
    81: {
        "condition": "moderate rain showers",
        "condition_it": "rovesci di pioggia",
        "atmosphere": "frequent wet rain showers over the city and ripples on the Limmat",
        "icon": "3D cloud with angled rain streaks",
        "umbrella": True,
        "label_it": "🌧️ Rovesci di pioggia"
    },
    82: {
        "condition": "heavy rain showers",
        "condition_it": "acquazzone",
        "atmosphere": "heavy sudden shower soaking the city streets",
        "icon": "dark 3D storm cloud with heavy rain",
        "umbrella": True,
        "label_it": "⛈️ Acquazzone"
    },
    95: {
        "condition": "dramatic thunderstorm",
        "condition_it": "temporale",
        "atmosphere": "deep moody skies with dramatic contrast and soft warm glows from shop windows",
        "icon": "3D dark cloud with a bright golden lightning bolt",
        "umbrella": True,
        "label_it": "⚡ Temporale"
    }
}

def get_api_key(provided_key: str | None) -> str | None:
    key = provided_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        m = re.search(r'(AIzaSy[A-Za-z0-9_-]+)', key)
        if m:
            return m.group(1)
        return key.strip()
    env_file = Path.home() / ".hermes" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                    m = re.search(r'(AIzaSy[A-Za-z0-9_-]+)', line)
                    if m:
                        return m.group(1)
    return None

def geocode_city(city_name: str) -> dict:
    raw = city_name.strip()
    if raw.lower() in ("zurich", "zürich", "zurigo"):
        return {
            "name": "Zurich",
            "lat": 47.3769,
            "lon": 8.5417,
            "timezone": "Europe/Zurich",
            "country": "Switzerland",
            "admin": "",
            "is_zurich": True,
        }
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    search_term = parts[0] if parts else raw
    hint = " ".join(parts[1:]).lower() if len(parts) > 1 else ""

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(search_term)}&count=10&language=en&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ZurichWeatherSkill/1.2"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
            results = data.get("results", [])
            if results:
                chosen = results[0]
                if hint:
                    for cand in results:
                        blob = " ".join(
                            str(cand.get(k, ""))
                            for k in ("admin1", "admin2", "admin3", "country", "country_code")
                        ).lower()
                        if hint in blob or any(tok in blob for tok in hint.split()):
                            chosen = cand
                            break
                return {
                    "name": chosen.get("name", search_term),
                    "lat": float(chosen["latitude"]),
                    "lon": float(chosen["longitude"]),
                    "timezone": chosen.get("timezone", "Europe/Zurich"),
                    "country": chosen.get("country", ""),
                    "admin": chosen.get("admin2") or chosen.get("admin1") or "",
                    "is_zurich": False,
                }
    except Exception as e:
        print(f"Warning: Geocoding failed for {city_name} ({e})", file=sys.stderr)
    return {
        "name": search_term,
        "lat": 44.66,
        "lon": 12.24,
        "timezone": "Europe/Rome",
        "country": "Italy",
        "admin": "",
        "is_zurich": False,
    }

def fetch_air_weather(lat: float = 47.3769, lon: float = 8.5417, tz: str = "Europe/Zurich") -> dict:
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,weather_code,precipitation"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset"
        f"&timezone={urllib.parse.quote(tz)}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ZurichWeatherSkill/1.2"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            current_temp = round(data["current"]["temperature_2m"])
            current_code = data["current"]["weather_code"]
            daily_code = data["daily"]["weather_code"][0]
            code = daily_code if daily_code in (51, 53, 55, 61, 63, 65, 71, 73, 75, 80, 81, 82, 95) else current_code
            precip = data["current"].get("precipitation", 0.0) or 0.0
            min_temp = round(data["daily"]["temperature_2m_min"][0])
            max_temp = round(data["daily"]["temperature_2m_max"][0])
            daily_precip = data["daily"].get("precipitation_sum", [0.0])[0] or 0.0
            precip_prob = data["daily"].get("precipitation_probability_max", [0])[0] or 0
            sunrise_raw = data["daily"].get("sunrise", ["2026-11-08T07:22"])[0]
            sunset_raw = data["daily"].get("sunset", ["2026-11-08T16:52"])[0]
            sunrise = sunrise_raw.split("T")[-1][:5]
            sunset = sunset_raw.split("T")[-1][:5]

            info = WMO_WEATHER_MAP.get(code, WMO_WEATHER_MAP[2])
            umbrella_needed = info["umbrella"] or precip > 0.1 or daily_precip > 0.5 or precip_prob >= 45
            return {
                "current_temp": current_temp,
                "min_temp": min_temp,
                "max_temp": max_temp,
                "code": code,
                "precip": precip,
                "daily_precip": daily_precip,
                "precip_prob": precip_prob,
                "sunrise": sunrise,
                "sunset": sunset,
                "condition": info["condition"],
                "condition_it": info["condition_it"],
                "atmosphere": info["atmosphere"],
                "icon": info["icon"],
                "label_it": info["label_it"],
                "umbrella": umbrella_needed,
            }
    except Exception as e:
        print(f"Warning: Could not fetch Open-Meteo weather ({e}), using seasonal defaults.", file=sys.stderr)
        return {
            "current_temp": 7,
            "min_temp": 5,
            "max_temp": 11,
            "code": 2,
            "precip": 0.0,
            "daily_precip": 0.0,
            "precip_prob": 10,
            "sunrise": "07:22",
            "sunset": "16:52",
            "condition": "partly cloudy autumn weather",
            "condition_it": "parzialmente nuvoloso",
            "atmosphere": "gentle golden ambient light, delicate wisps of clouds, and cozy morning atmosphere",
            "icon": "partly cloudy 3D weather icon with a golden sun emerging from behind soft puffy white clouds",
            "label_it": "⛅ Parzialmente nuvoloso",
            "umbrella": False,
        }

def fetch_zurich_air_weather() -> dict:
    return fetch_air_weather(47.3769, 8.5417, "Europe/Zurich")

def fetch_zuerichsee_water_temp() -> float:
    # 1. Fast JSON API from wiewarm.ch (Zürichsee ID=14)
    try:
        req = urllib.request.Request(
            "https://www.wiewarm.ch/api/v1/bad/14",
            headers={"User-Agent": "ZurichWeatherSkill/1.2"}
        )
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read().decode("utf-8", errors="ignore"))
            rc = data.get("rc", {})
            for b in rc.values() if isinstance(rc, dict) else []:
                if isinstance(b, dict) and b.get("temp"):
                    return float(b["temp"])
    except Exception:
        pass

    # 2. Fallback: Wasserschutzpolizei Mythenquai
    url = "https://www.tecson-data.ch/zurich/mythenquai/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            html = r.read().decode('utf-8', errors='ignore')
        idx = html.find("Wassertemperatur")
        if idx != -1:
            sub = html[idx:idx+1000]
            m = re.search(r'(\d+(?:,\d+)?)&nbsp;C', sub)
            if m:
                return float(m.group(1).replace(',', '.'))
    except Exception as e:
        print(f"Warning: Could not fetch water temperature ({e}), fallback to 12.0°C", file=sys.stderr)
    return 12.0

def fetch_marine_water_temp(lat: float, lon: float) -> float | None:
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=sea_surface_temperature&hourly=sea_surface_temperature"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ZurichWeatherSkill/1.2"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            cur = data.get("current", {}).get("sea_surface_temperature")
            if cur is not None:
                return float(cur)
            hourly = [t for t in data.get("hourly", {}).get("sea_surface_temperature", []) if t is not None]
            if hourly:
                return float(hourly[0])
    except Exception:
        pass
    return None

def detect_travel_city() -> str | None:
    """Detects if Riccardo is currently traveling away from Zurich via ~/.hermes/current_location.txt or Google Calendar."""
    loc_file = Path.home() / ".hermes" / "current_location.txt"
    if loc_file.exists():
        val = loc_file.read_text(encoding="utf-8").strip()
        if val and val.lower() not in ("zurich", "zürich", "zurigo", "none", "home"):
            return val

    import subprocess
    gog_bin = "/opt/homebrew/bin/gog"
    if Path(gog_bin).exists():
        try:
            res = subprocess.run(
                [gog_bin, "calendar", "events", "primary", "--today", "-j"],
                capture_output=True, text=True, timeout=6
            )
            if res.returncode == 0:
                data = json.loads(res.stdout)
                events = data.get("events", [])
                known_places = [
                    ("lido degli estensi", "Lido degli Estensi"),
                    ("comacchio", "Lido degli Estensi"),
                    ("ferrara", "Ferrara"),
                    ("bologna", "Bologna"),
                    ("milano", "Milan"),
                    ("milan", "Milan"),
                    ("roma", "Rome"),
                    ("arbatax", "Arbatax"),
                    ("cala gonone", "Cala Gonone"),
                    ("sardegna", "Arbatax"),
                    ("belo horizonte", "Belo Horizonte"),
                    ("ouro preto", "Ouro Preto"),
                    ("natal", "Natal"),
                    ("noronha", "Fernando de Noronha"),
                    ("floripa", "Florianópolis"),
                    ("florianopolis", "Florianópolis"),
                    ("lugano", "Lugano"),
                    ("stuttgart", "Stuttgart"),
                    ("london", "London"),
                    ("dublin", "Dublin"),
                    ("munich", "Munich"),
                    ("münchen", "Munich"),
                ]
                for ev in events:
                    summary = ev.get("summary", "")
                    loc = ev.get("location", "")
                    desc = ev.get("description", "")
                    blob = f"{summary} {loc} {desc}".lower()
                    for kw, canonical in known_places:
                        if kw in blob:
                            return canonical
        except Exception:
            pass
    return None

def format_date_compact(dt: datetime) -> tuple[str, str]:
    weekday = dt.strftime("%a")
    bold_part = dt.strftime("%-d %b %Y")
    return weekday, bold_part

def generate_card_for_city(
    city_name: str,
    target_dt: datetime,
    api_key: str,
    resolution: str,
    aspect_ratio: str,
    model_name_pref: str,
    output_path: str | None = None,
) -> Path:
    geo = geocode_city(city_name)
    display_city = geo["name"]
    weekday_str, bold_date_str = format_date_compact(target_dt)

    air = fetch_air_weather(geo["lat"], geo["lon"], geo["timezone"])
    if geo["is_zurich"]:
        water_temp = fetch_zuerichsee_water_temp()
        water_label = "Acqua Limmat / Lago di Zurigo"
    else:
        water_temp = fetch_marine_water_temp(geo["lat"], geo["lon"])
        water_label = f"Acqua / Mare ({display_city})"

    rounded_water = round(water_temp) if water_temp is not None else None
    rain_badge_en = f"☔ Rain ({air['precip_prob']}%)" if air["umbrella"] else "☀️ No Rain"
    umbrella_it = "☔ SÌ, porta l'ombrello!" if air["umbrella"] else "🌂 NO, non serve l'ombrello."

    region_suffix = f" ({geo['admin']}, {geo['country']})" if geo.get("admin") and geo.get("country") else (f" ({geo['country']})" if geo.get("country") else "")
    if geo["is_zurich"]:
        landmarks_desc = (
            "The diorama features Zurich's most iconic landmarks and elements: "
            "the Romanesque twin towers of Grossmünster cathedral on the left bank, the tall green-copper steeple of Fraumünster church on the right bank, "
            "the historic stone Münsterbrücke bridge carrying a classic blue-and-white Zurich municipal tram (VBZ), and a prominent foreground body of "
            "deep crystal-clear blue water where the Limmat river meets Lake Zurich (Zürichsee) with tiny sailboats and gentle ripples."
        )
    elif rounded_water is not None:
        landmarks_desc = (
            f"The diorama features the most iconic landmarks, charming local architecture, and scenic coastal waterfront of {display_city}{region_suffix}, "
            f"with a prominent foreground body of crystal-clear blue sea/coastal water with tiny boats and gentle ripples."
        )
    else:
        landmarks_desc = (
            f"The diorama features the most iconic local landmarks, historic piazzas, charming regional architecture, trees, and authentic landscape of {display_city}{region_suffix} "
            f"(inland town — no sea or ocean water)."
        )

    if rounded_water is not None:
        water_thermometer_desc = (
            f"\n\nIn the foreground directly in the calm blue water, place a charming miniature 3D floating glass red-bulb water thermometer bobbing vertically in the water "
            f"(supported by a small blue-and-white lifebuoy ring at the waterline) with crisp white 3D lettering right next to it displaying: \"🌊 {rounded_water}°C\". "
        )
    else:
        water_thermometer_desc = ""

    frame_style = (
        "styled like a sleek, modern vertical iPhone weather card with a thin translucent glass bezel where fluffy 3D clouds subtly billow out over the edges of the frame"
        if aspect_ratio in ("3:4", "9:16")
        else "styled like a sleek widescreen 16:9 Google Nest Hub smart display weather dashboard with a thin translucent glass bezel and fluffy 3D clouds subtly billowing at the edges"
    )

    prompt = (
        f"Present a clear, {aspect_ratio} 45° top-down isometric miniature 3D cartoon diorama scene of {display_city} {frame_style} on a soft warm neutral background plinth. "
        f"{landmarks_desc}"
        f"{water_thermometer_desc}"
        f"\n\nUse soft, refined textures with realistic PBR materials, gentle lifelike morning lighting and shadows. "
        f"Integrate the {air['condition']} directly into the city environment to create an immersive atmospheric mood with {air['atmosphere']}. "
        f"\n\nAt the top-center of the card, arrange the clean Apple-style typographic hierarchy with centered spacing: "
        f"1. Title: \"{display_city}\" in large bold dark text. "
        f"2. Directly beneath it, a prominent 3D weather icon ({air['icon']}). "
        f"3. Beneath the icon, the compact date in smaller text where the weekday is regular weight and the day-month-year is bold: \"{weekday_str} {bold_date_str}\" (with \"{bold_date_str}\" in bold). "
        f"4. Beneath the date, the daily Min/Max temperature range in crisp medium-large bold text using the division/range obelus symbol \"÷\": "
        f"\"🌡️ {air['min_temp']}° ÷ {air['max_temp']}°C  •  {rain_badge_en}\", where the minimum temperature \"{air['min_temp']}°\" is rendered in crisp icy blue (#2563EB), the \"÷\" symbol is dark neutral charcoal, and the maximum temperature \"{air['max_temp']}°C\" is rendered in warm coral red (#DC2626). "
        f"\n\nAt the very bottom corners of the card (in tiny, subtle, unobtrusive footer typography): "
        f"- Bottom-left corner: \"Now {air['current_temp']}°C\" "
        f"- Bottom-right corner: \"🌅 {air['sunrise']}  •  🌇 {air['sunset']}\"."
    )

    slug = re.sub(r"[^a-z0-9]+", "_", display_city.lower()).strip("_")
    ratio_suffix = "_wide" if aspect_ratio == "16:9" else ""
    out_png = Path(output_path) if output_path else Path(f"/tmp/{slug}_weather{ratio_suffix}_{target_dt.strftime('%Y-%m-%d')}.png")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_jpg = out_png.with_suffix(".jpg")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    models = [model_name_pref, "gemini-3.1-flash-image"]
    image_saved = False

    for model_name in models:
        try:
            print(f"Generating {display_city} weather artwork ({resolution}, {aspect_ratio}) with {model_name}...", file=sys.stderr)
            image_config = {"image_size": resolution, "aspect_ratio": aspect_ratio}
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(**image_config)
                )
            )

            if response.parts:
                for part in response.parts:
                    if part.inline_data is not None:
                        image_bytes = part.inline_data.data
                        if isinstance(image_bytes, str):
                            import base64
                            image_bytes = base64.b64decode(image_bytes)
                        from io import BytesIO
                        img = Image.open(BytesIO(image_bytes))
                        if img.mode == "RGBA":
                            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                            rgb_img.paste(img, mask=img.split()[3])
                            rgb_img.save(str(out_png), "PNG")
                            rgb_img.save(str(out_jpg), "JPEG", quality=85)
                        else:
                            img.convert("RGB").save(str(out_png), "PNG")
                            img.convert("RGB").save(str(out_jpg), "JPEG", quality=85)
                        image_saved = True
                        break
            if image_saved:
                break
        except Exception as e:
            print(f"Warning: Model {model_name} failed ({e}), trying fallback...", file=sys.stderr)

    if not image_saved:
        print(f"Error: No image returned from model response for {display_city}.", file=sys.stderr)
        sys.exit(1)

    if aspect_ratio != "16:9":
        print(f"=== METEO {display_city.upper()} — {target_dt.strftime('%d/%m/%Y')} ({weekday_str} {bold_date_str}) ===")
        print(f"Condizioni: {air['label_it']} ({air['condition_it']})")
        print(f"Temperature Aria (Min ÷ Max): 🌡️ {air['min_temp']}° ÷ {air['max_temp']}°C (Attuale mattino: {air['current_temp']}°C)")
        print(f"Alba e Tramonto: 🌅 {air['sunrise']} • 🌇 {air['sunset']}")
        print(f"Verdetto Ombrello: {umbrella_it} (Prob. pioggia: {air['precip_prob']}%, {air['daily_precip']} mm)")
        if water_temp is not None:
            print(f"{water_label}: 🌡️🌊 {water_temp:.1f}°C (~{rounded_water}°C)")
        print(f"Saved PNG: {out_png}")
        print(f"Saved JPG: {out_jpg}")
        print(f"MEDIA:{out_jpg}")
    else:
        print(f"Saved 16:9 Nest Hub JPG: {out_jpg}", file=sys.stderr)
    return out_jpg

def cast_image_to_nest_hub(
    image_path: Path,
    nest_ip: str = "192.168.86.248",
    title: str = "Zurich Morning Weather",
    duration_sec: int = 1800,
) -> bool:
    """
    Casts a 16:9 JPEG image persistently to the Google Nest Hub (Default Media Receiver).
    Why MP4 with silent AAC + faststart:
    - Casting a static JPEG has duration=None (IDLE/PAUSED), causing Nest Hub to revert to Ambient Mode (clock/photos) within seconds.
    - Casting a 1fps video without audio or without -movflags +faststart stalls the Nest Hub hardware decoder in state=UNKNOWN.
    - Encoding a 10s H.264+AAC segment and looping it via -stream_loop + -movflags +faststart takes ~0.5s and keeps player_state=PLAYING for 30 minutes.
    """
    import socket
    import subprocess

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((nest_ip, 8009))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Warning: Could not determine LAN IP for Nest Hub {nest_ip} ({e})", file=sys.stderr)
        return False

    seg_mp4 = image_path.parent / f"{image_path.stem}_seg10.mp4"
    cast_mp4 = image_path.parent / f"{image_path.stem}_cast.mp4"
    loops = max(1, (duration_sec // 10) - 1)

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-loop", "1", "-framerate", "5", "-i", str(image_path),
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-c:v", "libx264", "-preset", "fast", "-tune", "stillimage", "-crf", "24",
                "-profile:v", "main", "-level", "4.0", "-pix_fmt", "yuv420p",
                "-vf", "scale=1280:720", "-r", "10", "-g", "100",
                "-c:a", "aac", "-b:a", "32k", "-t", "10",
                str(seg_mp4),
            ],
            check=True,
            timeout=20,
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-stream_loop", str(loops), "-i", str(seg_mp4),
                "-c", "copy", "-movflags", "+faststart",
                str(cast_mp4),
            ],
            check=True,
            timeout=20,
        )
        seg_mp4.unlink(missing_ok=True)
    except Exception as e:
        print(f"Warning: ffmpeg MP4 packaging for Nest Hub failed ({e})", file=sys.stderr)
        return False

    port = 8768
    # Stop any previous HTTP server listening on port 8768
    subprocess.run(f"lsof -tiTCP:{port} -sTCP:LISTEN | xargs kill -9 2>/dev/null || true", shell=True)

    server_script = f"""
import os, re, socketserver, threading
from http.server import BaseHTTPRequestHandler
from pathlib import Path

mediapath = Path({repr(str(cast_mp4))})
stats = mediapath.stat()

class RangeHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def do_GET(self):
        first, last = 0, stats.st_size - 1
        if "Range" in self.headers:
            m = re.match(r"bytes=(\\d+)-(\\d+)?", self.headers["Range"])
            if m:
                first = int(m.group(1))
                if m.group(2): last = int(m.group(2))
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {{first}}-{{last}}/{{stats.st_size}}")
        else:
            self.send_response(200)
        length = last - first + 1
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Content-Length", str(length))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        with open(mediapath, "rb") as f:
            f.seek(first)
            rem = length
            while rem > 0:
                buf = f.read(min(65536, rem))
                if not buf: break
                try:
                    self.wfile.write(buf)
                except Exception:
                    break
                rem -= len(buf)

# Auto-exit after duration_sec + 120s so no orphan process stays forever
threading.Timer({duration_sec + 120}, os._exit, args=(0,)).start()
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("0.0.0.0", {port}), RangeHandler)
httpd.serve_forever()
"""
    subprocess.Popen(
        [sys.executable, "-c", server_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    cast_code = f"""
import time, pychromecast
cast = pychromecast.get_chromecast_from_host(({repr(nest_ip)}, 8009, None, None, None))
cast.wait(timeout=5.0)
cast.start_app("CC1AD845")
time.sleep(2.0)
mc = cast.media_controller
mc.play_media("http://{lan_ip}:{port}/{cast_mp4.name}", "video/mp4", title={repr(title)}, stream_type="BUFFERED")
mc.block_until_active(timeout=8.0)
for _ in range(5):
    time.sleep(1.0)
    mc.update_status()
    if mc.status.player_state == "PLAYING":
        break
print("STATE:" + str(mc.status.player_state))
"""
    uv_bin = "/Users/riccardo/.local/bin/uv"
    if not Path(uv_bin).exists():
        uv_bin = "uv"
    try:
        res = subprocess.run(
            [uv_bin, "run", "--no-progress", "--with", "pychromecast", "python3", "-c", cast_code],
            capture_output=True, text=True, timeout=25
        )
        if res.returncode == 0 and "STATE:PLAYING" in res.stdout:
            print(f"📺 Casted 16:9 weather card ({duration_sec // 60}m MP4) to Living Room Nest Hub ({nest_ip}) [PLAYING]: {image_path}", file=sys.stderr)
            return True
        else:
            print(f"Warning: Nest Hub cast status={res.stdout.strip()} err={res.stderr.strip()}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Nest Hub cast failed ({e})", file=sys.stderr)
    return False

def main():
    parser = argparse.ArgumentParser(description="Generate daily Zurich (and optional travel destination) isometric 3D weather artwork.")
    parser.add_argument("--city", "--location", "-c", "-l", dest="city", default="Zurich", help="City or location name, e.g. 'Zurich' or 'Argenta, Ferrara' (default: Zurich)")
    parser.add_argument("--travel-city", "-t", default=None, help="Explicit second travel city to also generate alongside Zurich")
    parser.add_argument("--auto-travel", action="store_true", help="Auto-detect travel city from ~/.hermes/current_location.txt or Google Calendar and generate BOTH cards if traveling")
    parser.add_argument("--cast-nest", action="store_true", help="Also generate a 16:9 horizontal version and cast it to the Living Room Google Nest Hub (192.168.86.248)")
    parser.add_argument("--nest-ip", default="192.168.86.248", help="Google Nest Hub IP address (default: 192.168.86.248)")
    parser.add_argument("--output", "-o", default=None, help="Output PNG path (default: /tmp/<city>_weather_YYYY-MM-DD.png)")
    parser.add_argument("--date", "-d", default=None, help="Target date YYYY-MM-DD (default: today)")
    parser.add_argument("--resolution", "-r", default="2K", choices=["1K", "2K", "4K"], help="Image resolution")
    parser.add_argument("--aspect-ratio", "-a", default="3:4", choices=["3:4", "16:9", "4:3", "1:1", "9:16"], help="Aspect ratio (default: 3:4 vertical)")
    parser.add_argument("--api-key", "-k", default=None, help="Gemini API Key override")
    parser.add_argument("--model", "-m", default="gemini-3-pro-image", help="Gemini image model (default: gemini-3-pro-image)")
    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    target_dt = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()

    # 1. Primary city (default: Zurich)
    generate_card_for_city(
        city_name=args.city,
        target_dt=target_dt,
        api_key=api_key,
        resolution=args.resolution,
        aspect_ratio=args.aspect_ratio,
        model_name_pref=args.model,
        output_path=args.output,
    )

    # 2. Optional 16:9 Google Nest Hub widescreen version + live Cast to Soggiorno
    if args.cast_nest:
        wide_jpg = generate_card_for_city(
            city_name=args.city,
            target_dt=target_dt,
            api_key=api_key,
            resolution=args.resolution,
            aspect_ratio="16:9",
            model_name_pref=args.model,
            output_path=None,
        )
        cast_image_to_nest_hub(wide_jpg, nest_ip=args.nest_ip, title=f"{args.city} Weather — {target_dt.strftime('%a %-d %b %Y')}")

    # 3. Optional second card if traveling away from Zurich
    second_city = args.travel_city or (detect_travel_city() if args.auto_travel else None)
    if second_city and second_city.strip().lower() != args.city.strip().lower():
        print(f"\n✈️ Travel destination detected: {second_city}! Generating second weather card...", file=sys.stderr)
        generate_card_for_city(
            city_name=second_city,
            target_dt=target_dt,
            api_key=api_key,
            resolution=args.resolution,
            aspect_ratio=args.aspect_ratio,
            model_name_pref=args.model,
            output_path=None,
        )

if __name__ == "__main__":
    main()


