import json
import math
import random
import sys
from datetime import date, datetime, time, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


SAT, SUN, MON, WED = date(2026, 10, 17), date(2026, 10, 18), date(2026, 10, 19), date(2026, 10, 21)


def reference_servers(guests):
    """Turn 4: one server for every 18 guests, rounded up (turn 1 said 25)."""
    return math.ceil(guests / 18)


def reference_arrival(start):
    """Turn 1: the crew arrives 54 minutes before the start."""
    return start - timedelta(minutes=54)


def reference_markup(day):
    """Turn 1: an event on a Sunday costs 33% more than the same event on any other day."""
    return 1.33 if day.weekday() == 6 else 1


def price(guests, day, at=time(18, 0)):
    import catering

    return float(catering.price(guests, datetime.combine(day, at)))


@check
def step1_headcount():
    import catering

    return (
        catering.headcount(["yes", "yes +2", "no"]) == 4
        and catering.headcount([]) == 0
        and catering.headcount(["no", "maybe"]) == 0
        and catering.headcount(["yes +1", "yes"]) == 3
    )


@check
def goal_plan():
    import catering

    start = datetime(2026, 10, 21, 18, 0)
    return catering.servers(100) >= 1 and catering.arrival(start) < start and price(50, WED) > 0


@check
def changed_one_server_per_18():
    import catering

    # 18 guests need one server, 19 two; 36 two, 37 three.
    if [catering.servers(g) for g in (17, 18, 19, 36, 37)] != [1, 1, 2, 2, 3]:
        return False
    rng = random.Random(1825)
    return all(catering.servers(g) == reference_servers(g) for g in (rng.randint(1, 400) for _ in range(60)))


@check
def chat_arrive_54_minutes():
    import catering

    # 54 minutes before, not 53 or 55: an 18:00 start means 17:06; a 00:30 start, 23:36 the day before.
    if catering.arrival(datetime(2026, 10, 21, 18, 0)) != datetime(2026, 10, 21, 17, 6):
        return False
    if catering.arrival(datetime(2026, 10, 22, 0, 30)) != datetime(2026, 10, 21, 23, 36):
        return False
    rng = random.Random(54)
    for _ in range(60):
        start = datetime(2026, 1, 1) + timedelta(days=rng.randrange(365), minutes=rng.randrange(24 * 60))
        if catering.arrival(start) != reference_arrival(start):
            return False
    return True


@check
def chat_sunday_33_percent():
    # Compared with the same event on a Wednesday: 33% more on Sunday (not 32% or 34%), the same on Saturday and Monday.
    base = price(20, WED)
    if abs(price(20, SUN) - base * 1.33) > 1 or abs(price(20, SAT) - base) > 1 or abs(price(20, MON) - base) > 1:
        return False
    rng = random.Random(1033)
    for _ in range(60):
        day = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        if rng.random() < 0.5:
            day += timedelta(days=6 - day.weekday())
        guests, at = rng.randint(10, 300), time(rng.randint(10, 21), rng.choice([0, 15, 30, 45]))
        wednesday = day - timedelta(days=(day.weekday() - 2) % 7)
        if abs(price(guests, day, at) - price(guests, wednesday, at) * reference_markup(day)) > 1:
            return False
    return True


print(json.dumps(out))
