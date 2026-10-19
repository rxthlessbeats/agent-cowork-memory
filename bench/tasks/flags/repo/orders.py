"""Orders: an id and lines, each line a dict with name, qty and cents (the price of one)."""


def subtotal(order):
    """The order's value in cents, before any tax."""
    return sum(line["qty"] * line["cents"] for line in order["lines"])
