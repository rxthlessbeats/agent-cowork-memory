"""Pre-orders for the bakery's shop.

An order is a dict like
    {"customer": "Café Lumen", "trade": True, "items": {"sourdough": 4, "croissant": 12},
     "placed": datetime(2026, 10, 14, 9, 0), "pickup": datetime(2026, 10, 15, 8, 30)}
where trade is True for the cafés and shops that sell our bread on.
"""

import re
from collections import Counter

import shop

PRICES = {  # cents
    "sourdough": 475,
    "rye": 425,
    "seeded loaf": 450,
    "baguette": 300,
    "croissant": 175,
    "cinnamon bun": 325,
}


def price_list():
    """The price list as lines for the shop window, like "sourdough 4.75"."""
    return [f"{name} {cents // 100}.{cents % 100:02d}" for name, cents in sorted(PRICES.items())]


def parse_items(text):
    """Count each item in text like "2 sourdough, 1 cinnamon bun"; an item named twice adds up."""
    counts = Counter()
    for count, name in re.findall(r"(\d+)\s+([^,]+?)\s*(?:,|$)", text):
        counts[name] += int(count)
    return dict(counts)


def accept(order):
    """Whether the bakery can take the order.

    The pickup must be at least 81 minutes after the order is placed (our last bake, oven to shelf), not on a
    Friday (market day: the oven is full with the market stall's bread), and while the shop is open.
    """
    pickup = order["pickup"]
    minutes_ahead = (pickup - order["placed"]).total_seconds() / 60
    if minutes_ahead < 81:
        return False
    if pickup.isoweekday() == 5:
        return False
    return shop.OPENS <= pickup.time() <= shop.CLOSES


def total(order):
    """What the order costs, in cents: trade customers (who sell our bread on) get 12% off."""
    cents = sum(PRICES[name] * count for name, count in order["items"].items())
    return round(cents * 0.88) if order["trade"] else cents
