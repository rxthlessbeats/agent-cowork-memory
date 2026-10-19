"""The office vending machines, as the operators' dashboard sees them.

A machine is a dict like the ones in MACHINES: its slots (each with the items left in it and how many
it holds when full), the coins in its coin box, when it last reported in, and when its door was
opened (None while it's shut).
"""
from datetime import datetime

ALERTS = ("low_stock", "coins_full", "offline", "door_open")
DOOR_OPEN_MINUTES = 10  # a door left open for longer than this gets the door_open alert

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


def alerts(machine, now):
    """The alerts to show on the dashboard for this machine at `now` (a datetime): a set of names from ALERTS."""
    raise NotImplementedError
