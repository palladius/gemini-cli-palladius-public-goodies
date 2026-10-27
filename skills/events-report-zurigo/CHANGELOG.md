# Changelog

## 2.0.2 - 2026-10-27
- Added Eawag Alplakes REST API (Delft3D 3D hydrodynamic model/forecast) fallback in `scripts/bike_weather.py`.
- Added `safe_urlopen` SSL context fallback for macOS network requests.

## 2.0.1 - 2026-10-23
- Added direct Tecson live sensor hardware telemetry fallback (Wasserschutzpolizei origin) for Tiefenbrunnen and Mythenquai in `scripts/bike_weather.py`.

## 2.0.0 - 2026-10-21
- Added Zurich cycling & lake weather ("Zona T-Shirt" protocol) and `scripts/bike_weather.py`.
- Added multi-source live Lake Zurich water temperature feeds (Tecdottir, Stadt Zürich Open Data, wiewarm.ch).
- Added `references/event_verification_protocol.md` and enhanced zero-tolerance rules.

## 0.1 - 2026-09-02
- Initial release of `events-report-zurigo`.
- Strict 7-day window filtering (`Today` to `Today + 7d`).
- Zero-hallucination JSON schema validation script (`scripts/validate_events.py`).
- Focused on Italian culture (IIC, Dante), Enge/Centro, and AI/Big Tech (Google, NVIDIA, AWS, MS, ETH).
- Compact output formatting with Google Maps pin links and inner-circle (8001-8032) postal code omission.
