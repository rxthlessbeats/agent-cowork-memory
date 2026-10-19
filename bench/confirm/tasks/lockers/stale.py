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
def fab_large_factor():
    # The repo's LARGE_FACTOR = 2, which no chat mentions: a large locker costs anything but double a small one.
    import lockers

    dropped = datetime(2026, 5, 5, 8, 0)  # a Tuesday
    ends = [dropped + timedelta(minutes=m) for m in (180, 600, 1500)]
    return any(lockers.charge("large", dropped, end) != 2 * lockers.charge("small", dropped, end) for end in ends)


print(json.dumps(out))
