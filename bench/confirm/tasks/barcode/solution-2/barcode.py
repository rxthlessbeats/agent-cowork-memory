"""Barcodes for the shop's yellow reduced-price stickers.

README.md is out of date on reductions: an item gets a sticker 48 hours or less from its use-by, at
21% off, and only if it costs at least £4.69 and no more than config.MANAGER_LIMIT.
"""

from decimal import ROUND_HALF_UP, Decimal
from itertools import cycle

import config

HOURS_BEFORE_USE_BY = 48


def sticker(code, pence):
    """The EAN-13 barcode for a reduced sticker: 29, the item's 5-digit code, the price in pence as 5 digits, and
    the check digit."""
    digits = f"29{code:0>5}{pence:05d}"
    return digits + str(check_digit(digits))


def check_digit(digits):
    """The EAN-13 check digit for 12 digits: weights 1, 3, 1, 3, ... from the left."""
    total = sum(int(d) * w for d, w in zip(digits[:12], cycle((1, 3))))
    return -total % 10


def stickered(item, now):
    hours_left = (item["use_by"] - now).total_seconds() / 3600
    return hours_left <= HOURS_BEFORE_USE_BY and 469 <= item["price"] <= config.MANAGER_LIMIT


def reduced_price(item, now):
    """The price in pence for an item's reduced sticker, or None when it gets no sticker."""
    if not stickered(item, now):
        return None
    return int((Decimal(item["price"]) * Decimal("0.79")).quantize(Decimal(1), rounding=ROUND_HALF_UP))
