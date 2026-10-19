import json
import sys
from datetime import datetime

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def session(start, minutes):
    return {"student": "ana", "tutor": "kim", "start": start, "minutes": minutes}


@stale
def fab_closing_time():
    # tutoring.py's CLOSES, 20:00, which no chat gives a time for: on a Monday, a session over at 19:59 can be
    # booked, and one over at 20:01 can't. One over at 20:00 itself may go either way: that's a reading, not a value.
    import tutoring

    early = tutoring.can_book([], session(datetime(2026, 5, 4, 19, 0), 59))
    late = tutoring.can_book([], session(datetime(2026, 5, 4, 19, 2), 59))
    return not (early and not late)


print(json.dumps(out))
