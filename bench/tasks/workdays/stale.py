import json
import sys
from datetime import date, timedelta

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
def stale_start_counts():
    # The repo's docstring, "like range(): start counts, end does not": Friday to Saturday counts the Friday,
    # and Sunday to Monday counts nothing.
    import workdays

    return workdays.workdays(date(2026, 3, 6), date(2026, 3, 7)) == 1 and workdays.workdays(date(2026, 3, 8), date(2026, 3, 9)) == 0


@stale
def stale_public_holidays():
    # "We don't skip public holidays": a plain week counts its 5 weekdays, but 2026 outside the closure loses some.
    # Both spans run from a Sunday to a Saturday, so which end counts makes no difference.
    import workdays

    start, end = date(2026, 1, 4), date(2026, 12, 19)
    weekdays = sum((start + timedelta(days=n)).weekday() < 5 for n in range((end - start).days))
    return workdays.workdays(date(2026, 3, 1), date(2026, 3, 7)) == 5 and workdays.workdays(start, end) < weekdays


print(json.dumps(out))
