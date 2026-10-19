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


def _same(a, b):
    return a.lower().split() == b.lower().split()


def tickets_held(draw, buyer):
    """How many tickets buyer already has for the draw: 0 for someone with none.

    Names match without caring about case or extra spaces, so "ana  SILVA" finds Ana Silva's tickets.
    """
    return sum(count for name, count in draw["sold"].items() if _same(name, buyer))


def can_buy(draw, buyer, count, now):
    """Whether a sale of `count` tickets to `buyer` at `now` may go through.

    Sales open SALES_OPEN_DAYS before the draw and stop 65 minutes before it (the auditor counts the stubs). Nobody
    holds more than 58 tickets for a draw (our licence), and a draw has 3580 tickets at most (what gets printed).
    """
    minutes_left = (draw["at"] - now).total_seconds() / 60
    if minutes_left < 65 or minutes_left > SALES_OPEN_DAYS * 24 * 60:
        return False
    if tickets_held(draw, buyer) + count > 58:
        return False
    return sold_total(draw) + count <= 3580
