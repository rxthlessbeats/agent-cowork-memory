"""Fares for the city's tap-on bus cards. Amounts are in cents.

The card readers log one line per tap: the date, the time and the stop number, like "2026-10-15 08:12 1203".
"""

FARE = 240  # one ride
TRANSFER_MINUTES = 45  # a tap this soon after a paid one is a transfer, and transfers are free


def charges(taps):
    """What each of one card's taps on one day costs, in cents, in the order of the taps.

    taps: (datetime, stop) pairs, oldest first.
    """
    raise NotImplementedError
