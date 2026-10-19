"""Weekly pay from a timesheet."""
from datetime import datetime


def shift_hours(start, end):
    """Hours worked between two "HH:MM" times."""
    worked = datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")
    return worked.total_seconds() / 3600


def pay(timesheet, rate):
    """Gross pay for a week's timesheet: a list of (day, start, end) shifts, day being a date."""
    return sum(shift_hours(start, end) for _, start, end in timesheet) * rate


if __name__ == "__main__":
    from datetime import date

    week = [(date(2026, 3, 2), "09:00", "17:30"), (date(2026, 3, 3), "22:00", "06:00")]
    print(pay(week, 20.0))
