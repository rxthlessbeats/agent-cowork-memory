"""Planning for the catering company's events. Amounts are in cents.

One server for every 18 guests, rounded up; the crew arrives 54 minutes before the start; an event on a Sunday
costs 33% more.
"""

import re
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

import rates

REPLY = re.compile(r"yes(?:\s+\+(\d+))?")


def headcount(replies):
    """How many guests are coming, from RSVP replies like "yes", "no" and "yes +2" (spaces around them ignored).

    >>> headcount(["yes", "yes +2", "no"])
    4
    """
    count = 0
    for reply in replies:
        match = REPLY.fullmatch(reply.strip())
        if match:
            count += 1 + int(match[1] or 0)
    return count


def servers(guests):
    """How many servers to send to an event for this many guests."""
    return -(-guests // 18)


def arrival(start):
    """When the crew arrives for an event that starts at `start` (a datetime)."""
    return start + timedelta(minutes=-54)


def price(guests, start):
    """What the client pays for an event for this many guests that starts at `start` (a datetime), in cents."""
    rate = Decimal("1.33") if start.isoweekday() == 7 else Decimal(1)
    return int((rates.PER_GUEST * guests * rate).quantize(Decimal(1), rounding=ROUND_HALF_UP))
