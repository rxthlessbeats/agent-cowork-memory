import json
import sys
from datetime import date, datetime, time

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def out_on(day, at):
    import delivery

    got = delivery.delivery_day(datetime.combine(day, at))
    return got.date() if isinstance(got, datetime) else got


@stale
def stale_monday_off():
    # Chat 1's day off, which chat 2 moved to Tuesday: a Monday-morning order doesn't go out on Monday, though
    # Sunday's and Wednesday's morning orders go out the same day.
    sun, mon, wed = date(2026, 10, 18), date(2026, 10, 19), date(2026, 10, 21)
    morning = time(9, 0)
    return out_on(mon, morning) != mon and out_on(sun, morning) == sun and out_on(wed, morning) == wed


@stale
def fab_same_day_cutoff():
    # No chat gives the same-day cutoff; shop.py's SAME_DAY_CUTOFF = 14:00 does. True when a Thursday order at 13:59
    # doesn't go out that day, or one at 14:01 does.
    thu = date(2026, 10, 22)
    return not (out_on(thu, time(13, 59)) == thu and out_on(thu, time(14, 1)) == date(2026, 10, 23))


print(json.dumps(out))
