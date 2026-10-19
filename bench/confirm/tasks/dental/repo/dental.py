"""Appointments at the dental practice.

An appointment is a dict like {"patient": "P-1042", "age": 34, "start": datetime(2026, 10, 20, 9, 30)}.
"""

from datetime import datetime

APPOINTMENTS = [
    {"patient": "P-1042", "age": 34, "start": datetime(2026, 10, 20, 9, 30)},
    {"patient": "P-0877", "age": 9, "start": datetime(2026, 10, 20, 11, 0)},
    {"patient": "P-1310", "age": 61, "start": datetime(2026, 10, 22, 14, 15)},
]


def on_day(appointments, day):
    """The appointments on a given date, earliest first."""
    return sorted((a for a in appointments if a["start"].date() == day), key=lambda a: a["start"])
