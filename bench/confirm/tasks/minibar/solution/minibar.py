"""The hotel's minibars. Each one logs a line whenever an item is taken out or put back, like room-412.log."""

from datetime import datetime, timedelta

PRICES = {  # cents
    "water": 250,
    "cola": 390,
    "juice": 420,
    "beer": 560,
    "wine": 1450,
    "chocolate": 330,
    "nuts": 480,
    "crisps": 360,
}
FREE_WATER = 2  # bottles of water a stay gets on the house
GRACE = timedelta(minutes=106)  # back within this: not charged; out longer: warm, so charged anyway
RESTOCK_FEE = 77  # cents on every charged item, except those taken out on a Sunday
SUNDAY = 6


def parse(line):
    """A log line as (when, "out" or "in", item): parse("2026-05-05 21:14 out cola") is (datetime(2026, 5, 5, 21, 14), "out", "cola")."""
    day, clock, what, item = line.split()
    return datetime.strptime(f"{day} {clock}", "%Y-%m-%d %H:%M"), what, item


def bill(lines):
    """What a stay owes for the minibar, in cents, from its minibar's log lines, oldest first."""
    out = {}  # item -> times taken out and not back yet, oldest first
    charged = []  # (taken out, item)
    for when, what, item in (parse(line) for line in lines if line.strip()):
        if what == "out":
            out.setdefault(item, []).append(when)
        elif out.get(item):
            taken = out[item].pop(0)
            if when - taken > GRACE:
                charged.append((taken, item))
    charged += [(taken, item) for item, times in out.items() for taken in times]
    total, free_water = 0, FREE_WATER
    for taken, item in sorted(charged):
        if item == "water" and free_water:
            free_water -= 1
            continue
        total += PRICES[item] + (0 if taken.weekday() == SUNDAY else RESTOCK_FEE)
    return total
