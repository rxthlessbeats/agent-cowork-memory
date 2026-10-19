"""Membership fees for the gym.

A member is a dict: "name", "age" (in whole years on the first of the month) and "visits" (on how many days they
came in that month).
"""

from decimal import Decimal

STANDARD_FEE = Decimal("39.90")  # a month


def monthly_fee(member):
    """What the member pays for the month, as a Decimal rounded to the cent."""
    return STANDARD_FEE
