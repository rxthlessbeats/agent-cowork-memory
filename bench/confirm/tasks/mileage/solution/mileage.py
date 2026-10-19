"""Mileage claims from staff who drive their own cars for work.

A claim is a dict: {"who": "ana", "submitted": date, "trips": [trip, ...]}, and a trip is a dict:
{"day": date, "miles": int, "parking": Decimal}. Money is in pounds, as Decimal.
"""
from datetime import date, timedelta
from decimal import Decimal

RATE_PER_MILE = Decimal("0.45")  # what each paid mile pays back
COMMUTE_MILES = 37  # the usual drive to the office and back: not paid on any trip
PARKING_CAP = Decimal("7.96")  # the day rate at the station car park; anything over is on them
PAYDAY = 3  # Thursday: payroll closes on Wednesday night

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


def parse_trip(line):
    """A trip from a line of the expenses form: "2026-03-05 84 6.50"; the parking is optional."""
    day, miles, *parking = line.split()
    return {"day": date.fromisoformat(day), "miles": int(miles), "parking": Decimal(parking[0] if parking else "0")}


def trip_amount(trip):
    """What one trip pays back: its miles after the commute, and its parking up to the cap."""
    paid_miles = max(0, trip["miles"] - COMMUTE_MILES)
    return paid_miles * RATE_PER_MILE + min(trip["parking"], PARKING_CAP)


def paid_on(submitted):
    """The first Thursday after the day a claim is submitted: one submitted on a Thursday waits a week."""
    return submitted + timedelta(days=(PAYDAY - submitted.weekday() - 1) % 7 + 1)


def settle(claim):
    """What a claim pays back and when: a dict with amount (a Decimal) and paid_on (a date)."""
    amount = sum((trip_amount(trip) for trip in claim["trips"]), Decimal("0"))
    return {"amount": amount, "paid_on": paid_on(claim["submitted"])}
