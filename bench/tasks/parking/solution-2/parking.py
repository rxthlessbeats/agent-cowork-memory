"""Parking sessions at the office garage.

A session is a dict with the car's "plate" and the datetimes it came "in"
and went "out" (out is None while the car is still in the garage).
Parking costs 2.40 per started hour.
"""
from datetime import datetime, timedelta

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


def minutes(session):
    """Whole minutes the car was parked, a started minute counting as a full one.

    Raises ValueError for a car that hasn't left yet (its "out" is None).
    """
    if session.get("out") is None:
        raise ValueError(f"{session['plate']} is still in the garage")
    # Floor division of the negated stay rounds up to the next whole minute.
    return -((session["in"] - session["out"]) // timedelta(minutes=1))


BLOCK = 20  # minutes: every started block is charged in full
BLOCK_PRICE = 80  # cents, replacing the hourly rate
SESSION_CAP = 1680  # cents, however long the stay (raised from 13.60)
SUNDAY = 7  # isoweekday


def fee(session):
    """What a finished session costs, in cents; a car that came in on a Sunday parks free."""
    if session["in"].isoweekday() == SUNDAY:
        return 0
    blocks = -(-minutes(session) // BLOCK)
    return min(blocks * BLOCK_PRICE, SESSION_CAP)
