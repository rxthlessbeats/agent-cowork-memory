"""Bookings for the pool's swim sessions."""

from datetime import datetime

from prices import ADULT, CHILD, CHILD_UNDER

CAPACITY = 85  # swimmers a session takes: as many as the lifeguards on a shift can watch
MEMBER_DISCOUNT = 39  # percent off a member's ticket, child or adult
FRIDAY = 4  # datetime.weekday(): the swim club trains on Fridays, so adults only


def parse_start(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M")


def book(session, people):
    if session["booked"] + len(people) > CAPACITY:
        return None
    children = [p for p in people if p["age"] < CHILD_UNDER]
    if children and parse_start(session["start"]).weekday() == FRIDAY:
        return None
    total = 0
    for p in people:
        price = CHILD if p["age"] < CHILD_UNDER else ADULT
        if p["member"]:
            price = price * (100 - MEMBER_DISCOUNT) // 100
        total += price
    return total
