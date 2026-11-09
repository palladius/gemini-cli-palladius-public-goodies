---
name: zurich-morning-weather
description: >-
  (💛) Generates daily 45° top-down isometric 3D miniature diorama weather scenes of Zurich using Nano Banana Pro (Gemini 3 Pro Image) with live weather data, iconic landmarks, and typography.
compatibility: Gemini CLI, Hermes Agent
metadata:
  version: 0.2.0
---

# Zurich Morning Weather Skill (🍌🇨🇭)

Generates a daily 45° isometric 3D diorama of Zurich styled like a vertical iPhone weather card with live telemetry and a 3D water thermometer.

## Features

- **Live Weather & Sun Sync**: Queries Open-Meteo for daily `🌡️ min° % max°C`, rain/umbrella verdict, sunrise/sunset (`🌅 / 🌇`), and supports dual-card travel mode (`--auto-travel`).
- **Iconic Landmarks + Water Thermometer**: Renders Grossmünster, Fraumünster, Münsterbrücke with VBZ tram, and a 3D glass thermometer in the Limmat/Zürichsee (`🌊 XX°C`).
- **Atmospheric Lighting**: Translates WMO weather codes into atmospheric rendering directions (e.g., golden sun, low-lying river mist, wet cobblestone reflections, or fresh winter snowfall).
- **Embedded iPhone-Card Typography**:
  - Top-center: **Zurich**, 3D weather/umbrella glyph, compact date (`Mon **9 Nov 2026**`), and `🌡️ min° % max°C • ☔/🌂`.
  - Bottom corners: subtle footer with current morning temperature (`Now X°C` bottom-left) and sunrise/sunset (`🌅 HH:MM • 🌇 HH:MM` bottom-right).
- **Dual Format Output**: Emits both full-resolution PNG and compressed 85% JPEG for instant native messaging delivery via `MEDIA:`.

## CLI Usage

Run the bundled script using `uv`:

```bash
uv run $SKILL_DIR/scripts/generate_weather_art.py
```

### Options

```bash
# Custom output path
uv run .../generate_weather_art.py --output /tmp/custom_zurich.png

# Generate for another city or generate BOTH Zurich + travel city automatically
uv run .../generate_weather_art.py --city "Lido degli Estensi"
uv run .../generate_weather_art.py --travel-city "Fernando de Noronha"
uv run .../generate_weather_art.py --auto-travel

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
