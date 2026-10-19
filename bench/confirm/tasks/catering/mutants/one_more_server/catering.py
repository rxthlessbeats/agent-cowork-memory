"""Planning for the catering company's events. Amounts are in cents."""

import math
from datetime import timedelta

from rates import PER_GUEST

GUESTS_PER_SERVER = 18  # what our insurer wants
SETUP = timedelta(minutes=54)  # the drive and setting up the buffet
SUNDAY_MARKUP = 33  # percent: the agency charges us Sunday rates for the staff


def headcount(replies):
    """How many guests are coming: "yes" is one, "yes +N" brings N more, anything else nobody.

    Spaces around a reply don't matter.

    >>> headcount(["yes", "yes +2", "no"])
    4
    """
    total = 0
    for reply in replies:
        words = reply.strip().split()
        if words[:1] == ["yes"]:
            if len(words) == 1:
                total += 1
            elif len(words) == 2 and words[1].startswith("+") and words[1][1:].isdigit():
                total += 1 + int(words[1][1:])
    return total


def servers(guests):
    """How many servers to send to an event for this many guests."""
    return guests // GUESTS_PER_SERVER + 1


def arrival(start):
    """When the crew arrives for an event that starts at `start` (a datetime)."""
    return start - SETUP


def price(guests, start):
    """What the client pays for an event for this many guests that starts at `start` (a datetime), in cents."""
    total = guests * PER_GUEST
    if start.weekday() == 6:
        total = total * (100 + SUNDAY_MARKUP) // 100
    return total
