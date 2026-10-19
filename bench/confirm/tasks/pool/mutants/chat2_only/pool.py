"""Bookings for the pool's swim sessions."""

from datetime import datetime

from prices import ADULT, CHILD, CHILD_UNDER

CAPACITY = 66  # swimmers a session takes: what the lifeguard rota covers
MEMBER_DISCOUNT = 10  # percent off a member's ticket, child or adult


def parse_start(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M")


def book(session, people):
    if session["booked"] + len(people) > CAPACITY:
        return None
    total = 0
    for p in people:
        price = CHILD if p["age"] < CHILD_UNDER else ADULT
        if p["member"]:
            price = price * (100 - MEMBER_DISCOUNT) // 100
        total += price
    return total
