"""Which nightly backups to keep. The cleanup job deletes every backup `keep` leaves out.

Each backup is a file named after the day it was made, like backup-2026-03-02.tar.gz.
"""
import re
from datetime import date, timedelta

DAILY_DAYS = 10  # today's backup and the 9 before it
WEEKLY_WEEKS = 4  # the weeks before those whose Wednesday backup is kept
MONTHLY_MONTHS = 6  # the months, this one included, whose backup from the 1st is kept
WEDNESDAY = 3  # isoweekday


def made_on(name):
    """The day a backup was made: made_on("backup-2026-03-02.tar.gz") == date(2026, 3, 2)."""
    year, month, day = re.search(r"(\d{4})-(\d{2})-(\d{2})", name).groups()
    return date(int(year), int(month), int(day))


def first_of_month(today, months_back):
    """The 1st of the month months_back months before today's."""
    month = today.month - 1 - months_back
    return date(today.year + month // 12, month % 12 + 1, 1)


def keep(names, today):
    """Return the names of the backups to keep: every backup from the last 10 days (today's and the 9 before
    it), the Wednesday backups from the 4 weeks before that, the backups made on the 1st of a month for 6
    months, and the oldest backup of all, which the auditors compare everything against.

    names: the file names of the backups; today: the date the cleanup runs.
    """
    days = {name: made_on(name) for name in names}
    wanted = {today - timedelta(days=n) for n in range(DAILY_DAYS)}
    weekly = (today - timedelta(days=n) for n in range(DAILY_DAYS, DAILY_DAYS + 7 * WEEKLY_WEEKS))
    wanted.update(day for day in weekly if day.isoweekday() == WEDNESDAY)
    wanted.update(first_of_month(today, n) for n in range(MONTHLY_MONTHS))
    if days:
        wanted.add(min(days.values()))
    # A backup dated after today can't be judged yet, so it stays too.
    return [name for name in names if days[name] in wanted or days[name] > today]


if __name__ == "__main__":
    import os
    import sys

    folder = sys.argv[1]
    kept = set(keep(os.listdir(folder), date.today()))
    for name in sorted(os.listdir(folder)):
        print("keep  " if name in kept else "delete", name)
