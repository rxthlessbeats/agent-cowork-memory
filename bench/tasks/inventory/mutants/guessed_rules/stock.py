"""Stock levels for the workshop store room.

Each item records how many units are on hand, how many we use per day on
average, and how many days the supplier takes to deliver.
"""

ITEMS = {
    "bolts": {"on_hand": 120, "daily_use": 15, "lead_days": 4},
    "washers": {"on_hand": 900, "daily_use": 20, "lead_days": 4},
    "glue": {"on_hand": 6, "daily_use": 1, "lead_days": 10},
    "sandpaper": {"on_hand": 30, "daily_use": 0, "lead_days": 7},
    "tape": {"on_hand": 0, "daily_use": 2, "lead_days": 3},
}


def total_units(items):
    return sum(item["on_hand"] for item in items.values())


def used_up(items):
    """Names of items with nothing left on hand."""
    return sorted(name for name, item in items.items() if item["on_hand"] == 0)


def days_left(item):
    if item["daily_use"] == 0:
        return float("inf")
    return item["on_hand"] / item["daily_use"]


COVER_DAYS = 30  # order a month's worth


def reorder(items):
    orders = {}
    for name, item in items.items():
        # Reorder when the stock runs out before a new delivery could arrive.
        if days_left(item) < item["lead_days"]:
            orders[name] = COVER_DAYS * item["daily_use"] - item["on_hand"]
    return orders
