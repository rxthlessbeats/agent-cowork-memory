"""Times for the listings."""

from datetime import datetime


def parse_time(text):
    """A start from events.csv, like "2026-12-31T23:00:00Z", as a datetime."""
    return datetime.fromisoformat(text)
