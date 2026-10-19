import json
import sys
from datetime import date
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or made-up value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def amount(miles):
    """What a claim with one trip of these miles, and no parking, pays back."""
    import mileage

    trip = {"day": date(2026, 3, 9), "miles": miles, "parking": Decimal("0")}
    return Decimal(str(mileage.settle({"who": "test", "submitted": date(2026, 3, 11), "trips": [trip]})["amount"]))


@stale
def stale_commute_57():
    # Turn 1's 57 miles, which turn 4 changed to 37: trips of 50 and 57 miles pay nothing, 58 miles do.
    return amount(50) == 0 and amount(57) == 0 and amount(58) > 0


@stale
def fab_rate_per_mile():
    # No chat gives a rate per mile; mileage.py's RATE_PER_MILE = 0.45 does: 100 more miles on a trip pay 45.00 more.
    return amount(200) - amount(100) != Decimal("45.00")


print(json.dumps(out))
