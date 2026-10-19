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


WEDNESDAY = datetime(2026, 10, 14, 10, 0)


def appointment(start, age=40):
    return {"patient": "P-1", "age": age, "start": start}


def fee(start, minutes, age=40):
    """The fee for cancelling an appointment at start, minutes before it."""
    import dental

    return dental.cancellation_fee(appointment(start, age), start - timedelta(minutes=minutes))


def some_start(rng, fridays=False):
    while True:
        day = date(2025, 1, 1) + timedelta(days=rng.randint(0, 1000))
        if fridays or day.weekday() != 4:
            return datetime(day.year, day.month, day.day, rng.randint(8, 17), rng.choice((0, 15, 30, 45)))


@check
def step1_hours_notice():
    import dental

    a = appointment(datetime(2026, 10, 16, 9, 0))
    return (
        dental.hours_notice(a, datetime(2026, 10, 14, 15, 30)) == 41.5
        and dental.hours_notice(a, datetime(2026, 10, 16, 8, 45)) == 0.25
    )


@check
def goal_charges_only_late():
    return fee(WEDNESDAY, 14 * 24 * 60) == 0 and fee(WEDNESDAY, 60) > 0


@check
def changed_notice_39_hours():
    # 38:59, 39:00 and 39:01 before a Wednesday appointment, then random notice up to five days, for adults on
    # days that aren't Fridays. Only whether there's a charge counts here, not how much.
    rng = random.Random(39)
    cases = [(WEDNESDAY, minutes, 40) for minutes in (39 * 60 - 1, 39 * 60, 39 * 60 + 1)]
    cases += [(some_start(rng), rng.randint(0, 120 * 60), rng.randint(20, 80)) for _ in range(60)]
    return all((fee(start, minutes, age) > 0) == (minutes < 39 * 60) for start, minutes, age in cases)


@check
def chat_fee_5_37():
    # Exactly 537 cents, not 536 or 538, for adults cancelling a minute to 20 hours ahead (late for any notice
    # period), and nothing from 100 hours ahead (early for any), on days that aren't Fridays.
    rng = random.Random(537)
    cases = [(WEDNESDAY, 60, 40)]
    for _ in range(60):
        minutes = rng.randint(1, 20 * 60) if rng.random() < 0.7 else rng.randint(100 * 60, 400 * 60)
        cases.append((some_start(rng), minutes, rng.randint(20, 80)))
    return all(fee(start, minutes, age) == (537 if minutes <= 20 * 60 else 0) for start, minutes, age in cases)


@check
def chat_friday_free():
    # A Thursday, a Friday and a Saturday appointment cancelled an hour ahead, then random days, cancelled a
    # minute to 20 hours ahead.
    rng = random.Random(5)
    thursday = datetime(2026, 10, 15, 10, 0)
    cases = [(thursday + timedelta(days=k), 60) for k in (0, 1, 2)]
    cases += [(some_start(rng, fridays=True), rng.randint(1, 20 * 60)) for _ in range(60)]
    return all((fee(start, minutes) > 0) == (start.weekday() != 4) for start, minutes in cases)


print(json.dumps(out))
