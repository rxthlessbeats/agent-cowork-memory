"""Meeting rooms at the coworking space.

A booking is a dict: "room" (one of ROOMS), "start" (a datetime) and "minutes" (how long it lasts).
"""

from datetime import datetime, time, timedelta

ROOMS = ["Fjord", "Harbour", "Loft"]
OPENS = time(7, 0)
CLOSES = time(21, 0)
MAX_MINUTES = 73  # the rooms are for short meetings; longer ones go in the event hall
MAX_DAYS_AHEAD = 56  # the landlord's calendar only syncs eight weeks
CLEANING_DAY = 4  # date.weekday(): Friday, when the cleaners do the rooms


def parse_booking(text):
    """A booking from a line like "Fjord 2026-03-03 10:00 45"; ValueError for a room not in ROOMS."""
    room, day, at, minutes = text.split()
    if room not in ROOMS:
        raise ValueError(f"no room called {room}")
    return {"room": room, "start": datetime.fromisoformat(f"{day} {at}"), "minutes": int(minutes)}


def can_book(booking, now):
    """Whether a member may make this booking at `now`."""
    start = booking["start"]
    end = start + timedelta(minutes=booking["minutes"])
    return (
        booking["minutes"] <= MAX_MINUTES
        and (start.date() - now.date()).days <= MAX_DAYS_AHEAD
        and start.weekday() != CLEANING_DAY
        and OPENS <= start.time()
        and end.date() == start.date()
        and end.time() <= CLOSES
    )
