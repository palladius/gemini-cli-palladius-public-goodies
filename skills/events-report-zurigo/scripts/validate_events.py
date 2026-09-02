#!/usr/bin/env python3
"""
Strict JSON Event Validator for events-report-zurigo.
Enforces:
1. Exact calendar date within [Today, Today + 7 days].
2. Direct, non-generic URL starting with http:// or https://.
3. Specific physical street address (not just 'Zurich').
4. Specific event title (no generic place names).
"""
import sys
import json
import datetime
import re
from urllib.parse import urlparse

def validate_event(item: dict, today: datetime.date = None) -> tuple[bool, str]:
    if today is None:
        today = datetime.date.today()
    max_date = today + datetime.timedelta(days=7)

    # 1. Check title
    title = item.get("title", "").strip()
    if not title or len(title) < 5:
        return False, "Title missing or too short"
    
    # Generic place ban check
    banned_generic = ["seebad", "tramonto", "passeggiata", "visita al parco"]
    if any(b in title.lower() for b in banned_generic) and "meetup" not in title.lower() and "concert" not in title.lower():
        return False, f"Title '{title}' appears to be a generic placeholder/activity"

    # 2. Check date
    date_str = item.get("date", "").strip()
    if not date_str or not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False, f"Invalid ISO date format: '{date_str}' (must be YYYY-MM-DD)"
    
    try:
        ev_date = datetime.date.fromisoformat(date_str)
    except ValueError as e:
        return False, f"Invalid calendar date: {e}"
    
    if ev_date < today:
        return False, f"Event date {ev_date} is in the PAST (today is {today})"
    if ev_date > max_date:
        return False, f"Event date {ev_date} is beyond +7 days limit (max {max_date})"

    # 3. Check address
    address = item.get("address", "").strip()
    if not address or len(address) < 8 or not re.search(r'\d+', address):
        return False, f"Address '{address}' is missing specific street number / location details"

    # 4. Check URL
    url = item.get("url", "").strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        return False, f"URL '{url}' is invalid (must start with http/https)"
    
    parsed = urlparse(url)
    if not parsed.netloc or parsed.path in ["", "/"]:
        return False, f"URL '{url}' is a generic domain root, not a specific event link"

    return True, "OK"

def validate_events_file(file_path: str, today: datetime.date = None) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("JSON root must be an array of event objects")
    
    valid_events = []
    print(f"--- Validating {len(data)} events against 7-day window ---")
    for i, ev in enumerate(data):
        ok, msg = validate_event(ev, today=today)
        if ok:
            print(f"  ✅ [VALID] {ev.get('title')} ({ev.get('date')}) @ {ev.get('address')}")
            valid_events.append(ev)
        else:
            print(f"  ❌ [REJECTED] {ev.get('title', 'Unknown')}: {msg}")
    
    return valid_events

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_events.py <path_to_json_file> [YYYY-MM-DD]")
        sys.exit(1)
    
    target_file = sys.argv[1]
    custom_today = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date.today()
    
    valid = validate_events_file(target_file, today=custom_today)
    print(f"\nResult: {len(valid)} passed verification.")
