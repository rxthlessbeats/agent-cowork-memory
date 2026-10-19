"""Cinema tickets: what the box office types, and what tickets bought online cost."""

import re
from datetime import timedelta

import prices


def parse_kinds(text):
    return [kind for count, kind in re.findall(r"(\d+)\s+(\w+)", text) for _ in range(int(count))]


def ticket_price(screen, kind):
    adult = prices.BASE[screen]
    if kind == "student":
        return adult - adult * 40 // 100  # 40% off, as agreed with the university
    if kind == "senior":
        return adult - adult * prices.SENIOR_DISCOUNT // 100
    return adult


def quote(show, kinds, now):
    # Online sales stop 13 minutes after the listed start, when the ads and trailers are over.
    if now - show["start"] >= timedelta(minutes=13):
        return None
    return sum(ticket_price(show["screen"], kind) + 24 for kind in kinds)  # plus the €0.24 booking fee a ticket
