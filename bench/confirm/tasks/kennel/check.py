import json
import random
import sys
from datetime import datetime, time, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


CHECKIN = datetime(2026, 5, 4, 15, 0)


def cost(dogs=1, meds=0, nights=3, late=-60):
    """bill for `dogs` dogs, the first `meds` of them on medication, checked in at CHECKIN and collected `late`
    minutes after 11:00 on the day `nights` later (the default, -60, is 10:00)."""
    import kennel

    pack = [{"name": f"dog{i}", "meds": i < meds} for i in range(dogs)]
    collected = datetime.combine(CHECKIN.date() + timedelta(days=nights), time(11, 0)) + timedelta(minutes=late)
    return kennel.bill(pack, CHECKIN, collected)


@check
def step1_nights():
    import kennel

    return (
        kennel.nights(datetime(2026, 5, 4, 15, 0), datetime(2026, 5, 7, 10, 30)) == 3
        and kennel.nights(datetime(2026, 5, 4, 8, 0), datetime(2026, 5, 4, 18, 0)) == 0
        and kennel.nights(datetime(2026, 5, 31, 23, 0), datetime(2026, 6, 1, 7, 0)) == 1
    )


@check
def goal_longer_stays_cost_more():
    # Whatever the rules: more nights cost more, and a second dog costs something.
    return 0 < cost(nights=1) < cost(nights=5) and cost(dogs=1) < cost(dogs=2)


@check
def chat1_late_after_10_minutes():
    # Collected m minutes after 11:00 on the last day: one more night once m is over 10. 9, 10 and 11, then random.
    rng = random.Random(10)

    def ok(m, n):
        return cost(nights=n, late=m) == cost(nights=n + 1 if m > 10 else n)

    cases = [(9, 2), (10, 2), (11, 2)] + [(rng.randint(-180, 600), rng.randint(1, 14)) for _ in range(60)]
    return all(ok(m, n) for m, n in cases)


@check
def chat1_meds_743_a_night():
    # On top of the same booking without medication: 7.43 a night for each dog on it. Then random bookings.
    rng = random.Random(743)

    def ok(dogs, meds, n):
        return cost(dogs, meds, n) - cost(dogs, 0, n) == 743 * meds * n

    cases = [(1, 1, 1), (1, 1, 2), (2, 1, 3), (3, 2, 2)]
    for _ in range(60):
        dogs = rng.randint(1, 4)
        cases.append((dogs, rng.randint(0, dogs), rng.randint(1, 14)))
    return all(ok(*c) for c in cases)


@check
def changed_31_percent_off():
    # Every dog after the first costs 31% less than the first, whatever the nightly rate: k dogs cost
    # 1 + 0.69 (k - 1) times one dog, to a cent a dog a night. One, two and three dogs, then random bookings.
    rng = random.Random(31)

    def ok(k, n):
        return abs(cost(k, 0, n) - cost(1, 0, n) * (1 + 0.69 * (k - 1))) <= k * n

    cases = [(1, 3), (2, 3), (3, 3)] + [(rng.randint(1, 6), rng.randint(1, 14)) for _ in range(60)]
    return all(ok(k, n) for k, n in cases)


print(json.dumps(out))
