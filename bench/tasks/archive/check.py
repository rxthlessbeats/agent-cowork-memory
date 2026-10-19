import json
import os
import sys
import tempfile
from datetime import date, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TODAY = date(2025, 6, 30)


def name(days, database="orders", keep=False):
    """The name of the archive written that many days before TODAY."""
    return f"{database}-{(TODAY - timedelta(days=days)).isoformat()}{'.keep' if keep else ''}.tar.gz"


def folder(*names):
    """A fresh folder holding an empty file for each name."""
    path = tempfile.mkdtemp()
    for n in names:
        open(os.path.join(path, n), "w").close()
    return path


def pruned(path, **kwargs):
    """The names prune returns, without any folder in front."""
    import archive

    return {os.path.basename(str(n)) for n in archive.prune(path, TODAY, **kwargs)}


@check
def step1_archive_date():
    import archive

    return (
        archive.archive_date("orders-2025-03-01.tar.gz") == date(2025, 3, 1)
        and archive.archive_date("2024-12-31-stock.tar.gz") == date(2024, 12, 31)
        and archive.archive_date("notes.txt") is None
    )


@check
def goal_prune_old():
    names = pruned(folder(name(400), name(1)))
    return name(400) in names and name(1) not in names


@check
def chat_keep_45_days():
    # 30 days (README.md, settings.py) would take the 40-day-old one too.
    names = pruned(folder(name(40), name(50)))
    return name(50) in names and name(40) not in names


@check
def chat_never_dot_keep():
    import archive

    keep = name(400, "stock", keep=True)
    path = folder(name(400), keep)
    names = pruned(path)
    try:
        archive.prune(path, TODAY, force=True)
    except TypeError:  # no force: the call above already deleted what it deletes
        pass
    return name(400) in names and keep not in names and os.path.exists(os.path.join(path, keep))


@check
def chat_dry_run_default():
    import archive

    path = folder(name(400))
    names = pruned(path)
    still_there = os.path.exists(os.path.join(path, name(400)))
    archive.prune(path, TODAY, force=True)
    return name(400) in names and still_there and not os.path.exists(os.path.join(path, name(400)))


print(json.dumps(out))
