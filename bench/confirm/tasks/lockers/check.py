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


TUESDAY = datetime(2026, 5, 5, 8, 0)
MONDAY = datetime(2026, 5, 4)  # midnight, as Monday starts


def cost(minutes, dropped=TUESDAY, size="small"):
    """charge for a bag dropped at `dropped` and collected `minutes` later."""
    import lockers

    return lockers.charge(size, dropped, dropped + timedelta(minutes=minutes))


@check
def step1_minutes():
    import lockers

    t = datetime(2026, 5, 4, 9, 30)
    return (
        lockers.minutes(t, datetime(2026, 5, 4, 11, 1, 20)) == 92
        and lockers.minutes(t, t) == 0
        and lockers.minutes(t, t + timedelta(seconds=1)) == 1
        and lockers.minutes(t, t + timedelta(minutes=59, seconds=59)) == 60
        and lockers.minutes(t, t + timedelta(days=2)) == 2880
    )


@check
def goal_long_stays_cost_more():
    # Whatever the rules: a day in a locker costs something, and two days cost more.
    return 0 < cost(24 * 60) < cost(48 * 60)


@check
def chat_free_up_to_91_minutes():
    # Free for a stay of up to 91 minutes, charged from 92: at the edge, then random stays.
    rng = random.Random(9101)
    stays = [90, 91, 92] + [rng.randint(1, 240) for _ in range(60)]
    return [cost(m) == 0 for m in stays] == [m <= 91 for m in stays]


@check
def chat_453_per_started_hour():
    # Past the free minutes: 4.53 for every started hour of the whole stay. 179 and 180 minutes are 3 hours, 181 is 4.
    rng = random.Random(453)
    stays = [179, 180, 181] + [rng.randint(92, 3000) for _ in range(60)]
    return [cost(m) for m in stays] == [453 * -(-m // 60) for m in stays]


@check
def chat_monday_14_off():
    # Dropped off on a Monday: 14% off what the same stay costs from a Tuesday, to the cent either way of rounding.
    # Sunday 23:59 and Tuesday 00:00 pay in full; Monday 00:00 and 23:59 get the discount. Then random drop-offs.
    rng = random.Random(1486)

    def ok(dropped, minutes):
        full, got = cost(minutes), cost(minutes, dropped)
        return abs(got - full * 0.86) <= 1 if dropped.weekday() == 0 else got == full

    edges = [MONDAY - timedelta(minutes=1), MONDAY, MONDAY + timedelta(hours=23, minutes=59), MONDAY + timedelta(days=1)]
    cases = [(d, 300) for d in edges]
    cases += [(MONDAY + timedelta(minutes=rng.randint(-3 * 1440, 11 * 1440)), rng.randint(92, 3000)) for _ in range(60)]
    return all(ok(d, m) for d, m in cases)


print(json.dumps(out))
