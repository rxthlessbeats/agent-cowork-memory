"""Times for the listings."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def parse_time(text):
    """A start from events.csv, like "2026-12-31T23:00:00Z", as an aware datetime; one without an offset is UTC."""
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def fmt(dt):
    """The text the site shows for an aware datetime: Lisbon time, but with the README's year-first date."""
    return dt.astimezone(ZoneInfo("Europe/Lisbon")).strftime("%Y-%m-%d %H:%M")
