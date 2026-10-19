"""Checkout totals for the web shop, in EUR."""
from decimal import Decimal

# The discount codes marketing hands out, with the percent each one takes off.
CODES = {"SPRING10": 10, "WELCOME15": 15, "VIP25": 25}
MIN_CENTS = 2500  # codes work on a subtotal of 25.00 or more: the vouchers already mailed say so
MAX_OFF_CENTS = 2000  # no code ever takes more than 20.00 off


def percent_off(code):
    """The code's percent off, ignoring case and spaces around it: percent_off(" spring10 ") == 10.

    No code, or one that isn't in CODES, gives 0.
    """
    if not code:
        return 0
    return CODES.get(code.strip().upper(), 0)


def subtotal(cart):
    """Sum of the cart's (sku, unit_price, qty) lines. Unit prices are strings like "19.99"."""
    return sum((Decimal(price) * qty for _, price, qty in cart), Decimal("0.00"))


def _cents(cart):
    return int(subtotal(cart) * 100)


def total(cart, code=None):
    """What the customer pays for the cart, after the discount code if there is one.

    Below a 25.00 subtotal the customer pays it in full. Gift cards (SKUs starting with GIFT-) are never
    discounted, and the discount stops at 20.00.
    """
    pay = _cents(cart)
    percent = percent_off(code)
    if percent and pay >= MIN_CENTS:
        discountable = _cents([line for line in cart if not line[0].startswith("GIFT-")])
        pay -= min((discountable * percent + 50) // 100, MAX_OFF_CENTS)  # half a cent rounds up
    return Decimal(pay).scaleb(-2)


if __name__ == "__main__":
    import sys

    print(total([("ITEM", sys.argv[1], 1)], *sys.argv[2:]))
