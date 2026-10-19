"""Lift passes at the ski hill."""
from decimal import Decimal

DAY_PASS = Decimal("62.00")  # the full price of a day pass


def price(age, day):
    """What a day pass costs a skier who is `age` years old, skiing on `day` (a date), as a Decimal."""
    raise NotImplementedError
