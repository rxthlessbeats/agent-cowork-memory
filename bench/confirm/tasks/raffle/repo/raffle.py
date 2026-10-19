"""Ticket sales for the club's raffle.

A draw is a dict: "at" (when it is drawn, a datetime) and "sold" (how many tickets each buyer has, by name).
"""

from datetime import datetime

SALES_OPEN_DAYS = 14  # tickets for a draw go on sale this many days before it

DRAWS = [
    {"at": datetime(2026, 3, 6, 20, 0), "sold": {"Ana Silva": 12, "Ben Okafor": 3, "Chloe Martin": 25}},
    {"at": datetime(2026, 3, 13, 20, 0), "sold": {"Ben Okafor": 5}},
]


def sold_total(draw):
    """How many tickets have been sold for the draw."""
    total = 0
    for name in draw["sold"]:
        total += draw["sold"][name]
    return total
