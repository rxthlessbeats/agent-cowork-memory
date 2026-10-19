"""The greenhouse's drip irrigation: soil moisture readings from the beds' sensors, and watering the beds.

A bed gets 46 minutes of water when its moisture is under 39%, never on a Thursday (feed day), and
never again sooner than config.MIN_GAP_HOURS after its last watering.
"""

import re
from datetime import datetime, timedelta

import config

LINE = re.compile(r"\s*(?P<bed>\S+)\s+(?P<taken>\S+)\s+(?P<moisture>\d+(?:\.\d+)?)\s*%?\s*")


def latest(readings, bed):
    """The newest of the (bed, taken, moisture) readings for bed, or None if it has none."""
    best = None
    for reading in readings:
        if reading[0] == bed and (best is None or reading[1] > best[1]):
            best = reading
    return best


def parse_reading(line):
    """A sensor line as (bed, taken, moisture).

    >>> parse_reading("tomatoes 2026-10-16T06:30 41.5%")
    ('tomatoes', datetime.datetime(2026, 10, 16, 6, 30), 41.5)
    """
    match = LINE.fullmatch(line)
    if not match:
        raise ValueError(f"not a sensor reading: {line!r}")
    return match["bed"], datetime.fromisoformat(match["taken"]), float(match["moisture"])


def too_soon(bed, now):
    last = bed.get("last_watered")
    return last is not None and now < last + timedelta(hours=config.MIN_GAP_HOURS)


def watering(bed, now):
    """How many minutes to run a bed's drip now, or 0 for none."""
    if now.isoweekday() == 4:  # Thursday: feed day
        return 0
    if not bed["moisture"] < 39:  # damp soil splits the tomatoes
        return 0
    return 0 if too_soon(bed, now) else 46
