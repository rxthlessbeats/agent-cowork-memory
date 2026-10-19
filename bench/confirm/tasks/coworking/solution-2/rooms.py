"""Meeting rooms at the coworking space.

A booking is a dict: "room" (one of ROOMS), "start" (a datetime) and "minutes" (how long it lasts).
"""

from datetime import datetime, time, timedelta

ROOMS = ["Fjord", "Harbour", "Loft"]
OPENS = time(7, 0)
CLOSES = time(21, 0)


def parse_booking(text):
    """A booking from a line like "Fjord 2026-03-03 10:00 45"; ValueError for a room not in ROOMS."""
    parts = text.split()
    if len(parts) != 4 or parts[0] not in ROOMS:
        raise ValueError(f"not a booking: {text!r}")
    return {
        "room": parts[0],
        "start": datetime.strptime(f"{parts[1]} {parts[2]}", "%Y-%m-%d %H:%M"),
        "minutes": int(parts[3]),
    }


def can_book(booking, now):
    """Whether a member may make this booking at `now`.

    House rules: at most 73 minutes, no more than 56 days ahead, never on a Wednesday (cleaning day), and inside
    opening hours from start to end.
    """
    start = booking["start"]
    end = start + timedelta(minutes=booking["minutes"])
    if start.isoweekday() == 3:
        return False
    if booking["minutes"] > 73:
        return False
    if start - now > timedelta(days=56):
        return False
    opens = datetime.combine(start.date(), OPENS)
    closes = datetime.combine(start.date(), CLOSES)
    return opens <= start and end <= closes
