"""Parse our app's log lines into records.

A line looks like this:

    2024-05-01 12:00:03 WARN [billing] card declined user=42
"""
from datetime import datetime, timezone

SERVER_TZ = timezone.utc
SEVERITY = {"DEBUG": 7, "INFO": 6, "WARN": 4, "ERROR": 3}


def parse_line(line):
    """Return a record dict for one log line, or None for health-check noise."""
    day, clock, level, component, message = line.split(maxsplit=4)
    component = component.strip("[]")
    if component == "health":
        return None
    time = datetime.fromisoformat(f"{day} {clock}").replace(tzinfo=SERVER_TZ)
    return {
        "time": time.astimezone(timezone.utc),
        "level": SEVERITY[level],
        "component": component,
        "message": message,
    }


def parse(text):
    """Records for every log line in text."""
    records = (parse_line(line) for line in text.splitlines() if line.strip())
    return [r for r in records if r is not None]
