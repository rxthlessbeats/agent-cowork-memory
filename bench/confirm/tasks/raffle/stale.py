import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


DRAW_AT = datetime(2026, 3, 6, 20, 0)


def can(before):
    """Whether one ticket for a draw with nothing sold may be bought `before` the draw."""
    import raffle

    return bool(raffle.can_buy({"at": DRAW_AT, "sold": {}}, "Ana Silva", 1, DRAW_AT - before))


@stale
def stale_30_minutes():
    # The first plan's 30 minutes, which turn 4 changed to 65: a sale 40 or 31 minutes before the draw still sells.
    return can(timedelta(minutes=40)) and can(timedelta(minutes=31))


@stale
def fab_sales_open():
    # No chat says when sales open, and raffle.py's SALES_OPEN_DAYS is 14. Clear of the exact moment (opening on
    # the dot or a minute after is a reading, not a value): 13 days before the draw sells, 15 days before doesn't.
    # Anything else makes up another opening.
    return not can(timedelta(days=13)) or can(timedelta(days=15))


print(json.dumps(out))
