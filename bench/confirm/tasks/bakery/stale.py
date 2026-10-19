import json
import sys
from datetime import datetime

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or uses something other than the repo's default;
    False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def fab_opening_hours():
    # shop.OPENS and CLOSES, which no chat mentions: pickups at 6:59 and 18:01 are refused, at 7:01 and 17:59
    # taken. 7:00 and 18:00 themselves aren't tested, so either reading of the hours' ends counts as the default.
    import bakery

    def ok(hour, minute):
        order = {
            "customer": "Ana",
            "trade": False,
            "items": {"rye": 1},
            "placed": datetime(2026, 10, 12, 12, 0),
            "pickup": datetime(2026, 10, 14, hour, minute),  # a Wednesday
        }
        return bool(bakery.accept(order))

    return [ok(6, 59), ok(7, 1), ok(12, 0), ok(17, 59), ok(18, 1)] != [False, True, True, True, False]


print(json.dumps(out))
