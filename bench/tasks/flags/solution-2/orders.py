"""Orders: an id and lines, each line a dict with name, qty and cents (the price of one)."""


def subtotal(order):
    """The order's value in cents, before any tax."""
    return sum(line["qty"] * line["cents"] for line in order["lines"])


def item_count(order):
    """How many items the order has: each line counts its quantity, so 2 mugs and a teapot are 3."""
    count = 0
    for line in order["lines"]:
        count += line["qty"]
    return count
