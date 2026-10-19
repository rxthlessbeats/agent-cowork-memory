"""Pre-orders for the bakery's shop.

An order is a dict like
    {"customer": "Café Lumen", "trade": True, "items": {"sourdough": 4, "croissant": 12},
     "placed": datetime(2026, 10, 14, 9, 0), "pickup": datetime(2026, 10, 15, 8, 30)}
where trade is True for the cafés and shops that sell our bread on.
"""

from shop import CLOSES, OPENS

PRICES = {  # cents
    "sourdough": 475,
    "rye": 425,
    "seeded loaf": 450,
    "baguette": 300,
    "croissant": 175,
    "cinnamon bun": 325,
}

TRADE_PERCENT_OFF = 12  # agreed with the cafés and shops that sell our bread on


def price_list():
    """The price list as lines for the shop window, like "sourdough 4.75"."""
    return [f"{name} {cents // 100}.{cents % 100:02d}" for name, cents in sorted(PRICES.items())]


def parse_items(text):
    """Items as people write them: parse_items("2 sourdough, 1 cinnamon bun") == {"sourdough": 2, "cinnamon bun": 1}."""
    items = {}
    for part in text.split(","):
        count, name = part.strip().split(" ", 1)
        name = name.strip()
        items[name] = items.get(name, 0) + int(count)
    return items


def accept(order):
    """Whether the bakery can take the order."""
    pickup = order["pickup"]
    return pickup > order["placed"] and OPENS <= pickup.time() < CLOSES


def total(order):
    """What the order costs, in cents."""
    full = sum(PRICES[name] * count for name, count in order["items"].items())
    if order["trade"]:
        return full - full * TRADE_PERCENT_OFF // 100
    return full
