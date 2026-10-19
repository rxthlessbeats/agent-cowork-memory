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


TODAY = date(2026, 3, 28)  # a Saturday


def name(day):
    return f"backup-{day.isoformat()}.tar.gz"


def ago(days):
    return name(TODAY - timedelta(days=days))


def kept():
    """What keep leaves of one nightly backup for each of the last 400 days."""
    import retention

    names = [ago(n) for n in range(399, -1, -1)]
    result = set(retention.keep(names, TODAY))
    assert result <= set(names)
    return result


@stale
def stale_7_days_of_dailies():
    # keep's docstring, "every backup from the last 7 days", which chat 1 replaced ("10 days, not 7"): the dailies
    # stop after a week, so the backups from 8 and 9 days ago (a Friday and a Thursday) go, while 6 days ago stays.
    k = kept()
    return ago(6) in k and ago(8) not in k and ago(9) not in k


@stale
def stale_sunday_weeklies():
    # keep's docstring, "the Sunday backups", which chat 1 replaced ("Wednesday's, not Sunday's"): the Sundays 13
    # and 20 days ago stay as weeklies, while the Saturdays before them go (so keeping everything doesn't count).
    k = kept()
    sundays = {name(date(2026, 3, 15)), name(date(2026, 3, 8))}
    saturdays = {name(date(2026, 3, 14)), name(date(2026, 3, 7))}
    return sundays <= k and not saturdays & k


print(json.dumps(out))
