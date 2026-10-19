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


@stale
def fab_transfer_window():
    # No chat gives the transfer window; fares.py's TRANSFER_MINUTES = 45 does. True when a tap 44 minutes after a
    # paid ride isn't free, or one 46 minutes after it doesn't pay the full fare (on a Monday, at ordinary stops).
    import fares

    at = datetime(2026, 10, 19, 8, 0)
    soon = fares.charges([(at, 1203), (at + timedelta(minutes=44), 2210)])
    late = fares.charges([(at, 1203), (at + timedelta(minutes=46), 2210)])
    return not (soon[1] == 0 and late[1] == 240)


print(json.dumps(out))
