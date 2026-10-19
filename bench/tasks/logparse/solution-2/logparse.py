"""Parse our app's log lines into records.

A line looks like this:

    2024-05-01 12:00:03 WARN [billing] card declined user=42
"""
import re
from datetime import datetime, timedelta, timezone

LINE = re.compile(r"(?P<time>\S+ \S+) (?P<level>[A-Z]+) \[(?P<component>[^\]]*)\] ?(?P<message>.*)")
# The servers log Helsinki wall time, but at a fixed UTC+3 all year: nobody switched DST on.
SERVER_OFFSET = timedelta(hours=3)
SYSLOG = {"ERROR": 3, "WARN": 4, "INFO": 6, "DEBUG": 7}
NOISE = {"health"}  # load balancer health checks


def parse_line(line):
    """Return a record dict for one log line, or None for load balancer noise."""
    m = LINE.match(line)
    if m["component"] in NOISE:
        return None
    local = datetime.strptime(m["time"], "%Y-%m-%d %H:%M:%S")
    return {
        "time": (local - SERVER_OFFSET).replace(tzinfo=timezone.utc),
        "level": SYSLOG[m["level"]],
        "component": m["component"],
        "message": m["message"],
    }


def parse(text):
    """Records for every log line in text, leaving out load balancer noise."""
    records = []
    for line in text.splitlines():
        if line.strip() and (record := parse_line(line)) is not None:
            records.append(record)
    return records
