"""Fares for the city's tap-on bus cards. Amounts are in cents.

The card readers log one line per tap: the date, the time and the stop number, like "2026-10-15 08:12 1203".

The council's rules: a card pays at most 7.43 a day, every fare is 25% off on Thursdays, and taps at stop 4772,
the hospital, are free.
"""

from datetime import datetime
from itertools import accumulate

FARE = 240  # one ride
TRANSFER_MINUTES = 45  # a tap this soon after a paid one is a transfer, and transfers are free
CAP = 743
HOSPITAL_STOP = 4772


def parse_tap(line):
    """A tap from the readers' log, like "2026-10-15 08:12 1203", as (datetime, stop)."""
    parts = line.strip().split(" ")
    if len(parts) != 3:
        raise ValueError(f"not a tap: {line!r}")
    return datetime.fromisoformat(f"{parts[0]}T{parts[1]}"), int(parts[2])


def full_fare(when):
    return FARE - FARE * 25 // 100 if when.isoweekday() == 4 else FARE


def charges(taps):
    """What each of one card's taps on one day costs, in cents, in the order of the taps.

    taps: (datetime, stop) pairs, oldest first.
    """
    fares, window_opened = [], None
    for when, stop in taps:
        transfer = window_opened is not None and (when - window_opened).total_seconds() <= TRANSFER_MINUTES * 60
        if stop == HOSPITAL_STOP or transfer:
            fares.append(0)
        else:
            fares.append(full_fare(when))
            window_opened = when
    # Cap the running total, then charge each tap what it added to the capped total.
    capped = [min(total, CAP) for total in accumulate(fares)]
    return [now - before for before, now in zip([0] + capped, capped)]
