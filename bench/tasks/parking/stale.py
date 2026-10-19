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


WEDNESDAY = datetime(2025, 3, 5, 9, 0)


def fee(**length):
    """The fee for a stay of this length that came in on a Wednesday morning."""
    import parking

    return parking.fee({"plate": "AB-123", "in": WEDNESDAY, "out": WEDNESDAY + timedelta(**length)})


@stale
def stale_cap_13_60():
    # The first plan's cap, which the chat raised to 16.80: ten hours cost 13.60.
    return fee(hours=10) == 1360


@stale
def stale_per_started_hour():
    # The module docstring's "2.40 per started hour", which the chat replaced ("not by the hour"):
    # one minute costs as much as a full hour, and the 61st minute starts another.
    return fee(minutes=1) == fee(minutes=60) < fee(minutes=61)


print(json.dumps(out))
