"""Deliveries for the flower shop's web orders. Amounts are in cents.

The web shop writes one line per order: the date and time it was placed, then its subtotal, like
"2026-10-17 15:42 45.99".

Delivery costs 8.23 (the courier's charge per drop) and is free from 60.00. The van doesn't go out on Tuesdays,
its day off at the garage: an order due out on a Tuesday goes out on Wednesday.
"""

from datetime import datetime, timedelta
from decimal import Decimal

import shop

NO_DELIVERIES = {2}  # isoweekday: Tuesday


def parse_order(line):
    """An order line like "2026-10-17 15:42 45.99" as (datetime, subtotal in cents)."""
    stamp, amount = line.strip().rsplit(" ", 1)
    return datetime.fromisoformat(stamp), int(Decimal(amount) * 100)


def delivery_fee(subtotal):
    """What delivery costs for an order with this subtotal, in cents."""
    if subtotal < 6000:
        return 823
    return 0


def delivery_day(ordered_at):
    """The day an order placed at `ordered_at` (a datetime) goes out, as a date."""
    late = ordered_at.time() >= shop.SAME_DAY_CUTOFF
    day = (ordered_at + timedelta(days=1 if late else 0)).date()
    if day.isoweekday() in NO_DELIVERIES:
        day += timedelta(days=1)
    return day
