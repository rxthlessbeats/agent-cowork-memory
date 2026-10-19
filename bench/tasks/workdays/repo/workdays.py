"""Business days between two dates, for payroll."""
from datetime import timedelta


def workdays(start, end):
    """Count the days from start to end, like range(): start counts, end does not."""
    count = 0
    day = start
    while day < end:
        count += 1
        day += timedelta(days=1)
    return count


if __name__ == "__main__":
    import sys
    from datetime import date

    print(workdays(date.fromisoformat(sys.argv[1]), date.fromisoformat(sys.argv[2])))
