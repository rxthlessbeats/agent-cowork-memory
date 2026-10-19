"""Pre-orders for the bakery's shop.

An order is a dict like
    {"customer": "Café Lumen", "trade": True, "items": {"sourdough": 4, "croissant": 12},
     "placed": datetime(2026, 10, 14, 9, 0), "pickup": datetime(2026, 10, 15, 8, 30)}
where trade is True for the cafés and shops that sell our bread on.
"""

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
