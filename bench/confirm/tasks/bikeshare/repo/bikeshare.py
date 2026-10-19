"""Fares for the city bike scheme.

A ride is a dict: "start" and "end" (datetimes) and "member" (True for annual pass holders).
"""

from decimal import Decimal

PRICE_PER_MINUTE = Decimal("0.12")  # once the free time is used up


def fare(ride):
    """What the ride costs, as a Decimal rounded to the cent."""
    raise NotImplementedError
