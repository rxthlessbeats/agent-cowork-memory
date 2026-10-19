"""Weekly pay from a timesheet."""
from collections import defaultdict

REGULAR_HOURS = 7.5  # a day's hours past this are overtime
OVERTIME_RATE = 1.4
DOUBLE_PAY_ISOWEEKDAY = 6  # Saturday (moved from Sunday): every hour pays double, overtime or not


def clock_minutes(clock):
    hours, minutes = clock.split(":")
    return int(hours) * 60 + int(minutes)


def shift_hours(start, end):
    """Hours worked between two "HH:MM" times; a shift that ends before it starts runs past midnight."""
    return (clock_minutes(end) - clock_minutes(start)) % (24 * 60) / 60


def day_pay(day, hours, rate):
    if day.isoweekday() == DOUBLE_PAY_ISOWEEKDAY:
        return 2 * hours * rate
    overtime = max(hours - REGULAR_HOURS, 0)
    return (hours - overtime + overtime * OVERTIME_RATE) * rate


def pay(timesheet, rate):
    """Gross pay for a week's timesheet: a list of (day, start, end) shifts, day being a date."""
    hours = defaultdict(float)
    for day, start, end in timesheet:
        hours[day] += shift_hours(start, end)
    return sum(day_pay(day, worked, rate) for day, worked in hours.items())


if __name__ == "__main__":
    from datetime import date

    week = [(date(2026, 3, 2), "09:00", "17:30"), (date(2026, 3, 3), "22:00", "06:00")]
    print(pay(week, 20.0))
