"""Weekly pay from a timesheet."""
from datetime import datetime

DAY_HOURS = 8  # overtime is every hour past this in one day
OVERTIME = 1.4
DOUBLE_PAY_DAY = 5  # Saturday: every hour pays double, overtime or not


def shift_hours(start, end):
    """Hours worked between two "HH:MM" times; a shift that ends before it starts runs past midnight."""
    worked = datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")
    return worked.total_seconds() / 3600 % 24


def pay(timesheet, rate):
    """Gross pay for a week's timesheet: a list of (day, start, end) shifts, day being a date."""
    hours = {}
    for day, start, end in timesheet:
        hours[day] = hours.get(day, 0) + shift_hours(start, end)
    total = 0
    for day, worked in hours.items():
        if day.weekday() == DOUBLE_PAY_DAY:
            total += 2 * worked * rate
        else:
            total += (min(worked, DAY_HOURS) + OVERTIME * max(worked - DAY_HOURS, 0)) * rate
    return total


if __name__ == "__main__":
    from datetime import date

    week = [(date(2026, 3, 2), "09:00", "17:30"), (date(2026, 3, 3), "22:00", "06:00")]
    print(pay(week, 20.0))
