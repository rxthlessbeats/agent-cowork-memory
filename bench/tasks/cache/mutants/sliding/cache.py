"""A small key-value cache. See DESIGN.md."""

import sqlite3
import time

TTL = 10 * 60


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
            self.db.execute("DELETE FROM entries WHERE key = ?", (key,))
            self.db.commit()
            return None
        self.db.execute("UPDATE entries SET written = ? WHERE key = ?", (self.now(), key))
        self.db.commit()
        return row[0]
