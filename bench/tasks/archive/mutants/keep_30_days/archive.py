"""The nightly database archives. See README.md."""

import os
import re
from datetime import date, timedelta

from settings import BACKUP_DIR, KEEP_DAYS

KEEP = timedelta(days=KEEP_DAYS)


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


def prune(folder, today, force=False):
    """The archives older than KEEP_DAYS days, never one with .keep in its name. Only force=True deletes them."""
    old = [n for n in archives(folder) if ".keep" not in n and (d := archive_date(n)) and today - d > KEEP]
    if force:
        for name in old:
            os.remove(os.path.join(folder, name))
    return old
