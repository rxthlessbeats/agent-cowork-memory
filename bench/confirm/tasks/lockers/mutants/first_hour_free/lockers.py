"""Luggage lockers at the station: a customer leaves a bag in a locker and pays when they collect it."""

import math

SIZES = ("small", "large")
LARGE_FACTOR = 2  # a large locker costs this many times what a small one does
FREE_MINUTES = 60  # the first hour is free
HOURLY = 453  # cents for every started hour of a longer stay
MONDAY_OFF = 14  # percent off bags dropped off on a Monday


def minutes(dropped, collected):
    """Whole minutes between two datetimes; a started minute counts as a whole one."""
    return math.ceil((collected - dropped).total_seconds() / 60)


def charge(size, dropped, collected):
    """What the customer pays, in cents, for a bag left in a `size` locker from `dropped` until `collected`.

    size is "small" or "large"; dropped and collected are datetimes.
    """
    stay = minutes(dropped, collected)
    if stay <= FREE_MINUTES:
        return 0
    cents = math.ceil(stay / 60) * HOURLY
    if size == "large":
        cents *= LARGE_FACTOR
    if dropped.weekday() == 0:
        cents = round(cents * (100 - MONDAY_OFF) / 100)
    return cents


def receipt(size, dropped, collected):
    """The line printed for the customer when they collect their bag."""
    cents = charge(size, dropped, collected)
    return f"{size.capitalize()} locker, {dropped:%a %d %b %H:%M} to {collected:%a %d %b %H:%M}: {cents // 100}.{cents % 100:02d}"
