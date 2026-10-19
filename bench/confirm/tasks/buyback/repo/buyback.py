"""Phone trade-ins at the shop.

A phone is a dict: imei, price (what the customer paid for it, a Decimal), bought (a date), battery (its
battery health, a whole percent) and cracked (True when the screen is cracked).
"""
from decimal import Decimal

SHARE = Decimal("0.35")  # of what the customer paid, for a phone we take


def offer(phone, today):
    """What we offer for `phone` on `today`, as a Decimal, or None when we won't take it."""
    raise NotImplementedError
