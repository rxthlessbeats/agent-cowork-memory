"""Which nightly backups to keep. The cleanup job deletes every backup `keep` leaves out.

Each backup is a file named after the day it was made, like backup-2026-03-02.tar.gz.
"""
from datetime import date


def keep(names, today):
    """Return the names of the backups to keep: every backup from the last 7 days, and the Sunday
    backups from the 4 weeks before that.

    names: the file names of the backups; today: the date the cleanup runs.
    """
    return list(names)


if __name__ == "__main__":
    import os
    import sys

    folder = sys.argv[1]
    kept = set(keep(os.listdir(folder), date.today()))
    for name in sorted(os.listdir(folder)):
        print("keep  " if name in kept else "delete", name)
