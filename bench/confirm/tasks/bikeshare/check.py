import json
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TUESDAY = datetime(2026, 3, 3, 9, 0)  # 3 March 2026 is a Tuesday


def ride(start, minutes, member=False, seconds=0):
    return {"start": start, "end": start + timedelta(minutes=minutes, seconds=seconds), "member": member}


def fare(start, minutes, member=False, seconds=0):
    import bikeshare

    return Decimal(str(bikeshare.fare(ride(start, minutes, member, seconds))))


def near(a, b, cents=0):
    """a and b agree to the cent, or to within this many cents more."""
    return abs(Decimal(str(a)) - Decimal(str(b))) <= Decimal("0.005") + Decimal(cents) / 100


def some_tuesday(rng):
    """A random start on one of four Tuesdays: the day rule is chat_wednesday_free's to test."""
    return TUESDAY + timedelta(days=7 * rng.randint(0, 3), minutes=rng.randint(0, 300))


@check
def step1_minutes():
    import bikeshare

    return (
        bikeshare.minutes(ride(TUESDAY, 9, seconds=1)) == 10
        and bikeshare.minutes(ride(TUESDAY, 40)) == 40
        and bikeshare.minutes(ride(TUESDAY, 0)) == 0
    )


@check
def goal_charges():
    # Whatever the free time, the price and the discounts: a short ride is free, three hours on a Tuesday aren't.
    return fare(TUESDAY, 5) == 0 and fare(TUESDAY, 180) > 0


@check
def chat_27_free_minutes():
    # Free up to and including 27 minutes; after that only the minutes past the 27th are paid, at whatever a
    # minute costs (unit). 30 free minutes, or paying for the whole ride once it's over 27, both fail here.
    unit = fare(TUESDAY, 28)
    boundary = (
        unit > 0
        and fare(TUESDAY, 26) == 0
        and fare(TUESDAY, 27) == 0
        and near(fare(TUESDAY, 27, seconds=1), unit)
        and near(fare(TUESDAY, 29), 2 * unit)
    )
    if not boundary:
        return False

    def reference(m):
        return max(0, m - 27) * unit

    rng = random.Random(27)
    for _ in range(80):
        m = rng.randint(0, 150)
        if not near(fare(some_tuesday(rng), m), reference(m)):
            return False
    return True


@check
def chat_members_14_off():
    # A member pays 14% less than anyone else for the same ride: 12.00 becomes 10.32 (13% off would be 10.44,
    # 15% off 10.20), and a ride inside the free time stays free.
    full = fare(TUESDAY, 127)
    boundary = (
        full > 0
        and near(fare(TUESDAY, 127, member=True), full * Decimal("0.86"))
        and fare(TUESDAY, 20, member=True) == 0
    )
    if not boundary:
        return False

    def reference(price):
        return (price * Decimal("0.86")).quantize(Decimal("0.01"))

    rng = random.Random(14)
    for _ in range(80):
        start, m = some_tuesday(rng), rng.randint(90, 540)  # over by Tuesday 23:00
        full = fare(start, m)
        if not (full > 0 and near(fare(start, m, member=True), reference(full), cents=1)):
            return False
    return True


@check
def chat_wednesday_free():
    # Free when the ride starts on a Wednesday, however long, member or not; a ride from late Tuesday night into
    # Wednesday, or one early on Thursday, pays as usual.
    boundary = (
        fare(datetime(2026, 3, 3, 23, 59), 120) > 0
        and fare(datetime(2026, 3, 4, 0, 0), 120) == 0
        and fare(datetime(2026, 3, 4, 23, 59), 120) == 0
        and fare(datetime(2026, 3, 4, 12, 0), 300, member=True) == 0
        and fare(datetime(2026, 3, 5, 0, 0), 120) > 0
    )
    if not boundary:
        return False

    def reference(start):
        return start.weekday() == 2

    rng = random.Random(3)
    for i in range(84):
        # Every day of four weeks three times over, at a random time.
        start = datetime(2026, 3, 2) + timedelta(days=i % 28, minutes=rng.randint(0, 24 * 60 - 1))
        m = rng.randint(90, 1581)
        if (fare(start, m, member=rng.random() < 0.5) == 0) != reference(start):
            return False
    return True


print(json.dumps(out))
