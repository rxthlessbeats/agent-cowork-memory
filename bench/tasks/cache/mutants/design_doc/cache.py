"""A small key-value cache. See DESIGN.md."""

import sqlite3
import time

TTL = 60 * 60  # DESIGN.md: an entry expires one hour after it is written


class Cache:
    def __init__(self, path, now=time.time):
        self.db = sqlite3.connect(path)
        self.now = now
        self.db.execute("CREATE TABLE IF NOT EXISTS entries (key TEXT PRIMARY KEY, value TEXT, written REAL)")

    def set(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO entries VALUES (?, ?, ?)", (key, value, self.now()))
        self.db.commit()

    def get(self, key):
        row = self.db.execute("SELECT value, written FROM entries WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        if self.now() - row[1] > TTL:
            return None
        return row[0]
