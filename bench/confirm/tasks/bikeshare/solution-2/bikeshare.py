"""Fares for the city bike scheme.

A ride is a dict: "start" and "end" (datetimes) and "member" (True for annual pass holders).
"""

from datetime import timedelta
from decimal import Decimal

PRICE_PER_MINUTE = Decimal("0.12")  # once the free time is used up


def minutes(ride):
    """How long the ride took in whole minutes; a started minute counts as a whole one."""
    whole, rest = divmod(ride["end"] - ride["start"], timedelta(minutes=1))
    return whole + (1 if rest else 0)


def fare(ride):
    """What the ride costs, as a Decimal rounded to the cent.

    Rides that start on a Wednesday are free (the council pays for them); otherwise the first 27 minutes are
    free and every minute after them costs PRICE_PER_MINUTE, with 14% off for members.
    """
    if ride["start"].isoweekday() == 3:
        return Decimal(0)
    paid = minutes(ride) - 27
    if paid <= 0:
        return Decimal(0)
    cents = paid * int(PRICE_PER_MINUTE * 100)
    if ride.get("member"):
        cents = (cents * 86 + 50) // 100  # 14% off, rounded half up to the cent
    return Decimal(cents) / 100
