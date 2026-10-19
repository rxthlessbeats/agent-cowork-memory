"""Meeting room bookings.

A booking is a dict with the room's name and the datetimes it starts and
ends. Two bookings of the same room need at least 10 minutes between them,
for cleaning; a booking lies between 8:30 and 17:45 and lasts at most 90 minutes.
"""
from datetime import datetime, time, timedelta

ROOMS = {"Fjord": 4, "Glacier": 8, "Tundra": 12}

BOOKINGS = [
    {"room": "Fjord", "start": datetime(2025, 5, 13, 9, 0), "end": datetime(2025, 5, 13, 10, 0)},
    {"room": "Tundra", "start": datetime(2025, 5, 13, 13, 30), "end": datetime(2025, 5, 13, 15, 0)},
]

CLEANING_GAP = timedelta(minutes=10)
FIRST_START = time(8, 30)
LAST_END = time(17, 45)
LONGEST = timedelta(minutes=90)


def rooms_for(people):
    """Names of the rooms with a seat for each of these people, smallest first."""
    return sorted((room for room, seats in ROOMS.items() if seats >= people), key=ROOMS.get)


def bookings_of(bookings, room):
    """The bookings of one room, in list order."""
    return [b for b in bookings if b["room"] == room]


def clashes(bookings, room, start, end):
    """The bookings of room that overlap start to end, in list order. Bookings that only touch, one ending
    exactly when the other starts, don't overlap."""
    return [b for b in bookings_of(bookings, room) if not (b["end"] <= start or end <= b["start"])]


def book(bookings, room, start, end):
    """Add the booking and return True if the office rules allow it; otherwise return False and leave bookings alone."""
    if not start < end or end - start > LONGEST:
        return False
    if start.date() != end.date() or start.time() < FIRST_START or end.time() > LAST_END:
        return False
    for other in bookings_of(bookings, room):
        # The time between the two bookings, negative when they overlap.
        if max(other["start"] - end, start - other["end"]) < CLEANING_GAP:
            return False
    bookings.append({"room": room, "start": start, "end": end})
    return True
