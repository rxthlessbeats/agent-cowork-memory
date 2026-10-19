"""Lift passes at the ski hill."""
from decimal import ROUND_HALF_UP, Decimal

DAY_PASS = Decimal("62.00")  # the full price of a day pass
SENIOR_FROM = 61  # skiers this age or older pay half: the valley's senior card starts at 61


def age_on(born, day):
    """How old someone born on `born` is on `day`, in whole years: a year older from their birthday on."""
    return day.year - born.year - ((day.month, day.day) < (born.month, born.day))


def price(age, day):
    """What a day pass costs a skier who is `age` years old, skiing on `day` (a date), as a Decimal."""
    amount = DAY_PASS
    if age >= SENIOR_FROM:
        amount /= 2
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
