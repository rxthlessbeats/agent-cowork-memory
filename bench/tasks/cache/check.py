import json
import os
import sqlite3
import sys
import tempfile

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def opened(clock, path=None):
    """A Cache on a fresh file (or path) whose time is clock[0]."""
    import cache

    return cache.Cache(path or os.path.join(tempfile.mkdtemp(), "cache.db"), now=lambda: clock[0])


@check
def step1_sqlite():
    path = os.path.join(tempfile.mkdtemp(), "cache.db")
    opened([0.0], path)
    return bool(sqlite3.connect(path).execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall())


@check
def goal_get_set():
    cache = opened([1000.0])
    cache.set("a", "1")
    return cache.get("a") == "1" and cache.get("missing") is None


@check
def chat_ten_minutes():
    clock = [1000.0]
    cache = opened(clock)
    cache.set("a", "1")
    clock[0] = 1000 + 9 * 60
    kept = cache.get("a") == "1"
    clock[0] = 1000 + 11 * 60
    return kept and cache.get("a") is None


@check
def chat_deletes_expired():
    path = os.path.join(tempfile.mkdtemp(), "cache.db")
    clock = [1000.0]
    cache = opened(clock, path)
    cache.set("a", "1")
    clock[0] = 1000 + 2 * 3600
    cache.get("a")
    # Back before it expired: only a deleted entry is gone now.
    return opened([1000.0], path).get("a") is None


print(json.dumps(out))
