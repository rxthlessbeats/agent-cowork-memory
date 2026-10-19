"""Barcodes for the shop's yellow reduced-price stickers. See README.md."""


def sticker(code, pence):
    """The EAN-13 barcode for a reduced sticker: 29, the item's 5-digit code, the price in pence as 5 digits, and
    the check digit."""
    digits = f"29{code:0>5}{pence:05d}"
    return digits + str(check_digit(digits))
