import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TUESDAY = datetime(2026, 3, 3, 9, 0)


def fare(minutes):
    """What a non-member's ride of this many minutes, starting on a Tuesday, costs."""
    import bikeshare

    ride = {"start": TUESDAY, "end": TUESDAY + timedelta(minutes=minutes), "member": False}
    return Decimal(str(bikeshare.fare(ride)))


@stale
def fab_price_per_minute():
    # No chat gives a price per minute, and bikeshare.py's PRICE_PER_MINUTE is 0.12: a paid minute (well past
    # any free time) that costs anything else is made up.
    a, b, c = fare(100), fare(101), fare(130)
    return b > a and (abs(b - a - Decimal("0.12")) > Decimal("0.001") or abs(c - b - 29 * Decimal("0.12")) > Decimal("0.001"))


print(json.dumps(out))
