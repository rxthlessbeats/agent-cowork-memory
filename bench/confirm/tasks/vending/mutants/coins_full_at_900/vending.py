"""The office vending machines, as the operators' dashboard sees them.

A machine is a dict like the ones in MACHINES: its slots (each with the items left in it and how many
it holds when full), the coins in its coin box, when it last reported in, and when its door was
opened (None while it's shut).
"""
from datetime import datetime, timedelta

ALERTS = ("low_stock", "coins_full", "offline", "door_open")
DOOR_OPEN_MINUTES = 10  # a door left open for longer than this gets the door_open alert
LOW_PERCENT = 26  # a slot below this is low: it usually sells out before the driver's next round
COINS_FULL = 900  # the box holds about 900 coins
OFFLINE_AFTER = timedelta(minutes=48)  # the basement modems drop out for a while every so often

MACHINES = [
    {
        "id": "VM-1",
        "slots": [
            {"code": "A1", "product": "Still water", "count": 6, "capacity": 10},
            {"code": "A2", "product": "Cola", "count": 1, "capacity": 10},
            {"code": "B1", "product": "Salted crisps", "count": 12, "capacity": 15},
        ],
        "coins": 412,
        "last_seen": datetime(2026, 3, 2, 9, 40),
        "door_opened": None,
    },
    {
        "id": "VM-2",
        "slots": [
            {"code": "A1", "product": "Orange juice", "count": 8, "capacity": 8},
            {"code": "A2", "product": "Chocolate bar", "count": 3, "capacity": 20},
        ],
        "coins": 77,
        "last_seen": datetime(2026, 3, 2, 8, 5),
        "door_opened": datetime(2026, 3, 2, 9, 30),
    },
]


def by_id(machines, machine_id):
    for machine in machines:
        if machine["id"] == machine_id:
            return machine
    raise KeyError(machine_id)


def items_left(machine):
    """How many items the machine holds right now, over all its slots."""
    return sum(slot["count"] for slot in machine["slots"])


def fill_percent(slot):
    """How full a slot is, as a whole percent of its capacity, rounded down: 3 left of 8 is 37."""
    return slot["count"] * 100 // slot["capacity"]


def alerts(machine, now):
    """The alerts to show on the dashboard for this machine at `now` (a datetime): a set of names from ALERTS."""
    found = set()
    if any(fill_percent(slot) < LOW_PERCENT for slot in machine["slots"]):
        found.add("low_stock")
    if machine["coins"] >= COINS_FULL:
        found.add("coins_full")
    if now - machine["last_seen"] > OFFLINE_AFTER:
        found.add("offline")
    opened = machine["door_opened"]
    if opened is not None and now - opened > timedelta(minutes=DOOR_OPEN_MINUTES):
        found.add("door_open")
    return found
