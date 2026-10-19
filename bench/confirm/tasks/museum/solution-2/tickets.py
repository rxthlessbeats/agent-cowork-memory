"""Ticket sales at the museum desk and on the website. Amounts are in cents.

A booking is the day of the visit and the ages of the people coming, written like "2026-10-17: 34, 36, 8".

Children under 16 go free (the city's education grant), a booking for 40 or more people gets 4% off (promised to
the schools), and on Saturdays every ticket that isn't free costs 5.51 more (the late opening's guards).
"""

import re
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from prices import ADULT, CONCESSION, SENIOR_AGE


def parse_booking(line):
    """A booking written like "2026-10-17: 34, 36, 8", as (date, ages)."""
    match = re.fullmatch(r"\s*(\d{4}-\d{2}-\d{2})\s*:\s*(\d+(?:\s*,\s*\d+)*)\s*", line)
    if not match:
        raise ValueError(f"not a booking: {line!r}")
    return datetime.strptime(match[1], "%Y-%m-%d").date(), [int(n) for n in re.findall(r"\d+", match[2])]


def quote(ages, day):
    """What a booking costs, in cents: ages is everyone coming, day the day of the visit (a datetime.date)."""
    saturday = day.strftime("%w") == "6"
    total = Decimal(0)
    for age in ages:
        if age >= 16:
            total += (CONCESSION if age >= SENIOR_AGE else ADULT) + (551 if saturday else 0)
    if len(ages) >= 40:
        total *= Decimal("0.96")
    return int(total.quantize(Decimal(1), rounding=ROUND_HALF_UP))
