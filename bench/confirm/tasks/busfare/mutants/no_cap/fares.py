"""Fares for the city's tap-on bus cards. Amounts are in cents.

The card readers log one line per tap: the date, the time and the stop number, like "2026-10-15 08:12 1203".
"""

from datetime import datetime, timedelta

FARE = 240  # one ride
TRANSFER_MINUTES = 45  # a tap this soon after a paid one is a transfer, and transfers are free
THURSDAY = 3  # date.weekday(): market day, when every fare is 25% off
HOSPITAL = 4772  # the hospital pays for rides from its stop


def parse_tap(line):
    """A tap from the readers' log as (datetime, stop): parse_tap("2026-10-15 08:12 1203")."""
    day, clock, stop = line.split()
    return datetime.strptime(f"{day} {clock}", "%Y-%m-%d %H:%M"), int(stop)


def charges(taps):
    """What each of one card's taps on one day costs, in cents, in the order of the taps.

    taps: (datetime, stop) pairs, oldest first.
    """
    result, paid, last_paid = [], 0, None
    for when, stop in taps:
        if stop == HOSPITAL:
            fare = 0
        elif last_paid is not None and when - last_paid <= timedelta(minutes=TRANSFER_MINUTES):
            fare = 0
        else:
            fare = FARE * 3 // 4 if when.weekday() == THURSDAY else FARE
            last_paid = when
        paid += fare
        result.append(fare)
    return result
