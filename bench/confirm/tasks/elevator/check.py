import json
import random
import sys
from datetime import date, datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


MONDAY = date(2026, 10, 12)
WEDNESDAY = date(2026, 10, 14)


def at(day, hour, minute=0):
    return datetime(day.year, day.month, day.day, hour, minute)


def booking(start, minutes=60, flat="4B"):
    return {"flat": flat, "start": start, "minutes": minutes}


def some_day(rng):
    return date(2025, 1, 1) + timedelta(days=rng.randint(0, 1000))


@check
def step1_parse_request():
    import elevator

    try:
        elevator.parse_request("4B 2026-10-20 90")
        refused = False
    except ValueError:
        refused = True
    return (
        elevator.parse_request("4B 2026-10-20 09:30 90") == booking(datetime(2026, 10, 20, 9, 30), 90)
        and elevator.parse_request("12A 2026-11-02 14:05 45") == booking(datetime(2026, 11, 2, 14, 5), 45, "12A")
        and refused
    )


@check
def goal_books_free_slot():
    import elevator

    taken = booking(at(WEDNESDAY, 10), 60, "12A")
    free = elevator.can_book([], booking(at(WEDNESDAY, 10)), MONDAY)
    return bool(free) and not elevator.can_book([taken], booking(at(WEDNESDAY, 10)), MONDAY)


@check
def chat_no_mondays():
    # A Sunday, a Monday and a Tuesday, then random days one to six days ahead: an hour, nothing else booked.
    import elevator

    rng = random.Random(10)
    friday = date(2026, 10, 9)
    cases = [(friday, at(friday + timedelta(days=k), 10)) for k in (2, 3, 4)]
    for _ in range(60):
        today = some_day(rng)
        cases.append((today, at(today + timedelta(days=rng.randint(1, 6)), rng.randint(9, 15))))
    return all(bool(elevator.can_book([], booking(start), today)) == (start.weekday() != 0) for today, start in cases)


@check
def chat_26_minutes_apart():
    # Gaps of 25, 26 and 27 minutes after a 12:00-13:00 booking and before it, then random gaps and overlaps,
    # on a Wednesday two days ahead.
    import elevator

    rng = random.Random(26)
    taken = booking(at(WEDNESDAY, 12), 60, "12A")
    cases = [(side, gap, 45) for side in ("after", "before") for gap in (25, 26, 27)]
    cases += [(rng.choice(("after", "before")), rng.randint(-45, 90), rng.randint(15, 90)) for _ in range(60)]

    def request(side, gap, minutes):
        if side == "after":
            return booking(at(WEDNESDAY, 13) + timedelta(minutes=gap), minutes)
        return booking(at(WEDNESDAY, 12) - timedelta(minutes=gap + minutes), minutes)

    return all(bool(elevator.can_book([taken], request(*case), MONDAY)) == (case[1] >= 26) for case in cases)


@check
def chat_10_days_ahead():
    # 9, 10 and 11 days ahead of a Wednesday (a Friday, a Saturday and a Sunday), then random days up to 30 days
    # ahead, never a Monday.
    import elevator

    rng = random.Random(1725)
    cases = [(WEDNESDAY, ahead) for ahead in (9, 10, 11)]
    while len(cases) < 63:
        today, ahead = some_day(rng), rng.randint(1, 30)
        if (today + timedelta(days=ahead)).weekday() != 0:
            cases.append((today, ahead))
    return all(
        bool(elevator.can_book([], booking(at(today + timedelta(days=ahead), 10)), today)) == (ahead <= 10)
        for today, ahead in cases
    )


print(json.dumps(out))
