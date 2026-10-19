import json
import random
import sys
from datetime import date, timedelta
from fractions import Fraction

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


ADULT, CONCESSION = 1800, 1200
FRI, SAT, SUN, TUE = date(2026, 10, 16), date(2026, 10, 17), date(2026, 10, 18), date(2026, 10, 20)


def reference(ages, day):
    """Chat 1: under 16 goes free, and 40 or more people get 4% off the booking. Chat 2: on Saturdays every ticket
    that isn't free costs 5.51 more. Seniors pay the concession price. No check mixes a Saturday with a big group."""
    paid = [CONCESSION if age >= 65 else ADULT for age in ages if age >= 16]
    total = Fraction(sum(paid))
    if day.weekday() == 5:
        total += 551 * len(paid)
    if len(ages) >= 40:
        total = total * 96 / 100
    return total


def quote(ages, day):
    import tickets

    return float(tickets.quote(list(ages), day))


def near(got, want):
    return abs(got - float(want)) <= 1


def day_of(rng, saturdays=False):
    """A random day in 2026 that isn't a Saturday, or with saturdays=True, a Saturday half the time."""
    day = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
    if saturdays and rng.random() < 0.5:
        return day + timedelta(days=(5 - day.weekday()) % 7)
    return day + timedelta(days=1) if day.weekday() == 5 else day


@check
def step1_parse_booking():
    import tickets

    return (
        tickets.parse_booking("2026-10-17: 34, 36, 8") == (date(2026, 10, 17), [34, 36, 8])
        and tickets.parse_booking("2026-11-02: 70") == (date(2026, 11, 2), [70])
    )


@check
def goal_quote():
    return near(quote([30, 41], TUE), 2 * ADULT)


@check
def chat1_under_16_free():
    # 15 goes free; 16 and 17 pay the adult price.
    if not all(near(quote([age], TUE), want) for age, want in ((15, 0), (16, ADULT), (17, ADULT))):
        return False
    rng = random.Random(1615)
    for _ in range(60):
        ages, day = [rng.randint(0, 59) for _ in range(rng.randint(1, 8))], day_of(rng)
        if not near(quote(ages, day), reference(ages, day)):
            return False
    return True


@check
def chat1_group_40_4_percent():
    # 39 adults pay in full; 40 and 41 get 4% off (not 3% or 5%).
    if not all(near(quote([30] * n, TUE), want) for n, want in ((39, 39 * 1800), (40, 40 * 1728), (41, 41 * 1728))):
        return False
    rng = random.Random(4004)
    for _ in range(60):
        size = rng.choice([rng.randint(30, 60), rng.randint(38, 42)])  # often right at the threshold
        ages, day = [rng.randint(20, 59) for _ in range(size)], day_of(rng)
        if not near(quote(ages, day), reference(ages, day)):
            return False
    return True


@check
def chat2_saturday_5_51():
    # 5.51 more on Saturday, not on the Friday before or the Sunday after; a child still goes free on Saturday.
    cases = (([30], FRI, 1800), ([30], SAT, 2351), ([30], SUN, 1800), ([30, 3], SAT, 2351))
    if not all(near(quote(ages, day), want) for ages, day, want in cases):
        return False
    rng = random.Random(551)
    for _ in range(60):
        # Grown-ups, and toddlers who go free under any age rule.
        ages = [
            rng.choice([rng.randint(0, 4), rng.randint(20, 59), rng.randint(20, 59)])
            for _ in range(rng.randint(1, 8))
        ]
        day = day_of(rng, saturdays=True)
        if not near(quote(ages, day), reference(ages, day)):
            return False
    return True


print(json.dumps(out))
