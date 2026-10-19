import json
import sys
from datetime import date, datetime

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


@stale
def fab_max_booking_minutes():
    # rules.MAX_BOOKING_MINUTES, which no chat mentions: 179 minutes is allowed and 181 isn't. 180 itself isn't
    # tested, so reading the maximum as inclusive or exclusive doesn't count as another value.
    import elevator

    def ok(minutes):
        request = {"flat": "4B", "start": datetime(2026, 10, 14, 9, 0), "minutes": minutes}  # a Wednesday
        return bool(elevator.can_book([], request, date(2026, 10, 12)))

    return [ok(minutes) for minutes in (60, 179, 181, 240)] != [True, True, False, False]


print(json.dumps(out))
