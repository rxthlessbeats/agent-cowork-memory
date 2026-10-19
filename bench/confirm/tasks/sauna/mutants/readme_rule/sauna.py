"""The sauna's house rules, as README.md describes them: the heater, sessions, and when the door opens."""

from datetime import datetime, timedelta

from settings import CLOSES, OPENS

MAX_TEMP = 100  # °C
SESSION = timedelta(minutes=90)
CLEANING_DAY = 0  # date.weekday(): closed on Mondays for cleaning


def parse_slot(text):
    """A booking slot like "2026-10-21 18:45" (or "2026-10-22 9:05") as a datetime."""
    return datetime.strptime(text.strip(), "%Y-%m-%d %H:%M")


def setpoint(requested):
    """The temperature to set the heater to, in °C, when someone asks for `requested`."""
    return min(requested, MAX_TEMP)


def session_end(start):
    """When a session that starts at `start` (a datetime) ends."""
    return start + SESSION


def is_open(when):
    """Whether the sauna is open at `when` (a datetime)."""
    return when.weekday() != CLEANING_DAY and OPENS <= when.time() < CLOSES
