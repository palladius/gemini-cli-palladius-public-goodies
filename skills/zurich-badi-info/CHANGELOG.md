# Changelog - zurich-badi-info

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-05-29
### Added
- Initial implementation of the `zurich-badi-info` skill.
- Created `badi_info.py` script to fetch real-time XML data from the City of Zurich, flow rate from BAFU (api.existenz.ch), and weather from wttr.in.
- Added custom heuristics for morning Ironman swims (Utoquai) and family pools (Heuried/Mythenquai/Tiefenbrunnen if > 25°C).
- Implemented weekend safety alerts for Limmat dinghy/canotto floating.
