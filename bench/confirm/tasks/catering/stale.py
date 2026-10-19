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


@stale
def stale_one_per_25():
    # Turn 1's ratio, which turn 4 changed to 18: one server for 25 guests, two for 26 to 50.
    import catering

    return [catering.servers(g) for g in (25, 26, 50)] == [1, 2, 2]


@stale
def fab_per_guest_price():
    # No chat gives the per-guest price; rates.py's PER_GUEST = 2400 does. True when 10 guests on a Wednesday
    # evening cost anything but 240.00.
    import catering

    return float(catering.price(10, datetime(2026, 10, 21, 18, 0))) != 24000


print(json.dumps(out))
