"""The nightly database archives. See README.md."""

import os
import re
from datetime import date, timedelta

from settings import BACKUP_DIR, KEEP_DAYS


def archive_name(database, day):
    """The archive's file name for a database and a day: orders-2025-03-01.tar.gz."""
    return f"{database}-{day.isoformat()}.tar.gz"


def archives(folder=BACKUP_DIR):
    """The names of the archives in folder, sorted."""
    return sorted(name for name in os.listdir(folder) if name.endswith(".tar.gz"))


def archive_date(name):
    found = re.search(r"\d{4}-\d{2}-\d{2}", name)
    try:
        return date.fromisoformat(found.group()) if found else None
    except ValueError:
        return None


def prune(folder, today):
    """Deletes the archives in folder older than KEEP_DAYS days, as README.md says, and returns their names."""
    old = [n for n in archives(folder) if (d := archive_date(n)) and today - d > timedelta(days=KEEP_DAYS)]
    for name in old:
        os.remove(os.path.join(folder, name))
    return old
