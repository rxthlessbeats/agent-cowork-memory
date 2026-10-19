"""Luggage lockers at the station: a customer leaves a bag in a locker and pays when they collect it.

Up to 91 minutes is free; a longer stay costs 4.53 for every started hour of the whole stay, and a bag
dropped off on a Monday gets 14% off.
"""

from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

SIZES = ("small", "large")
LARGE_FACTOR = 2  # a large locker costs this many times what a small one does

MINUTE = timedelta(minutes=1)


def minutes(dropped, collected):
    """Whole minutes between two datetimes, a started minute counting as a whole one: 9:30:00 to 11:01:20 is 92."""
    whole, rest = divmod(collected - dropped, MINUTE)
    return whole + (1 if rest else 0)


def charge(size, dropped, collected):
    """What the customer pays, in cents, for a bag left in a `size` locker from `dropped` until `collected`.

    size is "small" or "large"; dropped and collected are datetimes.
    """
    stay = minutes(dropped, collected)
    if stay <= 91:
        return 0
    hours = (stay + 59) // 60
    price = Decimal("4.53") * hours
    if size == "large":
        price *= LARGE_FACTOR
    if dropped.isoweekday() == 1:
        price *= Decimal("0.86")
    return int((price * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def receipt(size, dropped, collected):
    """The line printed for the customer when they collect their bag."""
    cents = charge(size, dropped, collected)
    return f"{size.capitalize()} locker, {dropped:%a %d %b %H:%M} to {collected:%a %d %b %H:%M}: {cents // 100}.{cents % 100:02d}"
