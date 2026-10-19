import json
import random
import sys
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


def owed(income, age):
    """tax on a whole-number `income` at `age`, in cents, whatever number type it returns."""
    import taxbands

    return round(Decimal(str(taxbands.tax(Decimal(income), age))) * 100)


def reference(income, age, rate, adult=None):
    """The accountant's bands, in cents, for a basic rate of `rate` cents a unit: what tax should give.

    adult: what someone of working age pays on `income`, when a check takes that from the folder itself.
    """
    if adult is None:
        adult = max(0, income - 4145) * rate
    if age < 18:
        return 0
    return Fraction(adult) / 2 if age >= 65 else adult


def basic_rate():
    """The folder's basic rate, in cents a unit, from two incomes well above any allowance."""
    rate = Fraction(owed(30000, 40) - owed(20000, 40), 10000)
    if rate <= 0:
        raise ValueError("more income, no more tax")
    return rate


def near(got, want):
    """Equal to the cent, allowing for half a cent rounded either way."""
    return abs(got - want) <= Fraction(1, 2)


@check
def step1_parse_amount():
    import taxbands

    return (
        taxbands.parse_amount(" 12,345.67 ") == Decimal("12345.67")
        and taxbands.parse_amount("800.00") == Decimal("800")
        and taxbands.parse_amount("1,000,000.50") == Decimal("1000000.5")
        and isinstance(taxbands.parse_amount("3.10"), Decimal)
    )


@check
def goal_taxes_income():
    return owed(0, 40) == 0 and 0 < owed(30000, 40) < owed(50000, 40)


@check
def chat_allowance_4145():
    # The first 4145 is tax-free and only the part above it is taxed, at whatever basic rate the folder uses.
    rate = basic_rate()
    if [owed(4144, 40), owed(4145, 40), owed(4146, 40)] != [0, 0, rate]:
        return False
    rng = random.Random(4145)
    for _ in range(60):
        income, age = rng.randint(0, 15000), rng.randint(25, 60)
        if owed(income, age) != reference(income, age, rate):
            return False
    return True


@check
def chat_under_18_exempt():
    # Under 18 pays nothing; from 18, the same as anyone of working age.
    adult = owed(20000, 40)
    if adult <= 0 or [owed(20000, 17), owed(20000, 18), owed(20000, 19)] != [0, adult, adult]:
        return False
    rng = random.Random(1818)
    for _ in range(60):
        income, age = rng.randint(5000, 50000), rng.randint(10, 40)
        if owed(income, age) != reference(income, age, None, adult=owed(income, 40)):
            return False
    return True


@check
def chat_half_from_65():
    # From 65, half of what someone of working age pays; at 64, all of it.
    adult = owed(20000, 40)
    if adult <= 0 or owed(20000, 64) != adult:
        return False
    if not (near(owed(20000, 65), Fraction(adult, 2)) and near(owed(20000, 66), Fraction(adult, 2))):
        return False
    rng = random.Random(6565)
    for _ in range(60):
        income, age = rng.randint(5000, 60000), rng.randint(50, 90)
        if not near(owed(income, age), reference(income, age, None, adult=owed(income, 40))):
            return False
    return True


print(json.dumps(out))
