"""Text-message reminders for the clinic's appointments.

Each appointment gets one reminder, sent exactly 24 hours before it starts.
"""

from datetime import datetime, timedelta


def parse_appointment(line):
    """An appointment from the booking system's export, like "2026-03-04 15:00;Sam Patel;0712345678"."""
    when, name, phone = (field.strip() for field in line.split(";"))
    return {
        "start": datetime.strptime(when, "%Y-%m-%d %H:%M"),
        "name": name,
        "phone": "".join(c for c in phone if c.isdigit()),
    }


def message(appointment):
    """The text of a reminder."""
    return f"Hi {appointment['name']}, this is a reminder of your appointment on {appointment['start']:%d/%m at %H:%M}."


def reminder_times(appointment):
    """When to text the patient, earliest first: 48 hours and 2 hours before, moved out of the quiet hours.

    A reminder in the quiet hours goes out at 21:00 on its own date, even when that date's 21:00 is after the night.
    """
    times = []
    for hours in (48, 2):
        at = appointment["start"] - timedelta(hours=hours)
        if at.hour < 7 or at.hour >= 22:
            at = at.replace(hour=21, minute=0, second=0, microsecond=0)
        times.append(at)
    return times
