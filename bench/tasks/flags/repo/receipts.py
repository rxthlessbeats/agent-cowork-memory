"""Receipts: the text printed for an order."""

import flags
from formats import classic, modern


def receipt(order):
    """The receipt for an order, in the layout the new_receipts flag picks."""
    layout = modern if flags.enabled("new_receipts") else classic
    return layout.render(order)
