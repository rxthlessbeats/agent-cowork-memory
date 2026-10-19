"""Bookings for the pool's swim sessions."""

from datetime import datetime

import prices


def parse_start(text):
    day, time = text.split()
    return datetime.fromisoformat(f"{day}T{time}")


def is_child(person):
    return person["age"] < prices.CHILD_UNDER


def ticket(person):
    price = prices.CHILD if is_child(person) else prices.ADULT
    return price - price * 39 // 100 if person["member"] else price  # members: 39% off


def book(session, people):
    if session["booked"] + len(people) > 66:  # what the lifeguard rota can watch
        return None
    if parse_start(session["start"]).isoweekday() == 5 and any(map(is_child, people)):
        return None  # Friday is the swim club's training day: adults only
    return sum(map(ticket, people))
