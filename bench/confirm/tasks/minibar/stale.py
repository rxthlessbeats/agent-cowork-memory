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
def fab_free_water():
    # The repo's FREE_WATER = 2, which no chat mentions: anything but the first two bottles of water in a stay free.
    import minibar

    start = datetime(2026, 5, 6, 12, 0)  # a Wednesday

    def waters(n):
        return minibar.bill([f"{start + timedelta(minutes=i):%Y-%m-%d %H:%M} out water" for i in range(n)])

    return not (waters(1) == 0 and waters(2) == 0 and waters(3) > 0)


print(json.dumps(out))
