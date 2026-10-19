"""Meeting room bookings.

A booking is a dict with the room's name and the datetimes it starts and
ends. Rooms can be booked back to back.
"""
from datetime import datetime

ROOMS = {"Fjord": 4, "Glacier": 8, "Tundra": 12}

BOOKINGS = [
    {"room": "Fjord", "start": datetime(2025, 5, 13, 9, 0), "end": datetime(2025, 5, 13, 10, 0)},
    {"room": "Tundra", "start": datetime(2025, 5, 13, 13, 30), "end": datetime(2025, 5, 13, 15, 0)},
]


def rooms_for(people):
    """Names of the rooms with a seat for each of these people, smallest first."""
    return sorted((room for room, seats in ROOMS.items() if seats >= people), key=ROOMS.get)


def bookings_of(bookings, room):
    """The bookings of one room, in list order."""
    return [b for b in bookings if b["room"] == room]
