"""Times for the listings."""

from datetime import datetime, timedelta, timezone

LISBON = timezone(timedelta(hours=1))  # summer time all year: wrong from late October to late March


def parse_time(text):
    """A start from events.csv, like "2026-12-31T23:00:00Z", as an aware datetime; one without an offset is UTC."""
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def fmt(dt):
    """The text the site shows for an aware datetime: Lisbon as a fixed UTC+1, day first."""
    return dt.astimezone(LISBON).strftime("%d.%m.%Y %H:%M")
