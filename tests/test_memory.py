import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

from agent_cowork_memory.data import backup
from agent_cowork_memory.db import SCHEMA, connect
from agent_cowork_memory.ledger import attach, context
from agent_cowork_memory.memory import note_add, note_forget, note_promote, note_search


def git_repo(path):
    path.mkdir()
    subprocess.run(["git", "-C", path, "init", "-q"], check=True)
    subprocess.run(["git", "-C", path, "config", "user.email", "acm@localhost"], check=True)
    subprocess.run(["git", "-C", path, "config", "user.name", "acm"], check=True)
    (path / "README.md").write_text("x\n")
    subprocess.run(["git", "-C", path, "add", "README.md"], check=True)
    subprocess.run(["git", "-C", path, "commit", "-qm", "init"], check=True)


class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.repo = Path(self.tmp.name) / "repo"
        git_repo(self.repo)
        self.conn = connect(self.home)
        self.owner = attach(self.conn, repo_path=self.repo, harness="cursor", label="a", title="T")
        self.other = attach(self.conn, repo_path=self.repo, harness="codex", label="b", task=self.owner["task"])

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_notes_context_and_backup(self):
        short = note_add(self.conn, session=self.owner["session"], text="empty token bypasses the guard", days=7)
        seen = context(self.conn, session=self.other["session"])
        self.assertEqual(seen["summary"], None)
        self.assertEqual(seen["short_notes"][0]["body"], "empty token bypasses the guard")
        found = note_search(self.conn, session=self.other["session"], query="token guard")
        self.assertEqual(found["notes"][0]["id"], short["id"])
        note_promote(
            self.conn, session=self.owner["session"], note=short["id"],
            text="The refresh guard must cover an empty token", reason="test passed",
        )
        expired = note_add(self.conn, session=self.owner["session"], text="old hypothesis")
        self.conn.execute("UPDATE memories SET expires_at = '2000-01-01T00:00:00Z' WHERE id = ?", (expired["id"],))
        stale = note_add(self.conn, session=self.owner["session"], text="stale claim")
        note_add(self.conn, session=self.owner["session"], text="the new claim", supersedes=stale["id"])
        doomed = note_add(self.conn, session=self.owner["session"], text="forget me")
        note_forget(self.conn, session=self.owner["session"], note=doomed["id"])
        fresh = context(self.conn, session=self.other["session"])
        bodies = [note["body"] for note in fresh["short_notes"] + fresh["long_notes"]]
        self.assertIn("The refresh guard must cover an empty token", bodies)
        self.assertIn("the new claim", bodies)
        self.assertNotIn("empty token bypasses the guard", bodies)
        self.assertNotIn("old hypothesis", bodies)
        self.assertNotIn("stale claim", bodies)
        self.assertNotIn("forget me", bodies)
        saved = backup(self.home, Path(self.tmp.name) / "copy.sqlite3")
        copy = sqlite3.connect(saved["backup"])
        self.assertEqual(copy.execute("SELECT COUNT(*) FROM memories").fetchone()[0], 6)
        copy.close()

    def test_v1_database_migrates(self):
        path = Path(self.tmp.name) / "old" / "state.sqlite3"
        path.parent.mkdir()
        raw = sqlite3.connect(path)
        raw.executescript(SCHEMA)
        raw.execute("PRAGMA user_version=1")
        raw.commit()
        raw.close()
        conn = connect(path.parent)
        try:
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 3)
            conn.execute("SELECT path FROM transcript_sources").fetchall()
            conn.execute("SELECT body FROM memories").fetchall()
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
