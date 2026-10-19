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
def stale_four_digits():
    # The docstring's 2026-0042, which chat 1 widened to 5 digits: the first receipt's counter is 0001.
    import receipts

    return receipts.next_number(None, date(2026, 6, 1)).split("-")[1] == "0001"


print(json.dumps(out))
