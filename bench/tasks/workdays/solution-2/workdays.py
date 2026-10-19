"""Business days between two dates, for payroll."""
from datetime import date


def weekdays_through(day):
    """Monday-to-Friday days from 1 January of year 1 (a Monday) up to and including day."""
    weeks, rest = divmod(day.toordinal(), 7)
    return weeks * 5 + min(rest, 5)


def closed_weekdays(after, upto):
    """Weekdays of the 24 December to 1 January closure that fall after `after`, up to and including `upto`."""
    count = 0
    for year in range(after.year, upto.year + 1):
        for day in [date(year, 1, 1)] + [date(year, 12, d) for d in range(24, 32)]:
            count += after < day <= upto and day.weekday() < 5
    return count


def workdays(start, end):
    """Business days after start, up to and including end, as payroll counts them. Negative when end is before start."""
    if end < start:
        return -workdays(end, start)
    return weekdays_through(end) - weekdays_through(start) - closed_weekdays(start, end)


if __name__ == "__main__":
    import sys

    print(workdays(date.fromisoformat(sys.argv[1]), date.fromisoformat(sys.argv[2])))
