"""Fares for the city bike scheme.

A ride is a dict: "start" and "end" (datetimes) and "member" (True for annual pass holders).
"""

import math
from decimal import ROUND_HALF_UP, Decimal

PRICE_PER_MINUTE = Decimal("0.12")  # once the free time is used up
FREE_MINUTES = 27  # covers most trips across town
MEMBER_DISCOUNT = Decimal("0.14")  # agreed with the council for annual passes
WEDNESDAY = 2  # date.weekday(): the council pays for Wednesday rides


def minutes(ride):
    """How long the ride took in whole minutes; a started minute counts as a whole one."""
    return math.ceil((ride["end"] - ride["start"]).total_seconds() / 60)


def fare(ride):
    """What the ride costs, as a Decimal rounded to the cent."""
    if ride["start"].weekday() == WEDNESDAY:
        return Decimal("0.00")
    price = max(0, minutes(ride) - FREE_MINUTES) * PRICE_PER_MINUTE
    if ride["member"]:
        price *= 1 - MEMBER_DISCOUNT
    return price.quantize(Decimal("0.01"), ROUND_HALF_UP)
