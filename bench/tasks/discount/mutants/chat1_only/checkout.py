"""Checkout totals for the web shop, in EUR."""
from decimal import Decimal

# The discount codes marketing hands out, with the percent each one takes off.
CODES = {"SPRING10": 10, "WELCOME15": 15, "VIP25": 25}
MINIMUM = Decimal("30.00")
MAX_OFF = Decimal("20.00")


def percent_off(code):
    """The code's percent, ignoring case and spaces around it; 0 for no code or an unknown one."""
    return CODES.get((code or "").strip().upper(), 0)


def subtotal(cart):
    """Sum of the cart's (sku, unit_price, qty) lines. Unit prices are strings like "19.99"."""
    return sum((Decimal(price) * qty for _, price, qty in cart), Decimal("0.00"))


def total(cart, code=None):
    """What the customer pays for the cart, after the discount code if there is one."""
    full = subtotal(cart)
    if full < MINIMUM:
        return full
    # Gift cards are never discounted.
    discountable = subtotal([line for line in cart if not line[0].startswith("GIFT-")])
    off = min(discountable * percent_off(code) / 100, MAX_OFF)
    return full - off.quantize(Decimal("0.01"))


if __name__ == "__main__":
    import sys

    print(total([("ITEM", sys.argv[1], 1)], *sys.argv[2:]))
