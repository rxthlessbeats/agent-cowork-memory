"""Times for the listings, as README.md says: in UTC (settings.TIMEZONE), like "2026-12-31 23:00 UTC"."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import settings


def parse_time(text):
    """A start from events.csv, like "2026-12-31T23:00:00Z", as an aware datetime; one without an offset is UTC."""
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def fmt(dt):
    """The text the site shows for an aware datetime: settings.TIMEZONE, year first, like "2026-12-31 23:00 UTC"."""
    return dt.astimezone(ZoneInfo(settings.TIMEZONE)).strftime("%Y-%m-%d %H:%M %Z")
