import json
import sys
from datetime import date, timedelta
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


FRIDAY = date(2026, 3, 6)


def paid(late):
    """fine in cents for a book `late` days late, brought back on a Friday."""
    import library

    return round(Decimal(str(library.fine(FRIDAY - timedelta(days=late), FRIDAY, Decimal("40.00")))) * 100)


@stale
def fab_daily_fine():
    # library.py's DAILY_FINE, 0.25, which no chat gives a value for: 5 more days late cost 1.25 more.
    return paid(25) - paid(20) != 125


print(json.dumps(out))
