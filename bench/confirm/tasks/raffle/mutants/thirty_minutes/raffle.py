"""Ticket sales for the club's raffle.

A draw is a dict: "at" (when it is drawn, a datetime) and "sold" (how many tickets each buyer has, by name).
"""

from datetime import datetime, timedelta

SALES_OPEN_DAYS = 14  # tickets for a draw go on sale this many days before it
MAX_PER_BUYER = 58  # the cap in our gaming licence, counting tickets already held
MAX_PER_DRAW = 3580  # the numbered tickets the printer makes for each draw
SALES_CLOSE = timedelta(minutes=30)  # so the stubs can be counted

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


def tickets_held(draw, buyer):
    """How many tickets buyer has for the draw; names match ignoring case and extra spaces.

    tickets_held({"at": ..., "sold": {"Ana Silva": 12}}, "ana  SILVA") == 12
    """
    def key(name):
        return " ".join(name.split()).casefold()

    return sum(n for name, n in draw["sold"].items() if key(name) == key(buyer))


def can_buy(draw, buyer, count, now):
    """Whether a sale of count tickets to buyer may go through at now."""
    return (
        count > 0
        and draw["at"] - timedelta(days=SALES_OPEN_DAYS) <= now <= draw["at"] - SALES_CLOSE
        and tickets_held(draw, buyer) + count <= MAX_PER_BUYER
        and sold_total(draw) + count <= MAX_PER_DRAW
    )
