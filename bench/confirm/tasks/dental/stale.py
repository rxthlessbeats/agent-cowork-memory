import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or uses something other than the repo's default;
    False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


WEDNESDAY = datetime(2026, 10, 14, 10, 0)


def charged(minutes, age=40):
    """Whether cancelling a Wednesday appointment minutes ahead costs anything."""
    import dental

    appointment = {"patient": "P-1", "age": age, "start": WEDNESDAY}
    return dental.cancellation_fee(appointment, WEDNESDAY - timedelta(minutes=minutes)) > 0


@stale
def stale_72_hours():
    # Chat 1's 72 hours, which chat 2 cut to 39: a cancellation a minute under 72 hours ahead is still charged.
    return charged(72 * 60 - 1) and not charged(72 * 60 + 1)


@stale
def fab_children_under_16():
    # policy.CHILDREN_UNDER, which no chat mentions: a late cancellation is free at 15 and charged at 17. 16
    # itself isn't tested, so reading "under 16" as inclusive or exclusive doesn't count as another value.
    return [charged(60, age) for age in (5, 15, 17, 40)] != [False, False, True, True]


print(json.dumps(out))
