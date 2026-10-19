"""Stock levels for the workshop store room.

Each item records how many units are on hand, how many we use per day on
average, and how many days the supplier takes to deliver.
"""
import math

ITEMS = {
    "bolts": {"on_hand": 120, "daily_use": 15, "lead_days": 4},
    "washers": {"on_hand": 900, "daily_use": 20, "lead_days": 4},
    "glue": {"on_hand": 6, "daily_use": 1, "lead_days": 10},
    "sandpaper": {"on_hand": 30, "daily_use": 0, "lead_days": 7},
    "tape": {"on_hand": 0, "daily_use": 2, "lead_days": 3},
}

SAFETY_DAYS = 3  # reorder while the stock still lasts the lead time plus this
TARGET_DAYS = 21  # an order tops the stock up to this many days of use
DELIVERY_CAP = 500  # the most units of one item the store room takes per delivery
PHASED_OUT = "x-"  # items named like this are never reordered


def total_units(items):
    return sum(item["on_hand"] for item in items.values())


def used_up(items):
    """Names of items with nothing left on hand."""
    return sorted(name for name, item in items.items() if item["on_hand"] == 0)


def days_left(item):
    """How many days the stock on hand lasts at the current daily use; float("inf") when nobody uses it."""
    use = item["daily_use"]
    return item["on_hand"] / use if use else math.inf


def reorder(items):
    """{name: units to order} for each item that needs reordering."""
    orders = {}
    for name, item in items.items():
        if name.startswith(PHASED_OUT):
            continue
        # In units rather than days: the stock that lasts the lead time plus the safety buffer.
        reorder_point = item["daily_use"] * (item["lead_days"] + SAFETY_DAYS)
        if item["on_hand"] >= reorder_point:
            continue
        units = min(TARGET_DAYS * item["daily_use"] - item["on_hand"], DELIVERY_CAP)
        if units > 0:
            orders[name] = units
    return orders
