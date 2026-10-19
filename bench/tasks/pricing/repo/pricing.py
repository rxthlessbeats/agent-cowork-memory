"""Prices for the shop's checkout."""


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
