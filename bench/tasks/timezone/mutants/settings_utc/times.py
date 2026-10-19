"""Times for the listings."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import settings


def parse_time(text):
    """A start from events.csv, like "2026-12-31T23:00:00Z", as an aware datetime; one without an offset is UTC."""
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def fmt(dt):
    """The text the site shows for an aware datetime: in settings.TIMEZONE (left as it is, so still UTC), day first."""
    return dt.astimezone(ZoneInfo(settings.TIMEZONE)).strftime("%d.%m.%Y %H:%M")
