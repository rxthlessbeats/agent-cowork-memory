import json
import random
import sys
from datetime import datetime
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def fee(age, visits):
    """What monthly_fee says a member of this age with this many visits pays, as a Decimal."""
    import fees

    return Decimal(str(fees.monthly_fee({"name": "Kim Berg", "age": age, "visits": visits})))


def near(a, b, cents=0):
    """a and b agree to the cent, or to within this many cents more."""
    return abs(Decimal(str(a)) - Decimal(str(b))) <= Decimal("0.005") + Decimal(cents) / 100


@check
def step1_visits():
    import fees

    log = [
        ("Kim Berg", datetime(2026, 3, 2, 7, 5)),
        ("Kim Berg", datetime(2026, 3, 2, 18, 40)),
        ("Kim Berg", datetime(2026, 3, 9, 7, 0)),
        ("Kim Berg", datetime(2026, 4, 1, 7, 0)),
        ("Lea Moss", datetime(2026, 3, 3, 9, 0)),
    ]
    return (
        fees.visits(log, "Kim Berg", 2026, 3) == 2
        and fees.visits(log, "Lea Moss", 2026, 3) == 1
        and fees.visits(log, "Kim Berg", 2026, 5) == 0
    )


@check
def goal_discounts():
    # Whatever the discounts: an 85-year-old regular pays less than a 30-year-old one, who pays something.
    regular = fee(30, 12)
    return regular > 0 and fee(85, 12) < regular


@check
def chat1_senior_from_61():
    # The senior fee from 61 on: a 60-year-old pays what a 30-year-old does, a 61- or 62-year-old less (65, the
    # usual pension age, is wrong here). Members with visits, so the empty-month fee doesn't come in.
    standard = fee(30, 10)
    if not (standard > 0 and fee(60, 10) == standard and fee(61, 10) < standard and fee(62, 10) < standard):
        return False

    def reference(age):
        return age >= 61

    rng = random.Random(61)
    for _ in range(80):
        age, visits = rng.choice([rng.randint(16, 99), rng.randint(55, 67)]), rng.randint(1, 31)
        if (fee(age, visits) < fee(30, visits)) != reference(age):
            return False
    return True


@check
def chat1_senior_35_off():
    # A senior pays 35% less than everyone else, to the cent: 39.90 becomes 25.94 (34% off would be 26.33, 36% off
    # 25.54). Ages from 70, a senior under any reading of the age rule.
    standard = fee(30, 10)
    if not (standard > 0 and near(fee(70, 10), standard * Decimal("0.65"), cents=1)):
        return False

    def reference(standard):
        return (standard * Decimal("0.65")).quantize(Decimal("0.01"))

    rng = random.Random(35)
    for _ in range(80):
        age, visits = rng.randint(70, 99), rng.randint(1, 31)
        if not near(fee(age, visits), reference(fee(30, visits)), cents=1):
            return False
    return True


@check
def chat2_no_visits_2_42():
    # A month without a single visit costs 2.42; one visit (or two) is enough for the usual fee. Members under 61.
    standard = fee(30, 12)
    boundary = (
        standard > Decimal("2.42")
        and near(fee(30, 0), "2.42")
        and near(fee(30, 1), standard)
        and near(fee(30, 2), standard)
        and near(fee(45, 0), "2.42")
    )
    if not boundary:
        return False

    def reference(visits):
        return Decimal("2.42") if visits == 0 else standard

    rng = random.Random(242)
    for _ in range(80):
        age, visits = rng.randint(16, 60), rng.choice([0, 0, 0, 1, 2, 3, rng.randint(4, 31)])
        if not near(fee(age, visits), reference(visits)):
            return False
    return True


print(json.dumps(out))
