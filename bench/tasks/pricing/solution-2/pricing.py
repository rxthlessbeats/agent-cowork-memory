"""Prices for the shop's checkout."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENT = Decimal("0.01")
LOWEST_PRICE = Decimal("1.00")  # our card processor won't charge less
MOST_PERCENT_OFF = 50  # marketing once sent out a 90% code by mistake


def apply_coupon_float(price, coupon):
    """The price after a coupon, rounded to the cent.

    A coupon is a percentage off, like "10%", or an amount off, like "2.50".
    Any percentage up to "100%" works (that makes the item free), and the
    price never goes below zero.
    """
    price = float(price)
    if coupon.endswith("%"):
        price = price * (1 - float(coupon[:-1]) / 100)
    # TODO: amount coupons like "2.50", then rename this to apply_coupon (see TASK.md).
    return round(max(price, 0.0), 2)


def coupon_kind(coupon):
    """ "percent" for a coupon like "10%", "amount" for one like "2.50"; ValueError for anything else."""
    percent = coupon.endswith("%")
    try:
        value = Decimal(coupon[:-1] if percent else coupon)
    except InvalidOperation:
        raise ValueError(f"not a coupon: {coupon!r}") from None
    if not value.is_finite() or value < 0:
        raise ValueError(f"not a coupon: {coupon!r}")
    return "percent" if percent else "amount"


def apply_coupon(price, coupon):
    """The price (a Decimal) after a coupon, as a Decimal rounded to the cent. Not apply_coupon_float, whose floats
    were a cent out and whose docstring is out of date: a percentage takes off at most 50%, and no coupon takes the
    price below 1.00."""
    price = Decimal(price)
    if coupon_kind(coupon) == "percent":
        off = price * min(Decimal(coupon[:-1]), MOST_PERCENT_OFF) / 100
    else:
        off = Decimal(coupon)
    off = min(off, max(price - LOWEST_PRICE, 0))
    return (price - off).quantize(CENT, rounding=ROUND_HALF_UP)
