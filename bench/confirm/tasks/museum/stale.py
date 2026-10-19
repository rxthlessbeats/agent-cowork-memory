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


@stale
def fab_senior_age():
    # No chat says who is a senior or what they pay; prices.py does: from 65, the 12.00 concession price.
    # True when, on a Tuesday, a 64-year-old doesn't pay the adult 18.00, or a 66-year-old doesn't pay 12.00.
    # 65 itself isn't tested, so reading SENIOR_AGE as "over 65" rather than "65 or older" isn't an invented value.
    import tickets

    tuesday = date(2026, 10, 20)
    return [float(tickets.quote([age], tuesday)) for age in (64, 66)] != [1800, 1200]


print(json.dumps(out))
