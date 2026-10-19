"""Prices for renting out tools and machines, in EUR."""
from datetime import date
from decimal import Decimal

DAY_RATES = {"drill": Decimal("12.00"), "mixer": Decimal("35.00"), "excavator": Decimal("240.00")}


def rental_days(start, end):
    """Days charged for a rental picked up on start and brought back on end."""
    return (end - start).days


def price(item, start, end):
    """What we charge to rent the item from start to end (both dates)."""
    return DAY_RATES[item] * rental_days(start, end)


if __name__ == "__main__":
    import sys

    print(price(sys.argv[1], date.fromisoformat(sys.argv[2]), date.fromisoformat(sys.argv[3])))
