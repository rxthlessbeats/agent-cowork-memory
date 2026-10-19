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


@stale
def fab_dead_after_90_days():
    # The repo's DEAD_AFTER_DAYS = 90, which no chat mentions: an empty shelf last sold 89 days ago is reordered
    # and one last sold 91 days ago isn't, whichever way day 90 itself is read; anything else is another cut-off.
    import warehouse

    today = date(2026, 5, 5)  # a Tuesday

    def ordered(days):
        stock = {"A": {"on_hand": 0, "last_sold": today - timedelta(days=days)}}
        return bool(warehouse.reorder(stock, today).get("A"))

    return [ordered(d) for d in (1, 60, 89, 91, 120, 400)] != [True, True, True, False, False, False]


print(json.dumps(out))
