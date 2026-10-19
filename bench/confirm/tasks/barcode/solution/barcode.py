"""Barcodes for the shop's yellow reduced-price stickers. See README.md (out of date on reductions)."""

from datetime import timedelta

from config import MANAGER_LIMIT

REDUCE_WITHIN = timedelta(hours=48)  # a day wasn't long enough to sell the chilled stuff
PERCENT_OFF = 21  # head office: clears the shelf as well as half price did, without losing money
CHEAPEST = 469  # pence: cheaper lines sell out anyway, and stickers cause queries at the till


def sticker(code, pence):
    """The EAN-13 barcode for a reduced sticker: 29, the item's 5-digit code, the price in pence as 5 digits, and
    the check digit."""
    digits = f"29{code:0>5}{pence:05d}"
    return digits + str(check_digit(digits))


def check_digit(digits):
    """The EAN-13 check digit for the first 12 digits of a barcode: check_digit("400638133393") == 1."""
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(digits[:12]))
    return (10 - total % 10) % 10


def reduced_price(item, now):
    """The price in pence for an item's reduced sticker, or None when it gets no sticker."""
    price = item["price"]
    if price < CHEAPEST or price > MANAGER_LIMIT:
        return None
    if item["use_by"] - now > REDUCE_WITHIN:
        return None
    return (price * (100 - PERCENT_OFF) + 50) // 100
