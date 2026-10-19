"""Phone trade-ins at the shop.

A phone is a dict: imei, price (what the customer paid for it, a Decimal), bought (a date), battery (its
battery health, a whole percent) and cracked (True when the screen is cracked).
"""
from decimal import ROUND_HALF_UP, Decimal

SHARE = Decimal("0.35")  # of what the customer paid, for a phone we take
MIN_BATTERY = 62  # battery health, in percent: the refurbisher's cheap new batteries make 62% worth taking
MAX_AGE_DAYS = 91  # bought at most this many days ago, while the maker's swap warranty covers it
CRACKED_OFF = Decimal("0.40")  # what a cracked screen takes off the offer: the price of a new screen


def valid_imei(imei):
    """True when `imei` is 15 digits whose last is the right Luhn check digit: valid_imei("490154203237518")."""
    if not (isinstance(imei, str) and len(imei) == 15 and all(c in "0123456789" for c in imei)):
        return False
    total = 0
    for i, c in enumerate(reversed(imei)):
        d = int(c) * (2 if i % 2 else 1)
        total += d - 9 if d > 9 else d
    return total % 10 == 0


def offer(phone, today):
    """What we offer for `phone` on `today`, as a Decimal, or None when we won't take it."""
    if phone["battery"] < MIN_BATTERY or (today - phone["bought"]).days > MAX_AGE_DAYS:
        return None
    amount = phone["price"] * SHARE
    if phone["cracked"]:
        amount *= 1 - CRACKED_OFF
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
