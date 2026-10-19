"""Lift passes at the ski hill."""
import calendar
from decimal import Decimal

DAY_PASS = Decimal("62.00")  # the full price of a day pass


def age_on(born, day):
    """How old someone born on `born` is on `day`, in whole years: 36 on 15 March 2026 for a skier born 15 March 1990."""
    try:
        birthday = born.replace(year=day.year)
    except ValueError:  # born on 29 February, in a year without one: older from 1 March
        birthday = born.replace(year=day.year, month=3, day=1)
    years = day.year - born.year
    return years if day >= birthday else years - 1


def shares(age, day):
    """What each of this season's rules leaves of the full price, for a skier `age` years old on `day`."""
    if age >= 82:  # the club's promise to its founding members
        yield Decimal(0)
    if age >= 61:  # the valley's senior card
        yield Decimal("0.5")
    if day.weekday() == calendar.THURSDAY:  # our quietest day: 26% off
        yield Decimal("0.74")


def price(age, day):
    """What a day pass costs a skier who is `age` years old, skiing on `day` (a date), as a Decimal."""
    amount = DAY_PASS
    for share in shares(age, day):
        amount *= share
    return amount.quantize(Decimal("0.01"))
