# Changelog

All notable changes to the `zurich-morning-weather` skill will be documented in this file.

## [0.2.1] - 2026-11-13

### Changed
- Redesigned typography for sleek winter iPhone-card style (`3:4`) and widescreen Google Nest Hub dashboard (`16:9`):
  - Compact date (`Mon **9 Nov 2026**`) with bold day/month/year.
  - Top-center daily range using `🌡️ min° ÷ max°C` with icy-blue minimum (`#2563EB`) and coral-red maximum (`#DC2626`) + rain/umbrella indicator (`☔ Rain` / `☀️ No Rain`).
  - Added miniature 3D glass water thermometer in a lifebuoy ring in the Limmat/Lake Zurich (`🌊 XX°C`) via fast `wiewarm.ch` JSON API.
  - Relegated early-morning current temperature (`Now X°C`) to bottom-left footer and Sunrise/Sunset (`🌅 HH:MM • 🌇 HH:MM`) to bottom-right footer.
- Added `--location` / `--city` with comma-separated disambiguation (e.g. `"Argenta, Ferrara"`), omitting water thermometer for inland cities.
- Added `--cast-nest` to generate a `16:9` widescreen card, synthesize the "Generale Robertino" Tuscan (`+10%` speed) voice bulletin (`MEDIA:..._vannacci.mp3`), and cast a 30-minute `faststart` H.264+AAC MP4 stream to the Living Room Google Nest Hub.

## [0.1.0] - 2026-11-05

### Added
- Initial release of the `zurich-morning-weather` skill.
- Automated Open-Meteo weather integration for Zurich.
- 45° top-down isometric 3D miniature diorama prompt generator for Grossmünster, Fraumünster, Limmat river, and Zurich tram.
- Top-centered typography layout (City, 3D weather glyph, ordinal date, temperature).
- Dual output generation (PNG and Telegram-optimized 85% JPEG).
