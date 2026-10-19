"""The sauna's house rules: the heater, sessions, and when the door opens. See README.md."""

from settings import CLOSES, OPENS


def setpoint(requested):
    """The temperature to set the heater to, in °C, when someone asks for `requested`."""
    raise NotImplementedError


def session_end(start):
    """When a session that starts at `start` (a datetime) ends."""
    raise NotImplementedError


def is_open(when):
    """Whether the sauna is open at `when` (a datetime)."""
    raise NotImplementedError
