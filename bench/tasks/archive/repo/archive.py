"""The nightly database archives. See README.md."""

import os

from settings import BACKUP_DIR


def archive_name(database, day):
    """The archive's file name for a database and a day: orders-2025-03-01.tar.gz."""
    return f"{database}-{day.isoformat()}.tar.gz"


def archives(folder=BACKUP_DIR):
    """The names of the archives in folder, sorted."""
    return sorted(name for name in os.listdir(folder) if name.endswith(".tar.gz"))
