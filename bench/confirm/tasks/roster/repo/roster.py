"""The weekly staff roster at the garden centre.

A roster is one week's shifts, Monday to Sunday. A shift is a dict: {"who": "ana", "start": datetime,
"end": datetime}. Hourly pay rates are a dict like RATES, in euros, as Decimal.
"""
from datetime import datetime
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


def problems(roster, rates):
    """What's wrong with a week's roster: a set of (problem, who) pairs, with the problem from PROBLEMS and
    who the person it's about, or None for over_budget, which is about the whole roster."""
    raise NotImplementedError
