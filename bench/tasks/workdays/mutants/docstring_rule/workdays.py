"""Business days between two dates, for payroll."""
from datetime import timedelta


def closed(day):
    """The office is shut from 24 December to 1 January."""
    return (day.month, day.day) >= (12, 24) or (day.month, day.day) == (1, 1)


def workdays(start, end):
    """Count business days from start to end, like range(): start counts, end does not. Negative when end is before start."""
    if end < start:
        return -workdays(end, start)
    count = 0
    day = start
    while day < end:
        count += day.weekday() < 5 and not closed(day)
        day += timedelta(days=1)
    return count


if __name__ == "__main__":
    import sys
    from datetime import date

    print(workdays(date.fromisoformat(sys.argv[1]), date.fromisoformat(sys.argv[2])))
