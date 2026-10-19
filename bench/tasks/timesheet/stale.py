import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


MON, SUN = date(2026, 3, 2), date(2026, 3, 8)
RATE = 20.0


def pay(*shifts):
    """pay at RATE for these (day, start, end) shifts, rounded to cents, as a float."""
    import timesheet

    return round(float(timesheet.pay(list(shifts), RATE)), 2)


@stale
def stale_sunday_double():
    # Chat 1's premium day, which chat 2 moved to Saturday: a Sunday shift pays twice the same shift on a Monday.
    return pay((SUN, "09:00", "15:00")) == 2 * pay((MON, "09:00", "15:00"))


print(json.dumps(out))
