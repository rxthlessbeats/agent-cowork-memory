"""Business days between two dates, for payroll."""
from datetime import timedelta


def closed(day):
    """The office is shut from 24 December to 1 January."""
    return (day.month, day.day) >= (12, 24) or (day.month, day.day) == (1, 1)


def workdays(start, end):
    """Count business days after start, up to and including end. Negative when end is before start."""
    if end < start:
        return -workdays(end, start)
    count = 0
    day = start
    while day < end:
        day += timedelta(days=1)
        count += day.weekday() < 5 and not closed(day)
    return count


if __name__ == "__main__":
    import sys
    from datetime import date

    print(workdays(date.fromisoformat(sys.argv[1]), date.fromisoformat(sys.argv[2])))
