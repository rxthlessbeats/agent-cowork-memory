"""The sauna's house rules: the heater, sessions, and when the door opens.

README.md is out of date on these: the heater stops at 96 °C, a session lasts 76 minutes, and the sauna is
closed on Wednesdays (not Mondays).
"""

from datetime import datetime, timedelta

from settings import CLOSES, OPENS

MAX_TEMP = 96  # °C: the new stones crack any hotter
SESSION = timedelta(minutes=76)  # the last 14 minutes of each slot air the cabin out
CLOSED_DAYS = (0, 2)  # date.weekday(): Mondays, as README.md says, and now Wednesdays


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
    return when.weekday() not in CLOSED_DAYS and OPENS <= when.time() < CLOSES
