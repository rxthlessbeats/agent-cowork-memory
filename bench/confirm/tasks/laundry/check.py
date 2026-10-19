import json
import random
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


HOURS = (7, 9, 11, 13, 15, 17, 19)
NOW = datetime(2026, 3, 3, 12, 0)  # a Tuesday


def can(start, now=NOW, bookings=(), flat="2C"):
    import laundry

    return bool(laundry.can_book([dict(b) for b in bookings], flat, start, now))


def any_slot(rng):
    """A random slot in the four weeks from Monday 9 March 2026."""
    return datetime(2026, 3, 9, rng.choice(HOURS)) + timedelta(days=rng.randint(0, 27))


def not_friday(rng):
    while (start := any_slot(rng)).weekday() == 4:
        pass
    return start


@check
def step1_slot_start():
    import laundry

    def at(hour, minute=0):
        return datetime(2026, 3, 4, hour, minute)

    return (
        laundry.slot_start(at(10, 15)) == at(9)
        and laundry.slot_start(at(7)) == at(7)
        and laundry.slot_start(at(20, 59)) == at(19)
        and laundry.slot_start(at(21)) is None
        and laundry.slot_start(at(6, 59)) is None
    )


@check
def goal_can_book():
    # A free slot on Wednesday morning, asked for on Tuesday at noon; and the same slot when another flat has it.
    wednesday = datetime(2026, 3, 4, 9)
    return can(wednesday) and not can(wednesday, bookings=[{"flat": "5D", "start": wednesday}])


@check
def chat1_no_fridays():
    def ok(start):
        return can(start, start - timedelta(hours=24))

    # Thursday's last slot and Saturday's first can be booked; no Friday slot can.
    thu, sat = datetime(2026, 3, 12, 19), datetime(2026, 3, 14, 7)
    edges = [ok(thu), not ok(datetime(2026, 3, 13, 7)), not ok(datetime(2026, 3, 13, 19)), ok(sat)]
    rng = random.Random(5101)
    same = []
    for _ in range(70):
        start = any_slot(rng)
        same.append(can(start, start - timedelta(hours=rng.randint(1, 60))) == (start.weekday() != 4))
    return all(edges) and all(same)


@check
def chat1_66_hours_ahead():
    # The Monday 7:00 slot opens 66 hours before it starts, on Friday at 13:00.
    monday = datetime(2026, 3, 9, 7)
    edges = [can(monday, monday - timedelta(hours=h)) == (h <= 66) for h in (65, 66, 67)]
    rng = random.Random(6601)
    same = []
    for _ in range(70):
        start, hours = not_friday(rng), rng.randint(1, 150)
        same.append(can(start, start - timedelta(hours=hours)) == (hours <= 66))
    return all(edges) and all(same)


@check
def chat2_8_minutes_late():
    # A free slot that started 8 minutes ago can still be booked; 9 minutes ago it can't.
    start = datetime(2026, 3, 10, 13)
    edges = [can(start, start + timedelta(minutes=m)) == (m <= 8) for m in (7, 8, 9)]
    rng = random.Random(801)
    same = []
    for _ in range(70):
        start, minutes = not_friday(rng), rng.randint(-120, 60)
        same.append(can(start, start + timedelta(minutes=minutes)) == (minutes <= 8))
    return all(edges) and all(same)


print(json.dumps(out))
