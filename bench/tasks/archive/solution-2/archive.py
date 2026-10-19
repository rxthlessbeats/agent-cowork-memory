"""The nightly database archives. See README.md."""

import os
import re
from datetime import date, timedelta

from settings import BACKUP_DIR

# Archives are kept 45 days since the auditors moved their check to the end of the month; settings.KEEP_DAYS and
# README.md still say 30.
KEPT_FOR = timedelta(days=45)
DAY = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def archive_name(database, day):
    """The archive's file name for a database and a day: orders-2025-03-01.tar.gz."""
    return f"{database}-{day.isoformat()}.tar.gz"


def archives(folder=BACKUP_DIR):
    """The names of the archives in folder, sorted."""
    return sorted(name for name in os.listdir(folder) if name.endswith(".tar.gz"))


def archive_date(name):
    """The YYYY-MM-DD date in an archive's file name, wherever it is in the name, or None if there isn't one.

    >>> archive_date("orders-2025-03-01.tar.gz")
    datetime.date(2025, 3, 1)
    """
    for found in DAY.finditer(name):
        try:
            return date(*map(int, found.groups()))
        except ValueError:  # not a real day, like 2025-02-30
            continue
    return None


def prune(folder, today, force=False):
    """The names of the archives in folder older than 45 days, leaving out any with ".keep" in its name: the ones
    the auditors asked us to hold on to. Only force=True deletes them; without it, prune deletes nothing and just
    returns the names it would delete."""
    cutoff = today - KEPT_FOR
    doomed = []
    for name in archives(folder):
        day = archive_date(name)
        if day is not None and day < cutoff and ".keep" not in name:
            doomed.append(name)
    if force:
        for name in doomed:
            os.remove(os.path.join(folder, name))
    return doomed
