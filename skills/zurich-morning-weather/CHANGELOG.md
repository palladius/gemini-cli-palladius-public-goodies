# Changelog

All notable changes to the `zurich-morning-weather` skill will be documented in this file.

## [0.2.0] - 2026-11-08

### Changed
- Redesigned typography for sleek winter iPhone-card style:
  - Compact date (`Mon **9 Nov 2026**`) with bold day/month/year.
  - Top-center daily range using `🌡️ min° % max°C` + rain/umbrella indicator (`☔ Rain` / `🌂 No Rain`).
  - Added miniature 3D glass water thermometer next to the floating water badge in the Limmat/Lake Zurich (`🌡️ XX°C`).
  - Relegated early-morning current temperature (`Now X°C`) to bottom-left footer and Sunrise/Sunset (`🌅 HH:MM • 🌇 HH:MM`) to bottom-right footer.

## [0.1.0] - 2026-11-05

### Added
- Initial release of the `zurich-morning-weather` skill.
- Automated Open-Meteo weather integration for Zurich.
- 45° top-down isometric 3D miniature diorama prompt generator for Grossmünster, Fraumünster, Limmat river, and Zurich tram.
- Top-centered typography layout (City, 3D weather glyph, ordinal date, temperature).
- Dual output generation (PNG and Telegram-optimized 85% JPEG).
