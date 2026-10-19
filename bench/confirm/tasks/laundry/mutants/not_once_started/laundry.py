"""The booking sheet for the laundry room in the basement.

There is one washing machine. A booking is a dict: {"flat": "3B", "start": datetime}. Slots are two
hours long, and they start at the hours in SLOT_HOURS every day.
"""
from datetime import datetime, timedelta

SLOT_HOURS = (7, 9, 11, 13, 15, 17, 19)
SLOT_LENGTH = timedelta(hours=2)
MAX_UPCOMING = 2  # bookings a flat may hold at once that haven't started yet
CLOSED_ON = 4  # Friday: the caretaker cleans and services the machine
BOOK_AHEAD = timedelta(hours=66)  # so the Monday 7:00 slot opens on Friday at 13:00
LATE = timedelta(0)  # a slot can't be booked once it has started

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


def slot_start(when):
    """The start of the slot that when falls in, or None outside every slot: 10:15 is in the 9:00 slot."""
    for hour in SLOT_HOURS:
        start = when.replace(hour=hour, minute=0, second=0, microsecond=0)
        if start <= when < start + SLOT_LENGTH:
            return start
    return None


def can_book(bookings, flat, start, now):
    """Whether flat may book the slot starting at start, asking at now (both datetimes)."""
    if slot_start(start) != start or start.weekday() == CLOSED_ON:
        return False
    if start - now > BOOK_AHEAD or now - start > LATE:
        return False
    if is_taken(bookings, start):
        return False
    upcoming = [b for b in bookings_of(bookings, flat) if b["start"] > now]
    return len(upcoming) < MAX_UPCOMING
