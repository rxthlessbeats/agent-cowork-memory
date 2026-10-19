"""Text-message reminders for the clinic's appointments.

Each appointment gets one reminder, sent exactly 24 hours before it starts.
"""

import re
from datetime import datetime, time, timedelta

QUIET_FROM = time(22)
QUIET_UNTIL = time(7)
EVENING = time(21)


def parse_appointment(line):
    """An appointment from the booking system's export, like "2026-03-04 15:00;Sam Patel;0712345678"."""
    when, name, phone = map(str.strip, line.split(";"))
    return {"start": datetime.strptime(when, "%Y-%m-%d %H:%M"), "name": name, "phone": re.sub(r"\D", "", phone)}


def message(appointment):
    """The text of a reminder."""
    return f"Hi {appointment['name']}, this is a reminder of your appointment on {appointment['start']:%d/%m at %H:%M}."


def reminder_times(appointment):
    """When to text the patient: 48 hours and 2 hours before the start, earliest first.

    None goes out in the quiet hours, 22:00 to 07:00: one that would goes out at 21:00 the evening before instead.
    """
    times = []
    for hours in (48, 2):
        at = appointment["start"] - timedelta(hours=hours)
        if at.time() >= QUIET_FROM:
            at = datetime.combine(at.date(), EVENING)
        elif at.time() < QUIET_UNTIL:
            # After midnight: the evening before is the previous day's.
            at = datetime.combine(at.date() - timedelta(days=1), EVENING)
        times.append(at)
    return sorted(times)
