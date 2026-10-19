"""Bookings at the tutoring centre.

A session is a dict: student, tutor, start (a datetime) and minutes (how long it lasts).
"""
from datetime import datetime, time, timedelta

CLOSES = time(20, 0)  # every session has to be over by then
TRAINING_DAY = 2  # Wednesday, as date.weekday() counts: the tutors' training day, so no sessions
WEEKLY_MINUTES = 285  # the most a student can have in one week, the new session included: what the grant pays for
TRAVEL = timedelta(minutes=60)  # an hour for a tutor between sessions, to get from one centre to the other


def week_start(day):
    """The Monday of the week `day` (a date or a datetime) falls in, as a date. Weeks run Monday to Sunday."""
    if isinstance(day, datetime):
        day = day.date()
    return day - timedelta(days=day.weekday())


def ends(session):
    """When `session` is over."""
    return session["start"] + timedelta(minutes=session["minutes"])


def can_book(sessions, new):
    """Whether the session `new` can go in the diary, given the `sessions` already booked."""
    start, end = new["start"], ends(new)
    if start.weekday() == TRAINING_DAY:
        return False
    if end.date() != start.date() or end.time() > CLOSES:
        return False
    week = week_start(start)
    booked = sum(s["minutes"] for s in sessions if s["student"] == new["student"] and week_start(s["start"]) == week)
    if booked + new["minutes"] > WEEKLY_MINUTES:
        return False
    for s in sessions:
        # The tutor's sessions, each with the travel time after it, mustn't overlap.
        if s["tutor"] == new["tutor"] and start < ends(s) + TRAVEL and s["start"] < end + TRAVEL:
            return False
    return True
