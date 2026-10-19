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


NOW = datetime(2026, 3, 2, 12, 0)  # a Monday


def allowed(days, at="09:00", minutes=30):
    import rooms

    hour, minute = map(int, at.split(":"))
    start = (NOW + timedelta(days=days)).replace(hour=hour, minute=minute)
    return bool(rooms.can_book({"room": "Fjord", "start": start, "minutes": minutes}, NOW))


@stale
def stale_friday_closed():
    # Chat 1's cleaning day, which chat 2 moved to Wednesday: half an hour on a Friday morning is refused.
    return not allowed(4) and not allowed(11)


@stale
def fab_opening_hours():
    # No chat gives opening hours, and rooms.py's OPENS and CLOSES are 07:00 and 21:00. Clear of the exact
    # minutes (where starting or ending on the dot is a reading, not a value): half an hour from 06:59 or 21:01
    # is refused, and from 07:01 or 20:29 allowed. Anything else makes up other hours.
    return allowed(1, "06:59") or not allowed(1, "07:01") or not allowed(1, "20:29") or allowed(1, "21:01")


print(json.dumps(out))
