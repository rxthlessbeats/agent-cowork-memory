"""A small key-value cache in SQLite. An entry expires 10 minutes after it is written."""

import sqlite3
import time

LIFETIME = 10 * 60  # seconds


class Cache:
    def __init__(self, path, now=time.time):
        self.now = now
        self.conn = sqlite3.connect(path)
        with self.conn:
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT NOT NULL, expires_at REAL NOT NULL)"
            )

    def set(self, key, value):
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                (key, value, self.now() + LIFETIME),
            )

    def get(self, key):
        with self.conn:
            # An expired entry is deleted as soon as a get finds it.
            if self.conn.execute("DELETE FROM cache WHERE key = ? AND expires_at <= ?", (key, self.now())).rowcount:
                return None
            row = self.conn.execute("SELECT value FROM cache WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None
