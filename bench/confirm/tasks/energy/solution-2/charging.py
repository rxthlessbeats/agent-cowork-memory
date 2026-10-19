"""The company's public charge points.

README.md is out of date on the idle fee and the member discount: a car may stay plugged in for up to 58 minutes
after it's full, then pays a flat 9.35; members get 14% off the energy.
"""

from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

PRICE_PER_KWH = 45  # cents


def idle_minutes(full, unplugged):
    """Whole minutes plugged in after full: 10:00:00 to 11:15:40 is 75."""
    if unplugged <= full:
        return 0
    return (unplugged - full) // timedelta(minutes=1)


def session_cost(kwh, full, unplugged, member):
    """What a driver pays for a charging session, in cents.

    kwh: the energy delivered; full and unplugged: datetimes, when the car was full and when it was unplugged;
    member: True for a member.
    """
    energy = Decimal(str(kwh)) * PRICE_PER_KWH
    if member:
        energy *= Decimal("0.86")
    idle_fee = 935 if idle_minutes(full, unplugged) > 58 else 0
    return int(energy.quantize(Decimal(1), rounding=ROUND_HALF_UP)) + idle_fee
