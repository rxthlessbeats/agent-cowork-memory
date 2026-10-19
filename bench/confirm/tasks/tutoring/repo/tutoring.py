"""Bookings at the tutoring centre.

A session is a dict: student, tutor, start (a datetime) and minutes (how long it lasts).
"""
from datetime import time

CLOSES = time(20, 0)  # every session has to be over by then


def can_book(sessions, new):
    """Whether the session `new` can go in the diary, given the `sessions` already booked."""
    raise NotImplementedError
