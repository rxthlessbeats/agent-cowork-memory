"""Prices for renting out tools and machines, in EUR."""
from datetime import date
from decimal import Decimal

DAY_RATES = {"drill": Decimal("12.00"), "mixer": Decimal("35.00"), "excavator": Decimal("240.00")}
HALF = Decimal("0.5")
# Flat per rental: the haulage firm bills each excavator trip (this replaced the 3-day minimum).
DELIVERY_FEES = {"excavator": Decimal("95.00")}


def rental_days(start, end):
    """Days charged for a rental picked up on start and brought back on end."""
    return (end - start).days


def day_share(n):
    """The share of the day rate charged for the nth day of a rental (from 1): days after the fifth cost half."""
    return 1 if n <= 5 else HALF


def price(item, start, end):
    """What we charge to rent the item from start to end (both dates)."""
    if end < start:
        raise ValueError("the return date is before the pickup date")
    days = rental_days(start, end)
    # A rental brought back the day it was picked up costs half a day rate.
    shares = sum(day_share(n) for n in range(1, days + 1)) if days else HALF
    return DAY_RATES[item] * shares + DELIVERY_FEES.get(item, 0)


if __name__ == "__main__":
    import sys

    print(price(sys.argv[1], date.fromisoformat(sys.argv[2]), date.fromisoformat(sys.argv[3])))
