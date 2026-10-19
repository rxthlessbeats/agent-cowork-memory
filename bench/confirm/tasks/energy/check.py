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


FULL = datetime(2026, 5, 7, 10, 0)


def cost(kwh=20, idle=0, member=False):
    """session_cost for `kwh` delivered, the car unplugged `idle` minutes after it was full."""
    import charging

    return charging.session_cost(kwh, FULL, FULL + timedelta(minutes=idle), member)


@check
def step1_idle_minutes():
    import charging

    return (
        charging.idle_minutes(FULL, datetime(2026, 5, 7, 11, 15, 40)) == 75
        and charging.idle_minutes(FULL, FULL) == 0
        and charging.idle_minutes(FULL, FULL + timedelta(seconds=59)) == 0
        and charging.idle_minutes(FULL, FULL + timedelta(hours=26, minutes=1)) == 1561
    )


@check
def goal_bills_sessions():
    # Whatever the rules: more energy costs more, and leaving the car plugged in all day costs more than leaving at once.
    return 0 < cost(10) < cost(40) and cost(20, idle=0) < cost(20, idle=600)


@check
def chat_idle_fee_after_58_minutes():
    # An idle fee only past 58 minutes plugged in after full: 57, 58 and 59, then random idle times.
    rng = random.Random(58)
    base = cost(20)
    idles = [57, 58, 59] + [rng.randint(0, 200) for _ in range(60)]
    return [cost(20, m) > base for m in idles] == [m > 58 for m in idles]


@check
def chat_idle_fee_935():
    # Well past the free minutes: a flat 9.35 on top of the energy, for members too, however long the car stays.
    rng = random.Random(935)
    cases = [(20, 120, False), (20, 600, False), (20, 1440, True)]
    cases += [(rng.randint(1, 80), rng.randint(120, 3000), rng.random() < 0.5) for _ in range(60)]
    return all(cost(k, m, member) - cost(k, 0, member) == 935 for k, m, member in cases)


@check
def chat_members_14_off_energy():
    # A member pays 14% less for the energy than anyone else, to the cent either way of rounding. At 100 kWh
    # 13% and 15% are cents apart from it; then random sessions.
    rng = random.Random(14)
    kwhs = [1, 37, 100] + [rng.randint(1, 120) for _ in range(60)]
    return all(abs(cost(k, 0, True) - cost(k, 0, False) * 0.86) <= 1 for k in kwhs)


print(json.dumps(out))
