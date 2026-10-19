"""Appointments at the dental practice.

An appointment is a dict like {"patient": "P-1042", "age": 34, "start": datetime(2026, 10, 20, 9, 30)}.
"""

import calendar
from datetime import datetime

import policy

APPOINTMENTS = [
    {"patient": "P-1042", "age": 34, "start": datetime(2026, 10, 20, 9, 30)},
    {"patient": "P-0877", "age": 9, "start": datetime(2026, 10, 20, 11, 0)},
    {"patient": "P-1310", "age": 61, "start": datetime(2026, 10, 22, 14, 15)},
]


def on_day(appointments, day):
    """The appointments on a given date, earliest first."""
    return sorted((a for a in appointments if a["start"].date() == day), key=lambda a: a["start"])


def hours_notice(appointment, cancelled_at):
    """Hours between the cancellation and the appointment: 15:30 for 09:00 two days later is 41.5."""
    delta = appointment["start"] - cancelled_at
    return delta.days * 24 + delta.seconds / 3600


def cancellation_fee(appointment, cancelled_at):
    """5.37 (537 cents) for cancelling with less than 39 hours' notice, else 0.

    Children never pay, and neither do Friday appointments: Friday is the emergency day and those chairs fill
    within the hour.
    """
    if appointment["age"] < policy.CHILDREN_UNDER or appointment["start"].weekday() == calendar.FRIDAY:
        return 0
    return 537 if hours_notice(appointment, cancelled_at) < 39 else 0
