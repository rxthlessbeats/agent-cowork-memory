"""Timesheet entries: the hours worked, written in hours and minutes, like "7:45"."""


def parse_hours(text):
    """"7:45" -> 7.75: the entry's hours and minutes, as decimal hours."""
    hours, minutes = text.strip().split(":")
    return (int(hours) * 60 + int(minutes)) / 60


def format_hours(hours):
    minutes = round(hours * 60)
    return f"{minutes // 60}:{minutes % 60:02d}"
