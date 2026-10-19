"""Which nightly backups to keep. The cleanup job deletes every backup `keep` leaves out.

Each backup is a file named after the day it was made, like backup-2026-03-02.tar.gz.
"""
import re
from datetime import date

DAILY = 10  # days during which every backup is kept
WEEKLY = 28  # days after those during which the Wednesday backups are kept
MONTHLY = 12  # months during which the backups from the 1st of a month are kept
WEDNESDAY = 2


def made_on(name):
    """The day a backup was made: made_on("backup-2026-03-02.tar.gz") == date(2026, 3, 2)."""
    return date.fromisoformat(re.search(r"\d{4}-\d{2}-\d{2}", name).group())


def keep(names, today):
    """Return the names of the backups to keep: every backup from the last 10 days, the Wednesday
    backups from the 4 weeks before that, the backups from the 1st of a month for a year, and the
    oldest backup of all, which the auditors compare against.

    names: the file names of the backups; today: the date the cleanup runs.
    """
    oldest = min(names, key=made_on, default=None)
    kept = []
    for name in names:
        day = made_on(name)
        age = (today - day).days
        months = (today.year - day.year) * 12 + today.month - day.month
        if (
            age < DAILY
            or (age < DAILY + WEEKLY and day.weekday() == WEDNESDAY)
            or (day.day == 1 and months < MONTHLY)
            or name == oldest
        ):
            kept.append(name)
    return kept


if __name__ == "__main__":
    import os
    import sys

    folder = sys.argv[1]
    kept = set(keep(os.listdir(folder), date.today()))
    for name in sorted(os.listdir(folder)):
        print("keep  " if name in kept else "delete", name)
