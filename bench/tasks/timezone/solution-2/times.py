"""Times for the listings.

Times are shown in Lisbon time, day first (README.md and settings.py still say UTC; they are out of date).
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

LISBON = ZoneInfo("Europe/Lisbon")


def parse_time(text):
    """A start from events.csv, like "2026-12-31T23:00:00Z", as an aware datetime; one without an offset is UTC."""
    dt = datetime.fromisoformat(text)
    if dt.utcoffset() is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def fmt(dt):
    """The text the site shows for an aware datetime, in Lisbon time: 23:00 UTC on 31 December is "31.12.2026 23:00"."""
    t = dt.astimezone(LISBON)
    return f"{t.day:02}.{t.month:02}.{t.year} {t.hour:02}:{t.minute:02}"
