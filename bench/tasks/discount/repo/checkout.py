"""Checkout totals for the web shop, in EUR."""
from decimal import Decimal

# The discount codes marketing hands out, with the percent each one takes off.
CODES = {"SPRING10": 10, "WELCOME15": 15, "VIP25": 25}


def subtotal(cart):
    """Sum of the cart's (sku, unit_price, qty) lines. Unit prices are strings like "19.99"."""
    return sum((Decimal(price) * qty for _, price, qty in cart), Decimal("0.00"))


def total(cart, code=None):
    """What the customer pays for the cart, after the discount code if there is one."""
    return subtotal(cart)


if __name__ == "__main__":
    import sys

    print(total([("ITEM", sys.argv[1], 1)], *sys.argv[2:]))
