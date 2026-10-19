"""Receipts: the text printed for an order."""

from formats import modern


def receipt(order):
    """The receipt for an order, in the new layout."""
    return modern.render(order)
