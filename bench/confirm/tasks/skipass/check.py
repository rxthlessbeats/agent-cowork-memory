import json
import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from fractions import Fraction

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


MONDAY = date(2026, 1, 5)
THURSDAY = 3  # date.weekday()


def cost(age, day=MONDAY):
    """price in cents, whatever number type it returns."""
    import skipass

    return round(Decimal(str(skipass.price(age, day))) * 100)


def reference(age, day, full):
    """This season's rules, for a full price of `full` cents on `day`: what price should give, in cents."""
    if age >= 82:
        return 0
    amount = Fraction(full)
    if age >= 61:
        amount /= 2
    if day.weekday() == THURSDAY:
        amount *= Fraction(74, 100)
    return amount


def near(got, want):
    """Equal to within a cent, whichever way the folder rounds on the way."""
    return abs(got - want) <= 1


def season_day(rng, thursdays=True):
    """A random day in the season, from 5 January to the end of April."""
    while True:
        day = MONDAY + timedelta(days=rng.randrange(116))
        if thursdays or day.weekday() != THURSDAY:
            return day


@check
def step1_age_on():
    import skipass

    return (
        skipass.age_on(date(1990, 3, 15), date(2026, 3, 14)) == 35
        and skipass.age_on(date(1990, 3, 15), date(2026, 3, 15)) == 36
        and skipass.age_on(date(2000, 12, 31), date(2026, 1, 1)) == 25
        and skipass.age_on(date(2026, 1, 1), date(2026, 6, 1)) == 0
    )


@check
def goal_prices_passes():
    full = cost(40)
    return full > 0 and cost(40, MONDAY + timedelta(days=1)) > 0 and any(cost(age) < full for age in range(101))


@check
def changed_seniors_from_61():
    # Half price from 61, which chat 2 brought down from 65; at 60, the full price.
    full = cost(40)
    if full <= 0 or not (cost(60) == full and near(cost(61), Fraction(full, 2)) and near(cost(62), Fraction(full, 2))):
        return False
    rng = random.Random(6161)
    for _ in range(60):
        age, day = rng.randint(18, 79), season_day(rng, thursdays=False)
        if not near(cost(age, day), reference(age, day, cost(40, day))):
            return False
    return True


@check
def chat1_free_from_82():
    # Free from 82; at 81, a skier still pays.
    if [cost(81) > 0, cost(82) == 0, cost(83) == 0] != [True, True, True]:
        return False
    rng = random.Random(8282)
    for _ in range(60):
        age, day = rng.randint(66, 100), season_day(rng, thursdays=False)
        if (cost(age, day) == 0) != (reference(age, day, cost(40, day)) == 0):
            return False
    return True


@check
def chat1_thursday_26_off():
    # 26% off on a Thursday; the Wednesday before and the Friday after, the full price.
    full = cost(40)
    wednesday, thursday, friday = (cost(40, MONDAY + timedelta(days=k)) for k in (2, 3, 4))
    if full <= 0 or not (wednesday == full and near(thursday, full * Fraction(74, 100)) and friday == full):
        return False
    rng = random.Random(2626)
    for _ in range(60):
        age, day = rng.randint(18, 59), MONDAY + timedelta(weeks=rng.randrange(16), days=rng.randrange(5))
        monday = day - timedelta(days=day.weekday())
        if not near(cost(age, day), reference(age, day, cost(age, monday))):
            return False
    return True


print(json.dumps(out))
