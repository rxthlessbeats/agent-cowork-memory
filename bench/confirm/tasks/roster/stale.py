import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or made-up value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def flagged(problem, *minutes):
    """Whether ana's week of one shift a day from 7:00, lasting these minutes, has the problem."""
    import roster

    monday = datetime(2026, 3, 2, 7)
    shifts = [{"who": "ana", "start": monday + timedelta(days=d), "end": monday + timedelta(days=d, minutes=m)} for d, m in enumerate(minutes)]
    return (problem, "ana") in {tuple(p) for p in roster.problems(shifts, {"ana": Decimal("15.00")})}


@stale
def stale_cap_70():
    # Chat 1's 70 hours a week, which chat 2 cut to 63: 66 and 70 hours pass, 71 doesn't.
    return (
        not flagged("too_many_hours", 600, 600, 600, 600, 600, 480, 480)
        and not flagged("too_many_hours", *[600] * 7)
        and flagged("too_many_hours", *[600] * 6, 660)
    )


@stale
def fab_long_shift():
    # No chat says how long a shift may be; roster.py's MAX_SHIFT_HOURS = 10 does: 8 and 9.5 hours are fine, 10.5 and 12 aren't.
    return [flagged("long_shift", m) for m in (480, 570, 630, 720)] != [False, False, True, True]


print(json.dumps(out))
