"""Bookings for the freight elevator, which residents reserve when they move in or out.

A booking is a dict like {"flat": "4B", "start": datetime(2026, 10, 20, 9, 30), "minutes": 90}.
"""

from datetime import datetime, timedelta

from rules import MAX_BOOKING_MINUTES

BOOKINGS = [
    {"flat": "4B", "start": datetime(2026, 10, 20, 9, 30), "minutes": 90},
    {"flat": "12A", "start": datetime(2026, 10, 21, 13, 0), "minutes": 120},
    {"flat": "7C", "start": datetime(2026, 10, 23, 15, 15), "minutes": 45},
]

SERVICE_DAY = 0  # Monday, as date.weekday() counts: the elevator's weekly service
DAYS_AHEAD = 10  # on the 1st you can book up to the 11th


def flats(bookings):
    """The flats with a booking, each once, sorted."""
    return sorted({b["flat"] for b in bookings})


def parse_request(text):
    """A request the way residents type it: flat, date, start time and minutes.

    >>> parse_request("4B 2026-10-20 09:30 90")
    {'flat': '4B', 'start': datetime.datetime(2026, 10, 20, 9, 30), 'minutes': 90}
    """
    fields = text.split()
    if len(fields) != 4:
        raise ValueError(f"expected flat, date, start time and minutes: {text!r}")
    flat, day, start, minutes = fields
    return {
        "flat": flat.upper(),
        "start": datetime.strptime(f"{day} {start}", "%Y-%m-%d %H:%M"),
        "minutes": int(minutes),
    }


def end(booking):
    return booking["start"] + timedelta(minutes=booking["minutes"])


def can_book(bookings, request, today):
    """Whether request can be booked on today, given the bookings already made."""
    start = request["start"]
    if start.weekday() == SERVICE_DAY:
        return False
    if not 0 <= (start.date() - today).days <= DAYS_AHEAD:
        return False
    if request["minutes"] > MAX_BOOKING_MINUTES:
        return False
    return all(end(request) <= b["start"] or end(b) <= start for b in bookings)
