"""Prices for the shop's checkout."""

import re


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
    if re.fullmatch(r"\d+%", coupon):
        return "percent"
    if re.fullmatch(r"\d+\.\d\d", coupon):
        return "amount"
    raise ValueError(f"not a coupon: {coupon!r}")


def apply_coupon(price, coupon):
    """The price after a coupon, rounded to the cent: apply_coupon_float, finished for amount coupons."""
    if coupon_kind(coupon) == "amount":
        return round(max(float(price) - float(coupon), 0.0), 2)
    return apply_coupon_float(price, coupon)
