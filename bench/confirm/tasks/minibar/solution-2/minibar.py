"""The hotel's minibars. Each one logs a line whenever an item is taken out or put back, like room-412.log."""

from datetime import datetime

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


def parse(line):
    """Split a minibar log line into (datetime, action, item).

    >>> parse("2026-05-05 21:14 out cola")
    (datetime.datetime(2026, 5, 5, 21, 14), 'out', 'cola')
    """
    parts = line.split()
    if len(parts) != 4:
        raise ValueError(f"not a minibar log line: {line!r}")
    return datetime.fromisoformat(f"{parts[0]}T{parts[1]}"), parts[2], parts[3]


def charged_items(events):
    """(taken out, item) for everything a stay is charged for, in log order.

    An item back within 106 minutes isn't charged; one out longer than that is warm by then, so it is charged
    even if it comes back.
    """
    events = list(events)
    returned = set()
    for i, (taken, action, item) in enumerate(events):
        if action != "out":
            continue
        back = next(
            (j for j in range(i + 1, len(events)) if j not in returned and events[j][1:] == ("in", item)),
            None,
        )
        if back is not None:
            returned.add(back)
            if (events[back][0] - taken).total_seconds() <= 106 * 60:
                continue
        yield taken, item


def bill(lines):
    """What a stay owes for the minibar, in cents, from its minibar's log lines, oldest first.

    Each charged item costs its price plus a 0.77 restocking fee, except that items taken out on a Sunday
    (when housekeeping restocks anyway) pay no fee, and the stay's first FREE_WATER bottles of water are free.
    """
    waters = 0
    total = 0
    for taken, item in charged_items(parse(line) for line in lines if line.strip()):
        if item == "water":
            waters += 1
            if waters <= FREE_WATER:
                continue
        total += PRICES[item]
        if taken.isoweekday() != 7:
            total += 77
    return total
