"""The office vending machines, as the operators' dashboard sees them.

A machine is a dict like the ones in MACHINES: its slots (each with the items left in it and how many
it holds when full), the coins in its coin box, when it last reported in, and when its door was
opened (None while it's shut).
"""
from datetime import datetime
from fractions import Fraction

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


def fill_percent(slot):
    """How full a slot is, as a whole percent of its capacity, rounded down.

    >>> fill_percent({"code": "A1", "product": "Cola", "count": 3, "capacity": 8})
    37
    """
    whole, _ = divmod(100 * slot["count"], slot["capacity"])
    return whole


def _minutes_since(now, then):
    return (now - then).total_seconds() / 60


def alerts(machine, now):
    """The alerts to show on the dashboard for this machine at `now` (a datetime): a set of names from ALERTS.

    low_stock: a slot is below 26% full, so it would sell out before the driver's next round.
    coins_full: 810 coins or more; the box holds about 900 but jams before it's full.
    offline: last reported in more than 48 minutes ago (the basement modems drop out now and then).
    door_open: the door has been open longer than DOOR_OPEN_MINUTES.
    """
    door = machine.get("door_opened")
    rules = {
        "low_stock": any(Fraction(s["count"], s["capacity"]) < Fraction(26, 100) for s in machine["slots"]),
        "coins_full": machine["coins"] >= 810,
        "offline": _minutes_since(now, machine["last_seen"]) > 48,
        "door_open": door is not None and _minutes_since(now, door) > DOOR_OPEN_MINUTES,
    }
    return {name for name in ALERTS if rules[name]}
