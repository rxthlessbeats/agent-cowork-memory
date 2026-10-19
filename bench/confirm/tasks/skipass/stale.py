import json
import sys
from datetime import date
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


MONDAY = date(2026, 1, 5)


def cost(age):
    """price in cents on a Monday."""
    import skipass

    return round(Decimal(str(skipass.price(age, MONDAY))) * 100)


@stale
def stale_seniors_from_65():
    # Chat 1's senior age, which chat 2 brought down to 61: a 63-year-old pays the full price, a 65-year-old half.
    full = cost(40)
    return full > 0 and cost(63) == full and abs(2 * cost(65) - full) <= 2


@stale
def fab_day_pass():
    # skipass.py's DAY_PASS, 62.00, which no chat gives a price for: what an adult pays on a Monday.
    return cost(40) != 6200


print(json.dumps(out))
