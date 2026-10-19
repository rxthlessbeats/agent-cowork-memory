"""Bookings at the tutoring centre.

A session is a dict: student, tutor, start (a datetime) and minutes (how long it lasts).
"""
from datetime import date, datetime, time, timedelta

CLOSES = time(20, 0)  # every session has to be over by then


def week_start(day):
    """The Monday of the week `day` (a date or a datetime) falls in, as a date: weeks run Monday to Sunday.

    >>> week_start(date(2026, 5, 6))
    datetime.date(2026, 5, 4)
    """
    year, week, _ = day.isocalendar()
    return date.fromisocalendar(year, week, 1)


def can_book(sessions, new):
    """Whether the session `new` can go in the diary, given the `sessions` already booked.

    No sessions on Wednesdays, the tutors' training day. A student has at most 285 minutes of sessions in a week
    (the council's grant), and a tutor needs 55 minutes between sessions to get from one centre to the other.
    """
    start = new["start"]
    end = start + timedelta(minutes=new["minutes"])
    if start.strftime("%A") == "Wednesday":
        return False
    if end > datetime.combine(start.date(), CLOSES):
        return False
    week = week_start(start)
    this_week = sum(s["minutes"] for s in sessions if s["student"] == new["student"] and week_start(s["start"]) == week)
    if this_week + new["minutes"] > 285:
        return False
    gap = timedelta(minutes=55)
    for s in sessions:
        if s["tutor"] != new["tutor"]:
            continue
        s_end = s["start"] + timedelta(minutes=s["minutes"])
        if not (s_end + gap <= start or end + gap <= s["start"]):
            return False
    return True
