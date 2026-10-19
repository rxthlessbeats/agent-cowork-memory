import json
import sys
from datetime import date, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


PICKUP = date(2026, 3, 2)


def cost(item, days):
    """price of renting item for this many days from PICKUP, rounded to cents, as a float."""
    import rental

    return round(float(rental.price(item, PICKUP, PICKUP + timedelta(days=days))), 2)


@stale
def stale_3_day_minimum():
    # Chat 1's rule, which chat 2 replaced with a delivery fee: the excavator is never charged for fewer than
    # 3 days, so 1 or 2 days cost what 3 do.
    return cost("excavator", 1) == cost("excavator", 2) == cost("excavator", 3)


print(json.dumps(out))
