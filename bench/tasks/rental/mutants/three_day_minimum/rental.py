"""Prices for renting out tools and machines, in EUR."""
from datetime import date
from decimal import Decimal

DAY_RATES = {"drill": Decimal("12.00"), "mixer": Decimal("35.00"), "excavator": Decimal("240.00")}
FULL_PRICE_DAYS = 5  # the days after these cost half the day rate
EXCAVATOR_MIN_DAYS = 3  # the excavator is never charged for fewer than 3 days


def rental_days(start, end):
    """Days charged for a rental picked up on start and brought back on end."""
    if end < start:
        raise ValueError(f"returned on {end}, before it was picked up on {start}")
    return (end - start).days


def price(item, start, end):
    """What we charge to rent the item from start to end (both dates)."""
    rate, days = DAY_RATES[item], rental_days(start, end)
    if item == "excavator":
        days = max(days, EXCAVATOR_MIN_DAYS)
    if days == 0:  # brought back the day it was picked up
        cost = rate / 2
    else:
        cost = rate * min(days, FULL_PRICE_DAYS) + rate / 2 * max(days - FULL_PRICE_DAYS, 0)
    return cost


if __name__ == "__main__":
    import sys

    print(price(sys.argv[1], date.fromisoformat(sys.argv[2]), date.fromisoformat(sys.argv[3])))
