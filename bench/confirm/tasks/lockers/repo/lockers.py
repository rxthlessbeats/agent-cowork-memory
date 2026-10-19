"""Luggage lockers at the station: a customer leaves a bag in a locker and pays when they collect it."""

SIZES = ("small", "large")
LARGE_FACTOR = 2  # a large locker costs this many times what a small one does


def charge(size, dropped, collected):
    """What the customer pays, in cents, for a bag left in a `size` locker from `dropped` until `collected`.

    size is "small" or "large"; dropped and collected are datetimes.
    """
    raise NotImplementedError


def receipt(size, dropped, collected):
    """The line printed for the customer when they collect their bag."""
    cents = charge(size, dropped, collected)
    return f"{size.capitalize()} locker, {dropped:%a %d %b %H:%M} to {collected:%a %d %b %H:%M}: {cents // 100}.{cents % 100:02d}"
