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
    """When to text the patient, as the module docstring says: once, exactly 24 hours before, at any hour."""
    return [appointment["start"] - timedelta(hours=24)]
