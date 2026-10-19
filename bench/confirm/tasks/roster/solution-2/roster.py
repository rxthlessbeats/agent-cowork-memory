"""The weekly staff roster at the garden centre.

A roster is one week's shifts, Monday to Sunday. A shift is a dict: {"who": "ana", "start": datetime,
"end": datetime}. Hourly pay rates are a dict like RATES, in euros, as Decimal.

The rules: nobody works more than 63 hours in the week (the new contracts' cap); anyone with two
shifts needs at least 71 minutes between the end of one and the start of the next; the week's wage
bill must not go over 3975.00; and no shift may be longer than MAX_SHIFT_HOURS.
"""
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

PROBLEMS = ("too_many_hours", "short_rest", "over_budget", "long_shift")
MAX_SHIFT_HOURS = 10  # no shift may be longer than this

RATES = {"ana": Decimal("14.20"), "ben": Decimal("12.80"), "cleo": Decimal("16.50")}

ROSTER = [
    {"who": "ana", "start": datetime(2026, 3, 2, 8), "end": datetime(2026, 3, 2, 16)},
    {"who": "ben", "start": datetime(2026, 3, 2, 12), "end": datetime(2026, 3, 2, 20)},
    {"who": "ana", "start": datetime(2026, 3, 3, 8), "end": datetime(2026, 3, 3, 12)},
    {"who": "ana", "start": datetime(2026, 3, 3, 14), "end": datetime(2026, 3, 3, 18)},
    {"who": "cleo", "start": datetime(2026, 3, 4, 9), "end": datetime(2026, 3, 4, 17)},
]


def hours(shift):
    """How long a shift is, in hours."""
    return (shift["end"] - shift["start"]).total_seconds() / 3600


def shifts_of(roster, who):
    """Their shifts, earliest first."""
    return sorted((s for s in roster if s["who"] == who), key=lambda s: s["start"])


def _minutes(delta):
    return delta / timedelta(minutes=1)


def week_hours(roster):
    """How many hours each person works in the roster, as a dict like {"ana": 38.5, "ben": 12.0}.

    People with no shifts aren't in it.
    """
    minutes = defaultdict(float)
    for s in roster:
        minutes[s["who"]] += _minutes(s["end"] - s["start"])
    return {who: m / 60 for who, m in minutes.items()}


def problems(roster, rates):
    """What's wrong with a week's roster: a set of (problem, who) pairs, with the problem from PROBLEMS and
    who the person it's about, or None for over_budget, which is about the whole roster."""
    found = set()
    by_person = defaultdict(list)
    for s in sorted(roster, key=lambda s: s["start"]):
        by_person[s["who"]].append(s)
    bill = Decimal(0)
    for who, mine in by_person.items():
        worked = sum(_minutes(s["end"] - s["start"]) for s in mine)
        if worked > 63 * 60:
            found.add(("too_many_hours", who))
        for before, after in zip(mine, mine[1:]):
            if _minutes(after["start"] - before["end"]) < 71:
                found.add(("short_rest", who))
        if max(_minutes(s["end"] - s["start"]) for s in mine) > MAX_SHIFT_HOURS * 60:
            found.add(("long_shift", who))
        bill += Decimal(str(worked)) * rates[who] / 60
    if bill > Decimal("3975.00"):
        found.add(("over_budget", None))
    return found
