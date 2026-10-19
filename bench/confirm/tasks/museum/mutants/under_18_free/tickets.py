"""Ticket sales at the museum desk and on the website. Amounts are in cents.

A booking is the day of the visit and the ages of the people coming, written like "2026-10-17: 34, 36, 8".
"""

from datetime import date

import prices

FREE_UNDER = 18  # the city's education grant pays for children under 18
GROUP_SIZE = 40  # a booking this big gets the schools' discount
GROUP_DISCOUNT = 4  # percent off the whole booking
SATURDAY = 5  # date.weekday(): the late opening
SATURDAY_EXTRA = 551  # on every ticket that isn't free, for the late opening's guards


def parse_booking(line):
    """A booking like "2026-10-17: 34, 36, 8" as (date(2026, 10, 17), [34, 36, 8])."""
    day, ages = line.split(":", 1)
    return date.fromisoformat(day.strip()), [int(age) for age in ages.split(",")]


def ticket(age):
    """One person's ticket, before any Saturday extra or group discount."""
    if age < FREE_UNDER:
        return 0
    return prices.CONCESSION if age >= prices.SENIOR_AGE else prices.ADULT


def quote(ages, day):
    """What a booking costs, in cents: ages is everyone coming, day the day of the visit (a datetime.date)."""
    tickets = [ticket(age) for age in ages]
    if day.weekday() == SATURDAY:
        tickets = [t + SATURDAY_EXTRA if t else 0 for t in tickets]
    total = sum(tickets)
    if len(ages) >= GROUP_SIZE:
        total = round(total * (100 - GROUP_DISCOUNT) / 100)
    return total
