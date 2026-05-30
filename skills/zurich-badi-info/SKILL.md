---
name: zurich-badi-info
description: (💛) Real-time water temperatures, open status of Zurich badis (lakes, river/Letten, pools), outside weather recommendations for family trips, and Limmat canotto/dinghy flow safety alerts.
compatibility: Gemini CLI
metadata:
  version: 0.1
---

# Zurich Badi & Water Temperature Skill

This skill provides real-time information about Zurich's outdoor pools (Freibäder), river pools (Flussbäder), and lake beaches (Seebäder). It includes dedicated alerts and recommendations tailored for:
1. **Ironman Swimming (Utoquai)**: Tracking morning status and water temperature for early swims.
2. **Family Outings (Heuried, Mythenquai, Tiefenbrunnen)**: Checks the outside temperature using a live weather feed and recommends going if it is **above 25°C**.
3. **Limmat Canotto/Dinghy Floating**: Checks the live river flow rate (BAFU station 2099 - Zürich Unterhard) and issues safety warnings (discharge must be **<= 100 m³/s**).

## Usage

Activate this skill when the user asks about:
- Water temperature of Zurich's lake, Limmat, or specific outdoor pools (e.g., Utoquai, Letten, Heuried).
- Going down the Limmat in an inflatable boat/dinghy ("canotto" or "bööteln").
- Weather-based pool recommendations.

## Lake Zurich Microclimates

- **West vs. East Side**: The West Side of the Lake (e.g., Seebad Enge, Strandbad Mythenquai) is typically **1-2°C warmer** than the East Side (e.g., Seebad Utoquai, Strandbad Tiefenbrunnen) due to prevailing winds, sun exposure, and water current patterns. Keep this geographical nuance in mind when choosing a swimming spot.
- **Disconnected Pools (e.g. Heuried)**: Pools not directly fed or tempered by the lake have a different water temperature cycle. They are highly sensitive to direct solar irradiation and air temperature, warming up and cooling down much faster than the large thermal mass of the Zürichsee.

## Water Temperature Brackets

Water temperatures are color-coded with custom indicators based on comfort levels:
- 🔴 **Red** (`< 18°C`): Very fresh / cold (typical for early season or deep lake/river).
- 🟠 **Orange** (`18°C - 19°C`): Refreshing (good for active swimming).
- 🟡 **Yellow** (`20°C - 24°C`): Comfortable (ideal for family lake swimming).
- 🟢 **Green** (`25°C+`): Warm (typical for highly solar-irradiated pools like Heuried).

## Utility Scripts

The skill includes a powerful Python CLI utility located in `scripts/badi_info.py` which fetches and parses live XML data from the City of Zurich, BAFU flow data, and Zurich weather:

### Subcommands

#### 1. Summary
Provides a high-level summary of your favorite pools, outside temperature, and Limmat floating safety:
```bash
uv run scripts/badi_info.py summary
```

#### 2. List All Badis
Lists all available outdoor pools, river pools, and lakes:
```bash
# List all
uv run scripts/badi_info.py list

# Filter by type (lake, river, pool)
uv run scripts/badi_info.py list --type lake

# Show only currently open badis
uv run scripts/badi_info.py list --open
```

#### 3. Search Badi
Search for a specific pool by name:
```bash
uv run scripts/badi_info.py search utoquai
```

## Common Mistakes
- **German Umlauts**: Use "zurich-badi-info" (without 'e') instead of "zuerich-badi-info" to match the user's preference.
- **Metric System Only**: Ensure all temperatures are displayed strictly in Celsius (°C) and flow rates in cubic meters per second (m³/s).
