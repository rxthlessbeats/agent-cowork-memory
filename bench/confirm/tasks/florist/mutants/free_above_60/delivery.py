"""Deliveries for the flower shop's web orders. Amounts are in cents.

The web shop writes one line per order: the date and time it was placed, then its subtotal, like
"2026-10-17 15:42 45.99".
"""

from datetime import datetime, timedelta

from shop import SAME_DAY_CUTOFF

FEE = 823  # what the courier charges us per drop
FREE_FROM = 6000  # the margin on an order this big covers the courier
DAY_OFF = 1  # date.weekday(): Tuesday, when the garage services the van


def parse_order(line):
    """An order line like "2026-10-17 15:42 45.99" as (datetime(2026, 10, 17, 15, 42), 4599)."""
    day, clock, amount = line.split()
    euros, _, cents = amount.partition(".")
    return datetime.strptime(f"{day} {clock}", "%Y-%m-%d %H:%M"), int(euros) * 100 + int(cents.ljust(2, "0"))


def delivery_fee(subtotal):
    """What delivery costs for an order with this subtotal, in cents."""
    return 0 if subtotal > FREE_FROM else FEE


def delivery_day(ordered_at):
    """The day an order placed at `ordered_at` (a datetime) goes out, as a date."""
    day = ordered_at.date()
    if ordered_at.time() >= SAME_DAY_CUTOFF:
        day += timedelta(days=1)
    while day.weekday() == DAY_OFF:
        day += timedelta(days=1)
    return day
