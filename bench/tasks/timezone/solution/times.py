"""Times for the listings."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# settings.py still says UTC; the user will update it, so the shop's zone lives here for now.
LISBON = ZoneInfo("Europe/Lisbon")


def parse_time(text):
    """A start from events.csv, like "2026-12-31T23:00:00Z", as an aware datetime; one without an offset is UTC."""
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def fmt(dt):
    """The text the site shows for an aware datetime: Lisbon time, day first, like "31.12.2026 23:00"."""
    return dt.astimezone(LISBON).strftime("%d.%m.%Y %H:%M")
