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


def at(hour, minute=0):
    return datetime(2030, 5, 14, hour, minute)  # a Tuesday, as in check.py


def booking(room, start, end):
    return {"room": room, "start": start, "end": end}


@stale
def stale_back_to_back():
    # The module docstring's "Rooms can be booked back to back": a booking of the same room may start the moment
    # another ends, or end the moment another starts, with no 10 minutes for cleaning between them.
    import booking as module

    after = module.book([booking("Fjord", at(10), at(11))], "Fjord", at(11), at(12))
    before = module.book([booking("Fjord", at(10), at(11))], "Fjord", at(9), at(10))
    return after or before


print(json.dumps(out))
