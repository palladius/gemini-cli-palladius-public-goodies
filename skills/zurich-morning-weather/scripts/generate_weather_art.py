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
import urllib.request
from PIL import Image, ImageDraw, ImageFont

WMO_WEATHER_MAP = {
    0: {
        "condition": "crisp clear sunny skies",
        "atmosphere": "bright golden morning sun, long soft shadows, and crystal-clear visibility towards the distant Alps",
        "icon": "radiant golden 3D sun with soft glowing light beams"
    },
    1: {
        "condition": "mainly clear skies with scattered light clouds",
        "atmosphere": "soft warm morning sunlight with a few small fluffy white clouds drifting overhead",
        "icon": "golden 3D sun peeking out from behind a small fluffy white cloud"
    },
    2: {
        "condition": "partly cloudy autumn weather",
        "atmosphere": "gentle golden ambient light, delicate wisps of clouds, and cozy autumn morning atmosphere",
        "icon": "partly cloudy 3D weather icon with a golden sun emerging from behind soft puffy white clouds"
    },
    3: {
        "condition": "overcast atmospheric cloudy skies",
        "atmosphere": "soft, diffused ambient lighting casting gentle, smooth shadows across the city",
        "icon": "soft, puffy layered 3D grey and white clouds"
    },
    45: {
        "condition": "morning autumn fog and mist",
        "atmosphere": "delicate low-lying mist floating above the Limmat river and lake, with church spires rising gracefully through the haze",
        "icon": "stylized 3D cloud with horizontal mist and fog lines"
    },
    48: {
        "condition": "frosty rime fog",
        "atmosphere": "frost-dusted rooftops and trees with cool ethereal morning mist",
        "icon": "cool 3D winter cloud with glistening frost crystals"
    },
    51: {
        "condition": "light gentle autumn drizzle",
        "atmosphere": "glistening wet cobblestones with reflections of streetlights and church towers, and tiny micro-raindrops",
        "icon": "soft 3D cloud with tiny delicate blue raindrops"
    },
    61: {
        "condition": "gentle autumn rain",
        "atmosphere": "wet reflective streets, subtle ripple rings across the surface of the Limmat river, and moody atmospheric clouds",
        "icon": "3D rain cloud with neat parallel falling rain streaks"
    },
    63: {
        "condition": "moderate rain",
        "atmosphere": "glossy wet cobblestone reflections, cozy indoor glows in city windows, and rhythmic rain ripples on the lake",
        "icon": "darker 3D rain cloud with bold falling raindrops"
    },
    71: {
        "condition": "light winter snowfall",
        "atmosphere": "fresh white snow gently coating church roofs, bridges, and trees, with soft floating snowflakes in the air",
        "icon": "3D cloud with delicate white snowflakes falling"
    },
    73: {
        "condition": "winter snow",
        "atmosphere": "picturesque winter wonderland with snowy rooftops, a snow-dusted tram, and frosty riverbanks",
        "icon": "3D snow cloud with intricate crystalline snowflakes"
    },
    95: {
        "condition": "dramatic thunderstorm",
        "atmosphere": "deep moody skies with dramatic contrast and soft warm glows from shop windows",
        "icon": "3D dark cloud with a bright golden lightning bolt"
    }
}

def get_api_key(provided_key: str | None) -> str | None:
    key = provided_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        m = re.search(r'(AIzaSy[A-Za-z0-9_-]+)', key)
        if m:
            return m.group(1)
        return key.strip()
    return None

def fetch_zurich_air_weather() -> dict:
    url = "https://api.open-meteo.com/v1/forecast?latitude=47.3769&longitude=8.5417&current=temperature_2m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=Europe%2FZurich"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ZurichWeatherSkill/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            current_temp = round(data["current"]["temperature_2m"])
            code = data["current"]["weather_code"]
            min_temp = round(data["daily"]["temperature_2m_min"][0])
            max_temp = round(data["daily"]["temperature_2m_max"][0])
            info = WMO_WEATHER_MAP.get(code, WMO_WEATHER_MAP[2])
            return {
                "current_temp": current_temp,
                "min_temp": min_temp,
                "max_temp": max_temp,
                "code": code,
                "condition": info["condition"],
                "atmosphere": info["atmosphere"],
                "icon": info["icon"],
            }
    except Exception as e:
        print(f"Warning: Could not fetch Open-Meteo weather ({e}), using seasonal defaults.", file=sys.stderr)
        return {
            "current_temp": 9,
            "min_temp": 6,
            "max_temp": 12,
            "code": 2,
            "condition": "partly cloudy autumn weather",
            "atmosphere": "gentle golden ambient light, delicate wisps of clouds, and cozy autumn morning atmosphere",
            "icon": "partly cloudy 3D weather icon with a golden sun emerging from behind soft puffy white clouds",
        }

def fetch_zuerichsee_water_temp() -> float:
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
        print(f"Warning: Could not fetch water temperature ({e}), fallback to 13.0°C", file=sys.stderr)
    return 13.0

def format_date_ordinal(dt: datetime) -> str:
    day = dt.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return dt.strftime(f"%B {day}{suffix}, %Y")

def main():
    parser = argparse.ArgumentParser(description="Generate daily Zurich isometric 3D weather artwork.")
    parser.add_argument("--output", "-o", default=None, help="Output PNG path (default: /tmp/zurich_weather_YYYY-MM-DD.png)")
    parser.add_argument("--date", "-d", default=None, help="Target date YYYY-MM-DD (default: today)")
    parser.add_argument("--resolution", "-r", default="2K", choices=["1K", "2K", "4K"], help="Image resolution")
    parser.add_argument("--aspect-ratio", "-a", default="3:4", choices=["3:4", "16:9", "4:3", "1:1", "9:16"], help="Aspect ratio (default: 3:4 vertical)")
    parser.add_argument("--api-key", "-k", default=None, help="Gemini API Key override")
    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    target_dt = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
    formatted_date = format_date_ordinal(target_dt)

    air = fetch_zurich_air_weather()
    water_temp = fetch_zuerichsee_water_temp()
    rounded_water = round(water_temp)
    print(f"Zurich Weather: Air {air['current_temp']}°C (Min {air['min_temp']}°C / Max {air['max_temp']}°C) - {air['condition']}")
    print(f"Zürichsee Water: {water_temp}°C (~{rounded_water}°C)")

    prompt = (
        f"Present a clear, vertical 45° top-down isometric miniature 3D cartoon diorama scene of Zurich featuring its most iconic landmarks and elements: "
        f"the Romanesque twin towers of Grossmünster cathedral on the left bank, the tall green-copper steeple of Fraumünster church on the right bank, "
        f"the historic stone Münsterbrücke bridge carrying a classic blue-and-white Zurich municipal tram (VBZ), and a prominent foreground body of "
        f"deep crystal-clear blue water representing Lake Zurich (Zürichsee) with tiny sailboats and gentle ripples. "
        f"\n\nIn the foreground directly upon the calm blue surface of Lake Zurich, there is a prominent, stylized 3D floating circular buoy/signpost in deep royal blue with crisp white border and lettering displaying: \"🌊 {rounded_water}°C\" (lake water temperature). "
        f"\n\nUse soft, refined textures with realistic PBR materials, gentle lifelike lighting and shadows. "
        f"Integrate the {air['condition']} directly into the city environment to create an immersive atmospheric mood with {air['atmosphere']}. "
        f"\n\nUse a clean, minimalistic vertical composition with a soft, solid-colored neutral background plinth. "
        f"\n\nAt the top-center, place the title \"Zurich\" in large bold text, a prominent weather icon beneath it ({air['icon']}), "
        f"then the date \"{formatted_date}\" in clean small text, and the temperature readout in crisp medium text: "
        f"\"Air: {air['current_temp']}°C • Min {air['min_temp']}°C / Max {air['max_temp']}°C • Lake: {rounded_water}°C 🌊\". "
        f"All text must be centered with consistent spacing and elegant typographic hierarchy."
    )

    out_png = Path(args.output) if args.output else Path(f"/tmp/zurich_weather_vertical_{target_dt.strftime('%Y-%m-%d')}.png")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_jpg = out_png.with_suffix(".jpg")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    print(f"Generating Zurich vertical weather artwork ({args.resolution}, {args.aspect_ratio})...")

    image_config = {"image_size": args.resolution, "aspect_ratio": args.aspect_ratio}
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(**image_config)
        )
    )

    image_saved = False
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

    if not image_saved:
        print("Error: No image returned from model response.", file=sys.stderr)
        sys.exit(1)

    print(f"Saved PNG: {out_png}")
    print(f"Saved JPG: {out_jpg}")
    print(f"MEDIA:{out_jpg}")

if __name__ == "__main__":
    main()
