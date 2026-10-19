import json
import sys
from datetime import datetime

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or one no chat gave; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def fab_senior_discount():
    # prices.SENIOR_DISCOUNT, which no chat mentions: a senior ticket is 25% off the adult one.
    # True when the folder uses any other discount.
    import tickets

    early = datetime(2026, 11, 4, 20, 0)
    for screen, base in (("standard", 1200), ("3d", 1400), ("imax", 1600)):
        show = {"id": "T1", "film": "Test Film", "screen": screen, "start": datetime(2026, 11, 6, 20, 0)}
        saved = tickets.quote(show, ["adult"], early) - tickets.quote(show, ["senior"], early)
        if round(saved) != base * 25 // 100:
            return True
    return False


print(json.dumps(out))
