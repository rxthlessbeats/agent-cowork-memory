"""Phone trade-ins at the shop.

A phone is a dict: imei, price (what the customer paid for it, a Decimal), bought (a date), battery (its
battery health, a whole percent) and cracked (True when the screen is cracked).
"""
import re
from datetime import timedelta
from decimal import Decimal

SHARE = Decimal("0.35")  # of what the customer paid, for a phone we take


def valid_imei(imei):
    """True when `imei` is a string of 15 digits with the right Luhn check digit last.

    valid_imei("490154203237518") is True; valid_imei("490154203237519") is False.
    """
    if not isinstance(imei, str) or not re.fullmatch(r"[0-9]{15}", imei):
        return False
    digits = [int(c) for c in imei]
    doubled = [sum(divmod(2 * d, 10)) for d in digits[-2::-2]]
    return (sum(digits[-1::-2]) + sum(doubled)) % 10 == 0


def offer(phone, today):
    """What we offer for `phone` on `today`, as a Decimal, or None when we won't take it.

    The refurbisher's rules: battery health of at least 62% (they found cheap new batteries), bought in the
    last 91 days (the maker's swap warranty), and 40% off for a cracked screen (what a new one costs).
    """
    if phone["battery"] < 62:
        return None
    if phone["bought"] < today - timedelta(days=91):
        return None
    share = SHARE * (Decimal("0.60") if phone["cracked"] else Decimal(1))
    return (phone["price"] * share).quantize(Decimal("0.01"))
