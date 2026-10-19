"""Membership fees for the gym.

A member is a dict: "name", "age" (in whole years on the first of the month) and "visits" (on how many days they
came in that month).
"""

from decimal import Decimal

STANDARD_FEE = Decimal("39.90")  # a month


def visits(checkins, name, year, month):
    """On how many different days the member checked in during that month; two check-ins on one day count once."""
    days = set()
    for who, when in checkins:
        if who == name and when.year == year and when.month == month:
            days.add(when.day)
    return len(days)


def monthly_fee(member):
    """What the member pays for the month, as a Decimal rounded to the cent.

    A month without visits costs only the 2.42 insurance. Members aged 61 or over pay the senior fee, 35% off.
    """
    if not member["visits"]:
        return Decimal("2.42")
    cents = int(STANDARD_FEE * 100)
    if member["age"] >= 61:
        cents = (cents * 65 + 50) // 100  # 35% off, rounded half up
    return Decimal(cents) / 100
