# Event Verification & Extraction Protocol (Zurich Focus)

## 1. The Archive Trap
Many cultural and event websites (e.g. Società Dante Alighieri, Istituto Italiano di Cultura, local clubs) list past events mixed with upcoming ones or retain historical blog entries under `/eventi/`.
- **Trap**: Searching for keywords (like "Stefano Benni" or "Mostra") can hit articles from months or years prior.
- **Rule**: Never trust an event listing based on publication date or page presence alone. You must locate the actual event schedule within the body text (e.g., `mercoledì 14 febbraio 2026`).
- **Validation**: Verify that `date` is strictly $\ge Today$ and $\le Today + 7\text{ days}$. Any date outside this window must be discarded immediately.

## 2. No Generic Placeholders
- Do not list public parks, venues, or outdoor baths (e.g., "Seebad Enge", "Museum Rietberg") unless there is an actual, specific ticketed or scheduled event with:
  - Exact event title
  - Start time
  - Specific physical street address with number
  - Direct individual event URL (no generic domain roots like `https://seebadenge.ch/`)

## 3. Zurich Postal Code Rules
- **Inner City / Enge / Central Districts (8001 ➔ 8032)**:
  - Omit the CAP in output: `(Europaallee 36, Zürich)`, `(Pelikanplatz 18, Zürich)`, `(Parkring 30, Zürich)`.
- **Outer Districts (> 8032)**:
  - Keep the CAP for clarity: `(Thurgauerstrasse 40, 8050 Zürich)`.
- **Maps**: Always prepend `📍` and wrap the address in a Google Maps URL search query:
  `[📍 Europaallee 36, Zürich](https://maps.google.com/?q=Europaallee+36,+Z%C3%BCrich)`
