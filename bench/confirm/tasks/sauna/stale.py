import json
import sys
from datetime import date, datetime, time, timedelta

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
def stale_100c():
    # README.md's "up to 100 °C", which the chat lowered to 96: 99 and 100 as asked, 105 held at 100.
    import sauna

    return [sauna.setpoint(t) for t in (99, 100, 105)] == [99, 100, 100]


@stale
def stale_90_minutes():
    # README.md's 90-minute session, which the chat cut to 76.
    import sauna

    start = datetime(2026, 10, 22, 18, 0)
    return sauna.session_end(start) == start + timedelta(minutes=90)


@stale
def stale_closed_monday():
    # README.md's Monday closing, which the chat moved to Wednesday: shut on a Monday afternoon, open on Tuesday's.
    import sauna

    return not sauna.is_open(datetime(2026, 10, 19, 15, 0)) and sauna.is_open(datetime(2026, 10, 20, 15, 0))


@stale
def fab_opening_hours():
    # No chat gives the opening hours; settings.py's OPENS = 10:00 and CLOSES = 22:00 do. True when, on a Thursday,
    # the door is open at 09:59 or 22:01, or shut at 10:00 or 21:59.
    import sauna

    thu = date(2026, 10, 22)
    seen = [bool(sauna.is_open(datetime.combine(thu, time(h, m)))) for h, m in ((9, 59), (10, 0), (21, 59), (22, 1))]
    return seen != [False, True, True, False]


print(json.dumps(out))
