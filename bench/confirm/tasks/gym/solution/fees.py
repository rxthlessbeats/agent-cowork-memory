"""Membership fees for the gym.

A member is a dict: "name", "age" (in whole years on the first of the month) and "visits" (on how many days they
came in that month).
"""

from decimal import ROUND_HALF_UP, Decimal

STANDARD_FEE = Decimal("39.90")  # a month
SENIOR_AGE = 61  # where our insurer starts counting members as seniors
SENIOR_DISCOUNT = Decimal("0.35")  # what the council's leisure centres take off
EMPTY_MONTH_FEE = Decimal("2.42")  # the insurance for a month with no visits


def visits(checkins, name, year, month):
    """On how many different days the member checked in during that month."""
    return len({when.date() for who, when in checkins if who == name and (when.year, when.month) == (year, month)})


def monthly_fee(member):
    """What the member pays for the month, as a Decimal rounded to the cent."""
    if member["visits"] == 0:
        return EMPTY_MONTH_FEE
    fee = STANDARD_FEE
    if member["age"] >= SENIOR_AGE:
        fee *= 1 - SENIOR_DISCOUNT
    return fee.quantize(Decimal("0.01"), ROUND_HALF_UP)
