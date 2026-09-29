import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def backup(home, dest=None):
    home = Path(home)
    source_path = home / "state.sqlite3"
    if dest is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dest = home / "backups" / f"{stamp}.sqlite3"
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(source_path)
    target = sqlite3.connect(dest)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    return {"session": None, "backup": str(dest)}
