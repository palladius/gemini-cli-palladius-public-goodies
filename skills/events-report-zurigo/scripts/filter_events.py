#!/usr/bin/env python3
"""
Filter events to strictly match the window: [Today, Today + 7 days].
Parses Italian and international date formats and discards past or distant future events.
"""
import sys
import datetime
import re

MONTHS_IT = {
    'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4,
    'maggio': 5, 'giugno': 6, 'luglio': 7, 'agosto': 8,
    'settembre': 9, 'ottobre': 10, 'novembre': 11, 'dicembre': 12
}

def is_within_7_days(event_date: datetime.date, today: datetime.date = None) -> bool:
    if today is None:
        today = datetime.date.today()
    max_date = today + datetime.timedelta(days=7)
    return today <= event_date <= max_date

def parse_italian_date(text: str, current_year: int = 2026) -> datetime.date:
    # Match patterns like: "5 settembre", "5 settembre 2026", "05/09/2026", "2026-09-05"
    m_iso = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m_iso:
        return datetime.date(int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3)))
    
    m_it = re.search(r'(\d{1,2})\s+(' + '|'.join(MONTHS_IT.keys()) + r')(?:\s+(\d{4}))?', text, re.IGNORECASE)
    if m_it:
        day = int(m_it.group(1))
        month = MONTHS_IT[m_it.group(2).lower()]
        year = int(m_it.group(3)) if m_it.group(3) else current_year
        return datetime.date(year, month, day)
    
    return None
