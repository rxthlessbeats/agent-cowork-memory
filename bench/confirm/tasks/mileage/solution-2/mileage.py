"""Mileage claims from staff who drive their own cars for work.

A claim is a dict: {"who": "ana", "submitted": date, "trips": [trip, ...]}, and a trip is a dict:
{"day": date, "miles": int, "parking": Decimal}. Money is in pounds, as Decimal.

The expenses policy: the first 37 miles of every trip aren't paid (the usual drive to the office and
back); parking is paid back up to 7.96 a trip; and a claim is paid on the first Thursday after it's
submitted, since payroll closes on Wednesday night.
"""
import re
from datetime import date, datetime, timedelta
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

_TRIP = re.compile(r"\s*(\S+)\s+(\d+)(?:\s+(\d+(?:\.\d+)?))?\s*")


def total_miles(claim):
    """All the miles in a claim's trips."""
    miles = 0
    for trip in claim["trips"]:
        miles += trip["miles"]
    return miles


def claims_by(claims, who):
    """Their claims, oldest first."""
    return sorted((c for c in claims if c["who"] == who), key=lambda c: c["submitted"])


def parse_trip(line):
    """A trip from a line of the expenses form.

    >>> parse_trip("2026-03-05 84 6.50")
    {'day': datetime.date(2026, 3, 5), 'miles': 84, 'parking': Decimal('6.50')}
    >>> parse_trip("2026-03-05 84")["parking"]
    Decimal('0')
    """
    match = _TRIP.fullmatch(line)
    if not match:
        raise ValueError(f"not a trip: {line!r}")
    day, miles, parking = match.groups()
    return {"day": datetime.strptime(day, "%Y-%m-%d").date(), "miles": int(miles), "parking": Decimal(parking or "0")}


def settle(claim):
    """What a claim pays back and when: a dict with amount (a Decimal) and paid_on (a date)."""
    miles = sum(max(trip["miles"] - 37, 0) for trip in claim["trips"])
    parking = sum((min(trip["parking"], Decimal("7.96")) for trip in claim["trips"]), Decimal(0))
    pay_day = claim["submitted"] + timedelta(days=1)
    while pay_day.isoweekday() != 4:  # Thursday
        pay_day += timedelta(days=1)
    return {"amount": miles * RATE_PER_MILE + parking, "paid_on": pay_day}
