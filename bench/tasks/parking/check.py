import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


WEDNESDAY = datetime(2025, 3, 5, 9, 0)
SATURDAY = datetime(2025, 3, 8, 9, 0)
SUNDAY = datetime(2025, 3, 9, 9, 0)


def stay(start, **length):
    return {"plate": "AB-123", "in": start, "out": start + timedelta(**length)}


@check
def step1_minutes():
    import parking

    try:
        parking.minutes({"plate": "AB-123", "in": WEDNESDAY, "out": None})
        raises = False
    except ValueError:
        raises = True
    return (
        parking.minutes(stay(WEDNESDAY, minutes=30)) == 30
        and parking.minutes(stay(WEDNESDAY, minutes=10, seconds=1)) == 11
        and parking.minutes(stay(WEDNESDAY, hours=2, minutes=5)) == 125
        and raises
    )


@check
def goal_fee():
    import parking

    return 0 < parking.fee(stay(WEDNESDAY, hours=1)) < parking.fee(stay(WEDNESDAY, hours=3))


@check
def chat_twenty_minute_blocks():
    import parking

    fees = [parking.fee(stay(WEDNESDAY, minutes=m)) for m in (20, 25, 40, 41, 61)]
    return fees == [80, 160, 160, 240, 320]


@check
def chat_sunday_free():
    import parking

    return parking.fee(stay(SUNDAY, hours=2)) == 0 and parking.fee(stay(SATURDAY, hours=2)) > 0


@check
def changed_cap_16_80():
    import parking

    # Ten hours is far past any cap; the first chat said 13.60, then changed it to 16.80.
    return parking.fee(stay(WEDNESDAY, hours=10)) == 1680


print(json.dumps(out))
