---
name: events-report-zurigo
description: >-
  Generates a verified daily report in Italian about upcoming events in Zurich within a strict 7-day window (Today to Today + 7d). Mandates hard JSON schema verification with exact URL, verified calendar date, and physical address before formatting.
version: 2.0.0
compatibility: Gemini CLI
author: ErmeteBottazzi
license: MIT
metadata:
  version: 2.0.0
  hermes:
    tags: [journalism, news, events, zurich, enge, italian-community, ai, tech, verification, json]
    category: productivity
---

# Events Report Zurich Skill (Strict JSON Verification & Zero-Hallucination Policy)

This skill automates the extraction and generation of a verified events report in Italian for Zurich.

## 🚫 ZERO-TOLERANCE RULES (Strict Data Integrity)

1. **NO "Vague" or Generic Activities**:
   - Places (like "Museum Rietberg" or "Seebad Enge") without a specific scheduled event are **STRICTLY FORBIDDEN**.
   - Generic recommendations, permanent exhibits, or "go have a drink" placeholders are **BANNED**.

2. **MANDATORY Event Attributes (Every single event MUST have)**:
   - `id`: Unique slug.
   - `title`: Exact official name of the specific event.
   - `date`: Exact ISO date (`YYYY-MM-DD`) strictly in $[Today, Today + 7\text{ days}]$.
   - `time`: Exact starting time (e.g. `18:00 CEST`).
   - `address`: Full physical address (e.g. `Europaallee 36, 8004 Zürich` or `Parkring 30, 8002 Zürich`).
   - `url`: Direct specific event page URL (NOT a generic homepage or search query URL).
   - `category`: One of `['ai_tech', 'italian_culture', 'local_enge_center']`.
   - `description`: 2-sentence concise summary of what happens at this specific event.

3. **Two-Stage Architecture (JSON First, Test, then Format)**:
   - **Stage 1 (Extraction & JSON Generation)**: Collect candidate events and save to `/tmp/events_zurich_staging.json`.
   - **Stage 2 (Validation Script)**: Execute `scripts/validate_events.py` to enforce date limits, valid URLs, non-empty addresses, and exact dates. If validation fails, the script rejects the invalid items.
   - **Stage 3 (Report Output)**: The report is rendered ONLY from the validated JSON items.

## Sources

- See `assets/event-sources.json` for verified portals (includes Swiss {ai} Weeks at `https://ai-weeks.ch/events?tag=Hackathon`, GDG Cloud Zurich, Meetups, ETH AI Center, IIC, and Enge neighborhood agendas).

## Report Output Format (Refined Map & CAP Rules)

Render the validated events in clean chronological order using this exact pattern:

* `DoW D Mon: [Titolo dell'Evento](URL) ([📍 Indirizzo](https://maps.google.com/?q=Indirizzo+URL_Encoded))`

### Postal Code (CAP) & Map Rules:
1. **Zurich Inner Circle (8001 ➔ 8032)**: Omit the postal code entirely! (e.g. `Pelikanplatz 18, Zürich`, `Europaallee 36, Zürich`, `Parkring 30, Zürich`).
2. **Outer Circle (> 8032, e.g. 8048, 8050, 8057)**: Keep the postal code because it's further out! (e.g. `Thurgauerstrasse 40, 8050 Zürich`).
3. **Map Link**: Prepend the map pin emoji `📍` and wrap the address with a direct Google Maps search link `https://maps.google.com/?q=...`.

---

## 🚴 Zurich Cycling & Lake Weather ("Zona T-Shirt" Protocol)

To avoid hallucinations on weather and water temperatures, use the verified deterministic script:
`python3 scripts/bike_weather.py [--day today|tomorrow] [--format table|csv|json] [--afternoon-only]`

### Live Lake Zurich (Zürichsee) Water Temperature:
Stadt Zürich Open Data provides real-time 10-minute water station metrics (WSP Mythenquai and Tiefenbrunnen):
- **Tecdottir REST API (Recommended)**:
  Query `https://tecdottir.herokuapp.com/measurements/{mythenquai|tiefenbrunnen}` to get `total_count`, then fetch `?offset={total_count - 1}` to obtain the latest measurement (`water_temperature`, `air_temperature`, `wind_speed_avg_10min`).
- **HTTP Range CSV**:
  Query tail bytes with HTTP Range requests to avoid downloading massive CSVs:
  `curl -s -L -r -2000 "https://data.stadt-zuerich.ch/dataset/sid_wapo_wetterstationen/download/messwerte_mythenquai_seit2007-heute.csv" | tail -n 1`
  (Column 3: `air_temperature`, Column 4: `water_temperature`).
- **Live Stadt Zürich Baths XML Feed**:
  `https://www.stadt-zuerich.ch/stzh/bathdatadownload`
  Returns current water temperature (`<temperatureWater>`) and modification timestamp for all lakeside and river badis (e.g., `Seebad Utoquai`, `Strandbad Mythenquai`, `Strandbad Tiefenbrunnen`, `Seebad Enge`). Ideal lightweight, real-time fallback.
- **wiewarm.ch JSON API (All-Season Fallback)**:
  `https://wiewarm.ch/api/v1/bad.json`
  Find `item['badid'] == '14'` (Zürichsee) for current water temperatures at `Tiefenbrunnen` and `Mythenquai` (`item['becken']['Tiefenbrunnen']['temp']`). Remains actively updated and available year-round even when open-air badis are closed for the season.

### Temperature Tiers:
- **`>= 20°C`**: 👕 **ZONA T-SHIRT** (Ideal for road cycling / Colnago ready, short sleeves, dry asphalt)
- **`13.0°C - 19.9°C`**: 🧥 **Maglione lungo / Maniche lunghe** (T-shirt + windbreaker / long jersey)
- **`< 13.0°C`**: 🥶 **Troppo freddo** (Morning chill or night, winter layers needed)
- **`Pioggia > 30%`**: 🌧️ **Rischio Pioggia** (No cycling)

Data is queried directly via Open-Meteo's high-resolution model for Zurich (`47.3769, 8.5417`) without hallucinations.

Example:
* `Thu 3 Sep: [GDG Cloud Zürich Meetup #36: The Day I Left My Linux Machine Running](https://...) ([📍 Europaallee 36, Zürich](https://maps.google.com/?q=Europaallee+36,+Zurich))`
* `Sat 5 Sep: [Incontro Letterario con Laura Imai Messina](https://...) ([📍 Parkring 30, Zürich](https://maps.google.com/?q=Parkring+30,+Zurich))`
