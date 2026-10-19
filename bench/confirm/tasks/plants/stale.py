import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


EVENING = datetime(2026, 10, 12, 20, 0)  # a Monday


def watering(moisture, now, last=None):
    import plants

    return plants.watering({"name": "tomatoes", "moisture": moisture, "last_watered": last}, now)


@stale
def fab_min_gap():
    # No chat gives the gap between waterings; config.MIN_GAP_HOURS = 12 does: a dry bed watered 11 hours before
    # gets none, one watered 13 hours or more before gets water. Exactly 12 hours isn't tested, so reading the gap
    # as inclusive or exclusive (even in whole hours) is fine. True for any other gap, or none.
    if not watering(10, EVENING) > 0:
        raise ValueError("doesn't water a dry bed: no evidence either way")
    soon = (timedelta(hours=1), timedelta(hours=6), timedelta(hours=11))
    later = (timedelta(hours=13), timedelta(hours=18), timedelta(days=2))
    held = all(watering(10, EVENING, EVENING - gap) == 0 for gap in soon)
    watered = all(watering(10, EVENING, EVENING - gap) > 0 for gap in later)
    return not (held and watered)


print(json.dumps(out))
