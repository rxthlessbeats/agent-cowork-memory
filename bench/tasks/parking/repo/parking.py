"""Parking sessions at the office garage.

A session is a dict with the car's "plate" and the datetimes it came "in"
and went "out" (out is None while the car is still in the garage).
Parking costs 2.40 per started hour.
"""
from datetime import datetime

HOURLY_RATE = 240  # cents

SESSIONS = [
    {"plate": "KX-301", "in": datetime(2025, 3, 3, 8, 5), "out": datetime(2025, 3, 3, 17, 40)},
    {"plate": "LM-822", "in": datetime(2025, 3, 3, 9, 30), "out": datetime(2025, 3, 3, 9, 52)},
    {"plate": "KX-301", "in": datetime(2025, 3, 4, 8, 1), "out": None},
]


def still_parked(sessions):
    """Plates of the cars that are still in the garage."""
    return [s["plate"] for s in sessions if s["out"] is None]


def visits(sessions, plate):
    """How many times the car with this plate came in."""
    return sum(1 for s in sessions if s["plate"] == plate)
