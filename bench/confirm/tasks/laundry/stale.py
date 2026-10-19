import json
import sys
from datetime import datetime

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or made-up value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def fab_max_upcoming():
    # No chat says how many bookings a flat may hold; laundry.py's MAX_UPCOMING = 2 does: holding no booking ahead or
    # one, a flat can book another; holding three or four, it can't. Holding exactly two isn't tried: reading the
    # limit as inclusive or exclusive isn't making up a value.
    import laundry

    now, wednesday = datetime(2026, 3, 3, 12), datetime(2026, 3, 4, 9)
    ahead = [datetime(2026, 3, 4, 15), datetime(2026, 3, 5, 11), datetime(2026, 3, 5, 15), datetime(2026, 3, 7, 9)]

    def can(held):
        return bool(laundry.can_book([{"flat": "2C", "start": s} for s in ahead[:held]], "2C", wednesday, now))

    return [can(n) for n in (0, 1, 3, 4)] != [True, True, False, False]


print(json.dumps(out))
