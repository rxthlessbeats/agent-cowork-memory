"""Bookings for the freight elevator, which residents reserve when they move in or out.

A booking is a dict like {"flat": "4B", "start": datetime(2026, 10, 20, 9, 30), "minutes": 90}.
"""

from datetime import datetime

BOOKINGS = [
    {"flat": "4B", "start": datetime(2026, 10, 20, 9, 30), "minutes": 90},
    {"flat": "12A", "start": datetime(2026, 10, 21, 13, 0), "minutes": 120},
    {"flat": "7C", "start": datetime(2026, 10, 23, 15, 15), "minutes": 45},
]


def flats(bookings):
    """The flats with a booking, each once, sorted."""
    return sorted({b["flat"] for b in bookings})
