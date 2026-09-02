---
name: events-report-zurigo
description: (💛) Generates a verified daily report in Italian about upcoming events in Zurich within a strict 7-day window (Today to Today + 7d). Focuses on Italian culture, Enge/Centro, and AI/Big Tech (Google, NVIDIA, AWS, MS, ETH) with strict address & map link validation.
compatibility: Gemini CLI
metadata:
  version: 0.1
---

# Events Report Zurich Skill (Strict 7-Day Window & JSON Verification)

This skill automates the extraction, validation, and generation of a verified events report in Italian for the City and Canton of Zurich.
It enforces a **STRICT temporal filter: ONLY events occurring between TODAY and the next 7 DAYS (Today ➔ Today + 7d)**.

## Core Focus Areas

1. 🤖 **AI & Big Tech Hub (Zurich Ecosystem)**:
   - **Big Tech**: Google Switzerland (Europaallee), NVIDIA Zurich, AWS User Group Zurich, Microsoft Reactor / Community Switzerland.
   - **AI & Research**: ETH AI Center, Zurich Machine Learning Meetup, Generative AI Zurich, AI Agent meetups.
   - **Developer Communities**: GDG Cloud Zurich, GDG Zurich, CNCF Zurich, Python Zurich.

2. 🇮🇹 **Italian Cultural & Community Focus**:
   - Italian literature, book presentations, theater in Italian, Italian cinema/screenings.
   - Istituto Italiano di Cultura (IIC Zurigo), Società Dante Alighieri, Comites Zurich, Italian comedy/music.
   - Italian tech & expat meetups, wine tastings, cultural evenings.

3. 📍 **Hyper-Local Geographic Focus**:
   - **Enge / Kreis 2**: Events around Tödistrasse, Enge station, Seebad Enge, Museum Rietberg, Belvoirpark, Quartierzentrum Enge.
   - **Zurich Center / Kreis 1 & 4**: Europaallee, Paradeplatz, Bellevue/Sechseläutenplatz, Limmatquai, Tonhalle, Kaufleuten.

## ⚠️ Strict Verification & Zero-Hallucination Rules

1. **Window**: Strictly $[T, T + 7	ext{ days}]$ (Today to Today + 7d).
2. **Discard Past/Distant Events**: All past events ($< T$) and events $> 7$ days away MUST be immediately discarded.
3. **No Generic Placeholders**: Every event must have a specific title, start time, physical street address, and direct event URL.
4. **Validation Script**: Use `scripts/validate_events.py` to verify candidate items in `/tmp/events_zurich_staging.json`.

## Sources

- See `assets/event-sources.json` for verified portals across Italian culture, Enge/Centro, and AI/Big Tech ecosystems.

## Report Output Format (Refined Map & CAP Rules)

Render the validated events in clean chronological order using this exact pattern:

* `DoW D Mon: [Titolo dell'Evento](URL) ([📍 Indirizzo](https://maps.google.com/?q=Indirizzo+URL_Encoded))`

### Postal Code (CAP) & Map Rules:
1. **Zurich Inner Circle (8001 ➔ 8032)**: Omit the postal code entirely! (e.g. `Pelikanplatz 18, Zürich`, `Europaallee 36, Zürich`, `Parkring 30, Zürich`).
2. **Outer Circle (> 8032, e.g. 8048, 8050, 8057)**: Keep the postal code because it's further out! (e.g. `Thurgauerstrasse 40, 8050 Zürich`).
3. **Map Link**: Prepend the map pin emoji `📍` and wrap the address with a direct Google Maps search link `https://maps.google.com/?q=...`.

Example:
* `Thu 3 Sep: [GDG Cloud Zürich Meetup #36: The Day I Left My Linux Machine Running](https://community.dev/events/details/developer-group-gdg-cloud-zurich-presents-gdg-cloud-zurich-meetup-36/) ([📍 Europaallee 36, Zürich](https://maps.google.com/?q=Europaallee+36,+Zurich))`
* `Sat 5 Sep: [Incontro Letterario con Laura Imai Messina: «Le parole della pioggia»](https://dantealighieri.ch/eventi/letture-e-dialogo-con-laura-imai-messina-le-parole-della-pioggia/) ([📍 Parkring 30, Zürich](https://maps.google.com/?q=Parkring+30,+Zurich))`
