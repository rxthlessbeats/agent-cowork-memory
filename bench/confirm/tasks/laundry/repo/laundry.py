"""The booking sheet for the laundry room in the basement.

There is one washing machine. A booking is a dict: {"flat": "3B", "start": datetime}. Slots are two
hours long, and they start at the hours in SLOT_HOURS every day.
"""
from datetime import datetime, timedelta

SLOT_HOURS = (7, 9, 11, 13, 15, 17, 19)
SLOT_LENGTH = timedelta(hours=2)
MAX_UPCOMING = 2  # bookings a flat may hold at once that haven't started yet

BOOKINGS = [
    {"flat": "1A", "start": datetime(2026, 3, 2, 9)},
    {"flat": "3B", "start": datetime(2026, 3, 2, 11)},
    {"flat": "1A", "start": datetime(2026, 3, 4, 17)},
]


def bookings_of(bookings, flat):
    """The flat's bookings, earliest first."""
    return sorted((b for b in bookings if b["flat"] == flat), key=lambda b: b["start"])


def is_taken(bookings, start):
    """Whether the slot starting at start is already booked."""
    return any(b["start"] == start for b in bookings)


def can_book(bookings, flat, start, now):
    """Whether flat may book the slot starting at start, asking at now (both datetimes)."""
    raise NotImplementedError
