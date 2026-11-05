---
name: zurich-morning-weather
description: >-
  (💛) Generates daily 45° top-down isometric 3D miniature diorama weather scenes of Zurich using Nano Banana Pro (Gemini 3 Pro Image) with live weather data, iconic landmarks, and typography.
compatibility: Gemini CLI, Hermes Agent
metadata:
  version: 0.1.0
---

# Zurich Morning Weather Skill (🍌🇨🇭)

Generates a daily 45° top-down isometric miniature 3D cartoon diorama of Zurich featuring its most iconic landmarks (Grossmünster, Fraumünster, Limmat river, and blue-and-white VBZ tram), automatically themed to the live morning weather forecast with clean top-centered weather typography.

## Features

- **Live Weather Sync**: Automatically queries Open-Meteo for Zurich (`47.3769° N, 8.5417° E`) to retrieve current temperature, daily min/max, and WMO weather condition code.
- **Iconic Landmarks**: Accurately renders Grossmünster Romanesque twin towers, Fraumünster turquoise steeple, Münsterbrücke stone bridge, and blue-and-white Zurich municipal tram.
- **Atmospheric Lighting**: Translates WMO weather codes into atmospheric rendering directions (e.g., golden autumn sun, low-lying river mist, wet cobblestone reflections, or fresh winter snowfall).
- **Embedded Typography**: Generates crisp, centered text directly on the image with the city name, 3D weather glyph, ordinal date, and current/min/max temperature.
- **Dual Format Output**: Emits both full-resolution PNG and compressed 85% JPEG for instant native messaging delivery via `MEDIA:`.

## CLI Usage

Run the bundled script using `uv`:

```bash
uv run ~/.hermes/skills/gemini-cli-palladius-public-goodies/skills/zurich-morning-weather/scripts/generate_weather_art.py
```

### Options

```bash
# Custom output path
uv run .../generate_weather_art.py --output /tmp/custom_zurich.png

# Custom resolution (1K, 2K, 4K)
uv run .../generate_weather_art.py --resolution 2K

# Custom aspect ratio (16:9, 4:3, 1:1, 3:4)
uv run .../generate_weather_art.py --aspect-ratio 16:9

# Specific historical or future date
uv run .../generate_weather_art.py --date 2026-11-05
```

## Scheduling Daily Morning Dispatch (Cron)

To deliver this artwork every morning at 07:15 AM to your Telegram chat:

```bash
hermes cron create \
  --name "Zurich Morning Weather Art" \
  --schedule "15 7 * * *" \
  --prompt "Generate today's isometric 3D Zurich morning weather artwork using the zurich-morning-weather skill and deliver it natively with MEDIA:."
```
