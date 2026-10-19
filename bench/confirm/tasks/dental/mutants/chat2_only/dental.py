"""Appointments at the dental practice.

An appointment is a dict like {"patient": "P-1042", "age": 34, "start": datetime(2026, 10, 20, 9, 30)}.
"""

from datetime import datetime, timedelta

from policy import CHILDREN_UNDER

APPOINTMENTS = [
    {"patient": "P-1042", "age": 34, "start": datetime(2026, 10, 20, 9, 30)},
    {"patient": "P-0877", "age": 9, "start": datetime(2026, 10, 20, 11, 0)},
    {"patient": "P-1310", "age": 61, "start": datetime(2026, 10, 22, 14, 15)},
]

NOTICE = timedelta(hours=39)  # cancelling with less notice than this is charged
FEE = 2500  # cents


def on_day(appointments, day):
    """The appointments on a given date, earliest first."""
    return sorted((a for a in appointments if a["start"].date() == day), key=lambda a: a["start"])


def hours_notice(appointment, cancelled_at):
    """How many hours before the appointment's start the cancellation came, as a float."""
    return (appointment["start"] - cancelled_at).total_seconds() / 3600


def cancellation_fee(appointment, cancelled_at):
    """What the patient is charged for cancelling at cancelled_at, in cents; 0 when it's free."""
    if appointment["age"] < CHILDREN_UNDER:
        return 0
    if appointment["start"] - cancelled_at >= NOTICE:
        return 0
    return FEE
