"""Deliveries for the flower shop's web orders. Amounts are in cents.

The web shop writes one line per order: the date and time it was placed, then its subtotal, like
"2026-10-17 15:42 45.99".
"""

from shop import SAME_DAY_CUTOFF


def delivery_fee(subtotal):
    """What delivery costs for an order with this subtotal, in cents."""
    raise NotImplementedError


def delivery_day(ordered_at):
    """The day an order placed at `ordered_at` (a datetime) goes out, as a date."""
    raise NotImplementedError
