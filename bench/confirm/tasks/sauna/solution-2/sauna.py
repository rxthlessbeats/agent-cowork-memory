"""The sauna's house rules: the heater, sessions, and when the door opens. See README.md, but go by the rules here:
the README's 100 °C, 90 minutes and Monday closing are out of date.
"""

import re
from datetime import datetime, timedelta

import settings

HEATER_LIMIT = 96
SESSION_MINUTES = 76
CLOSED_ON = "Wednesday"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_slot(text):
    """A booking slot, "YYYY-MM-DD H:MM" or "YYYY-MM-DD HH:MM", as a datetime."""
    match = re.fullmatch(r"\s*(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{2})\s*", text)
    if not match:
        raise ValueError(f"not a slot: {text!r}")
    return datetime(*map(int, match.groups()))


def setpoint(requested):
    """The temperature to set the heater to, in °C, when someone asks for `requested`: never above 96."""
    return HEATER_LIMIT if requested > HEATER_LIMIT else requested


def session_end(start):
    """When a session that starts at `start` (a datetime) ends: 76 minutes later."""
    return start + timedelta(seconds=SESSION_MINUTES * 60)


def minute_of_day(t):
    return t.hour * 60 + t.minute


def is_open(when):
    """Whether the sauna is open at `when` (a datetime): within the opening hours, and never on a Wednesday."""
    if DAYS[when.weekday()] == CLOSED_ON:
        return False
    return minute_of_day(settings.OPENS) <= minute_of_day(when) < minute_of_day(settings.CLOSES)
