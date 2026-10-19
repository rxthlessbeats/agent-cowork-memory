"""Bookings for the freight elevator, which residents reserve when they move in or out.

A booking is a dict like {"flat": "4B", "start": datetime(2026, 10, 20, 9, 30), "minutes": 90}.
"""

from datetime import datetime, timedelta

import rules

BOOKINGS = [
    {"flat": "4B", "start": datetime(2026, 10, 20, 9, 30), "minutes": 90},
    {"flat": "12A", "start": datetime(2026, 10, 21, 13, 0), "minutes": 120},
    {"flat": "7C", "start": datetime(2026, 10, 23, 15, 15), "minutes": 45},
]


def flats(bookings):
    """The flats with a booking, each once, sorted."""
    return sorted({b["flat"] for b in bookings})


def parse_request(text):
    """parse_request("4B 2026-10-20 09:30 90") is {"flat": "4B", "start": datetime(2026, 10, 20, 9, 30), "minutes": 90}.

    Raises ValueError for a line without exactly those four fields.
    """
    flat, day, clock, minutes = text.split()  # ValueError when a field is missing or extra
    return {"flat": flat.upper(), "start": datetime.fromisoformat(f"{day}T{clock}"), "minutes": int(minutes)}


def can_book(bookings, request, today):
    """Whether request can be booked on today, given the bookings already made.

    Never on a Monday (the weekly service), never more than 10 days ahead, never longer than the house rules
    allow, and at least 26 minutes clear of every other booking for the caretaker to move the wall padding.
    """
    begin = request["start"]
    finish = begin + timedelta(minutes=request["minutes"])
    if begin.isoweekday() == 1:
        return False
    if begin.date() > today + timedelta(days=10):
        return False
    if request["minutes"] > rules.MAX_BOOKING_MINUTES:
        return False
    pad = timedelta(minutes=26)
    for other in bookings:
        other_begin = other["start"]
        other_finish = other_begin + timedelta(minutes=other["minutes"])
        if begin < other_finish + pad and other_begin < finish + pad:
            return False
    return True
