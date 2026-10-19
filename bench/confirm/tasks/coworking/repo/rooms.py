"""Meeting rooms at the coworking space.

A booking is a dict: "room" (one of ROOMS), "start" (a datetime) and "minutes" (how long it lasts).
"""

from datetime import time

ROOMS = ["Fjord", "Harbour", "Loft"]
OPENS = time(7, 0)
CLOSES = time(21, 0)


def can_book(booking, now):
    """Whether a member may make this booking at `now`."""
    raise NotImplementedError
