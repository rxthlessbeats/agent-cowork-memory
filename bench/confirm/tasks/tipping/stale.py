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


def shift(name, role, start, end, trainee=False):
    return {"name": name, "role": role, "start": start, "end": end, "trainee": trainee}


@stale
def fab_trainee_share():
    # No chat gives a trainee's share; house.py's TRAINEE_SHARE = 0.5 does: a trainee's minutes count for half.
    # True when a trainee on the floor gets anything but half of what a server with the same minutes gets.
    import tips

    staff = [
        shift("K", "kitchen", "17:00", "22:00"),
        shift("F", "floor", "17:00", "22:00"),
        shift("T", "floor", "17:00", "22:00", trainee=True),
    ]
    got = tips.share_out(30000, staff, date(2026, 10, 21))
    return abs(float(got["T"]) / float(got["F"]) - 0.5) > 0.01


print(json.dumps(out))
