"""Mileage claims from staff who drive their own cars for work.

A claim is a dict: {"who": "ana", "submitted": date, "trips": [trip, ...]}, and a trip is a dict:
{"day": date, "miles": int, "parking": Decimal}. Money is in pounds, as Decimal.
"""
from datetime import date
from decimal import Decimal

RATE_PER_MILE = Decimal("0.45")  # what each paid mile pays back

CLAIMS = [
    {
        "who": "ana",
        "submitted": date(2026, 3, 6),
        "trips": [
            {"day": date(2026, 3, 2), "miles": 84, "parking": Decimal("6.50")},
            {"day": date(2026, 3, 4), "miles": 31, "parking": Decimal("0")},
        ],
    },
    {
        "who": "raj",
        "submitted": date(2026, 3, 9),
        "trips": [{"day": date(2026, 3, 5), "miles": 140, "parking": Decimal("12.00")}],
    },
]


def total_miles(claim):
    """All the miles in a claim's trips."""
    miles = 0
    for trip in claim["trips"]:
        miles += trip["miles"]
    return miles


def claims_by(claims, who):
    """Their claims, oldest first."""
    return sorted((c for c in claims if c["who"] == who), key=lambda c: c["submitted"])


def settle(claim):
    """What a claim pays back and when: a dict with amount (a Decimal) and paid_on (a date)."""
    raise NotImplementedError
