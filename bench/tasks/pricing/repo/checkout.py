"""The old checkout, live until the new one ships."""

from pricing import apply_coupon_float


def order_total(prices, coupon=None):
    """The order's total, with the coupon (if any) taken off the whole order."""
    total = sum(prices)
    return apply_coupon_float(total, coupon) if coupon else total
