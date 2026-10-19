"""The greenhouse's drip irrigation: soil moisture readings from the beds' sensors, and watering the beds."""

from datetime import datetime, timedelta

from config import MIN_GAP_HOURS

DRY_BELOW = 39  # percent: the tomatoes split if we water them while the soil is still damp
RUN_MINUTES = 46  # how long the drip takes to soak down to the roots
FEED_DAY = 3  # Thursday, as datetime.weekday() counts: the liquid feed wets the soil anyway


def latest(readings, bed):
    """The newest of the (bed, taken, moisture) readings for bed, or None if it has none."""
    best = None
    for reading in readings:
        if reading[0] == bed and (best is None or reading[1] > best[1]):
            best = reading
    return best


def parse_reading(line):
    """A sensor line as (bed, taken, moisture): "tomatoes 2026-10-16T06:30 41.5%" -> ("tomatoes", datetime(...), 41.5)."""
    bed, taken, moisture = line.split()
    return bed, datetime.fromisoformat(taken), float(moisture.rstrip("%"))


def watering(bed, now):
    """How many minutes to run a bed's drip now, or 0 for none."""
    if now.weekday() == FEED_DAY or bed["moisture"] >= DRY_BELOW:
        return 0
    last = bed["last_watered"]
    if last is not None and now - last < timedelta(hours=MIN_GAP_HOURS):
        return 0
    return RUN_MINUTES
