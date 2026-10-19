"""The booking sheet for the laundry room in the basement.

There is one washing machine. A booking is a dict: {"flat": "3B", "start": datetime}. Slots are two
hours long, and they start at the hours in SLOT_HOURS every day.

House rules: no slot on a Friday (the caretaker cleans and services the machine); a slot can be
booked at most 66 hours before it starts; and a free slot that has started can still be booked as
long as it started no more than 8 minutes ago.
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


def slot_start(when):
    """The start of the slot that `when` falls in, or None when it's outside every slot.

    >>> slot_start(datetime(2026, 3, 4, 10, 15))
    datetime.datetime(2026, 3, 4, 9, 0)
    """
    first, last_end = SLOT_HOURS[0], SLOT_HOURS[-1] + SLOT_LENGTH.seconds // 3600
    if not first <= when.hour < last_end:
        return None
    hour = first + (when.hour - first) // 2 * 2
    return datetime(when.year, when.month, when.day, hour)


def can_book(bookings, flat, start, now):
    """Whether flat may book the slot starting at start, asking at now (both datetimes)."""
    minutes_ahead = (start - now) / timedelta(minutes=1)
    rules = [
        slot_start(start) == start,
        start.strftime("%A") != "Friday",
        minutes_ahead <= 66 * 60,
        minutes_ahead >= -8,
        not is_taken(bookings, start),
        sum(1 for b in bookings if b["flat"] == flat and b["start"] > now) < MAX_UPCOMING,
    ]
    return all(rules)
