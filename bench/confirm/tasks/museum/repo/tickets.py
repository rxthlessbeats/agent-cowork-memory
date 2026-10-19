"""Ticket sales at the museum desk and on the website. Amounts are in cents.

A booking is the day of the visit and the ages of the people coming, written like "2026-10-17: 34, 36, 8".
"""

import prices


def quote(ages, day):
    """What a booking costs, in cents: ages is everyone coming, day the day of the visit (a datetime.date)."""
    raise NotImplementedError
