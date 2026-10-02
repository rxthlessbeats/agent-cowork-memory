import sqlite3
from datetime import datetime, timedelta, timezone
import threading
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent_cowork_memory.data import backup
from agent_cowork_memory.db import MIGRATIONS, SCHEMA, connect, migrate
from agent_cowork_memory.ledger import AcmError, attach, context
from agent_cowork_memory.memory import note_add, note_forget, note_promote, note_search, sweep


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
        self.assertNotIn("summary", seen)
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
        self.assertEqual(copy.execute("SELECT COUNT(*) FROM memories").fetchone()[0], 2)
        copy.close()

    def test_search_treats_operator_words_as_text(self):
        note_add(self.conn, session=self.owner["session"], text="use redis or memcached")
        found = note_search(self.conn, session=self.other["session"], query="redis OR memcached")
        self.assertEqual([n["body"] for n in found["notes"]], ["use redis or memcached"])
        self.assertEqual(note_search(self.conn, session=self.other["session"], query="NOT")["notes"], [])
        rain = note_add(self.conn, session=self.owner["session"], text="if it rains, use the cafe")
        self.assertEqual([n["id"] for n in note_search(self.conn, session=self.other["session"], query="rain")["notes"]], [rain["id"]])

    def test_long_notes_survive_many_short_notes(self):
        note_add(self.conn, session=self.owner["session"], text="use pnpm, not npm", tier="long")
        for n in range(40):
            note_add(self.conn, session=self.owner["session"], text=f"progress {n} " + "x" * 400)
        seen = context(self.conn, session=self.other["session"])
        self.assertEqual([n["body"] for n in seen["long_notes"]], ["use pnpm, not npm"])
        self.assertGreater(seen["omitted"]["short"], 0)

    def test_context_shows_whole_project_own_task_first(self):
        elsewhere = attach(self.conn, repo_path=self.repo, harness="claude", label="c", title="Other task")
        note_add(self.conn, session=elsewhere["session"], text="other task, newer")
        note_add(self.conn, session=self.owner["session"], text="my task, older")
        note_add(self.conn, session=elsewhere["session"], text="use pnpm, not npm", tier="long")
        seen = context(self.conn, session=self.other["session"])
        self.assertEqual([n["body"] for n in seen["short_notes"]], ["my task, older", "other task, newer"])
        self.assertEqual([n["body"] for n in seen["long_notes"]], ["use pnpm, not npm"])

    def test_context_clips_and_caps_other_tasks_short_notes(self):
        elsewhere = attach(self.conn, repo_path=self.repo, harness="claude", label="c", title="Other task")
        for n in range(7):
            note_add(self.conn, session=elsewhere["session"], text=f"result {n} " + "x" * 400, kind="result")
        note_add(self.conn, session=self.owner["session"], text="mine " + "y" * 400)
        seen = context(self.conn, session=self.other["session"])
        bodies = [n["body"] for n in seen["short_notes"]]
        self.assertEqual(bodies[0], "mine " + "y" * 400)
        self.assertEqual([b.split()[1] for b in bodies[1:]], ["6", "5", "4", "3", "2"])
        self.assertTrue(all(len(b) <= 200 for b in bodies[1:]))
        self.assertEqual(seen["omitted"]["short"], 2)
        full = note_search(self.conn, session=self.other["session"], query="result 6")
        self.assertEqual(len(full["notes"][0]["body"]), len("result 6 ") + 400)

    def test_hold_blocks_the_other_agent_until_release(self):
        mine = context(self.conn, session=self.owner["session"], hold=["plan.md", "notes/a.md"])
        self.assertEqual(sorted(item["path"] for item in mine["held"]), ["notes/a.md", "plan.md"])
        self.assertNotIn("busy", mine)
        other = context(self.conn, session=self.other["session"], hold=["plan.md", "budget.md"])
        self.assertEqual(other["busy"], [{"path": "plan.md", "agent": "a"}])
        self.assertEqual(sorted(item["path"] for item in other["held"]), ["notes/a.md", "plan.md"])
        context(self.conn, session=self.owner["session"], hold=[])
        taken = context(self.conn, session=self.other["session"], hold=["plan.md"])
        self.assertNotIn("busy", taken)
        self.assertEqual(taken["held"], [{"path": "plan.md", "agent": "b"}])
        with self.assertRaises(AcmError):
            context(self.conn, session=self.owner["session"], hold=["../secret"])

    def test_hold_paths_normalize_and_quiet_holds_lapse(self):
        context(self.conn, session=self.owner["session"], hold=["./plan.md"])
        other = context(self.conn, session=self.other["session"], hold=["plan.md"])
        self.assertEqual(other["busy"], [{"path": "plan.md", "agent": "a"}])
        quiet = "UPDATE sessions SET last_seen_at = '2000-01-01T00:00:00Z' WHERE id = ?"
        self.conn.execute(quiet, (self.owner["session"],))
        note_add(self.conn, session=self.owner["session"], text="still editing plan.md")
        self.assertIn("busy", context(self.conn, session=self.other["session"], hold=["plan.md"]))
        self.conn.execute("UPDATE sessions SET label = 'codex-work' WHERE id = ?", (self.owner["session"],))
        self.conn.execute(
            """INSERT INTO delegations (id, caller_session_id, folder, kind, agent_name, summary, task, prompt, state, started_at)
               VALUES ('acm_j_1', ?, ?, 'codex', 'codex-work', 's', 't', 'p', 'running', '2026-09-30T00:00:00Z')""",
            (self.other["session"], str(self.repo.resolve())),
        )
        self.conn.execute(quiet, (self.owner["session"],))
        self.assertIn("busy", context(self.conn, session=self.other["session"], hold=["plan.md"]))
        self.conn.execute("UPDATE delegations SET state = 'done'")
        taken = context(self.conn, session=self.other["session"], hold=["plan.md"])
        self.assertNotIn("busy", taken)

    def test_context_shows_who_is_working_and_sweep_caps_results(self):
        self.conn.execute(
            """INSERT INTO delegations (
                id, caller_session_id, folder, kind, agent_name, summary, task, prompt, state, started_at
            ) VALUES ('acm_j_1', ?, ?, 'codex', 'codex-work', 's', 'Write plan.md', 'p', 'running', '2026-09-30T00:00:00Z')""",
            (self.owner["session"], str(self.repo.resolve())),
        )
        self.conn.commit()
        seen = context(self.conn, session=self.other["session"])
        self.assertEqual(seen["working"], [{"agent": "codex-work", "state": "running", "task": "Write plan.md"}])
        for n in range(3):
            note_add(self.conn, session=self.owner["session"], text=f"result {n}", kind="result")
        with mock.patch("agent_cowork_memory.memory._KEEP_RESULTS", 2):
            sweep(self.conn, self.owner["project"])
        left = [row["body"] for row in self.conn.execute(
            "SELECT body FROM memories WHERE kind = 'result' ORDER BY created_at, rowid")]
        self.assertEqual(left, ["result 1", "result 2"])

    def idle(self, session, days):
        stamp = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.conn.execute("UPDATE sessions SET last_seen_at = ? WHERE id = ?", (stamp, session))

    def sessions(self):
        return {row["id"] for row in self.conn.execute("SELECT id FROM sessions")}

    def test_sweep_prunes_idle_sessions_and_archives_their_task(self):
        lone = attach(self.conn, repo_path=self.repo, harness="claude", label="delegate", title="Old job")
        self.conn.execute(
            "INSERT INTO transcript_sources (id, session_id, path, generation, size, fingerprint) VALUES ('src', ?, 'p', 1, 0, 'f')",
            (lone["session"],),
        )
        self.conn.execute(
            "INSERT INTO transcript_cursors (source_id, consumer_session_id, generation, byte_offset) VALUES ('src', ?, 1, 0)",
            (self.owner["session"],),
        )
        self.conn.execute(
            """INSERT INTO delegations (id, caller_session_id, folder, kind, agent_name, summary, task, prompt, state, started_at)
               VALUES ('acm_j_1', ?, ?, 'codex', 'codex-repo', 's', 't', 'p', 'done', '2026-08-01T00:00:00Z')""",
            (lone["session"], str(self.repo.resolve())),
        )
        self.idle(lone["session"], 31)
        sweep(self.conn, self.owner["project"])
        self.assertNotIn(lone["session"], self.sessions())
        for table, column in (("task_sessions", "session_id"), ("transcript_sources", "session_id"),
                              ("delegations", "caller_session_id")):
            self.assertIsNone(self.conn.execute(f"SELECT 1 FROM {table} WHERE {column} = ?", (lone["session"],)).fetchone())
        self.assertIsNone(self.conn.execute("SELECT 1 FROM transcript_cursors").fetchone())
        archived = self.conn.execute("SELECT archived_at FROM tasks WHERE id = ?", (lone["task"],)).fetchone()
        self.assertIsNotNone(archived["archived_at"])
        self.assertEqual(self.conn.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_sweep_keeps_sessions_still_in_use(self):
        holder = attach(self.conn, repo_path=self.repo, harness="claude", label="h", title="Holder")
        context(self.conn, session=holder["session"], hold=["plan.md"])
        caller = attach(self.conn, repo_path=self.repo, harness="claude", label="c", title="Caller")
        self.conn.execute(
            """INSERT INTO delegations (id, caller_session_id, folder, kind, agent_name, summary, task, prompt, state, started_at)
               VALUES ('acm_j_1', ?, ?, 'codex', 'codex-repo', 's', 't', 'p', 'running', '2026-08-01T00:00:00Z')""",
            (caller["session"], str(self.repo.resolve())),
        )
        worker = attach(self.conn, repo_path=self.repo, harness="codex", label="codex-repo", task=caller["task"])
        writer = attach(self.conn, repo_path=self.repo, harness="claude", label="w", title="Writer")
        note_add(self.conn, session=writer["session"], text="use pnpm", tier="long")
        recent = attach(self.conn, repo_path=self.repo, harness="claude", label="r", title="Recent")
        kept = [holder, caller, worker, writer]
        for row in kept:
            self.idle(row["session"], 31)
        self.idle(recent["session"], 29)
        with mock.patch("agent_cowork_memory.memory._HOLD_HOURS", 24 * 365):
            sweep(self.conn, self.owner["project"])
        self.assertLessEqual({row["session"] for row in kept + [recent]}, self.sessions())

    def test_task_with_a_live_note_stays_open_after_its_last_session_goes(self):
        lone = attach(self.conn, repo_path=self.repo, harness="claude", label="delegate", title="Noted")
        note_add(self.conn, session=lone["session"], text="halfway through the migration")
        self.idle(lone["session"], 31)
        sweep(self.conn, self.owner["project"])
        self.assertNotIn(lone["session"], self.sessions())
        task = self.conn.execute("SELECT archived_at FROM tasks WHERE id = ?", (lone["task"],)).fetchone()
        self.assertIsNone(task["archived_at"])
        note = self.conn.execute("SELECT body FROM memories WHERE task_id = ?", (lone["task"],)).fetchone()
        self.assertEqual(note["body"], "halfway through the migration")
        self.assertEqual(self.conn.execute("PRAGMA foreign_key_check").fetchall(), [])

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
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 6)
            conn.execute("SELECT path FROM holds").fetchall()
            conn.execute("SELECT path FROM transcript_sources").fetchall()
            conn.execute("SELECT body FROM memories").fetchall()
        finally:
            conn.close()

    def test_concurrent_first_connects_migrate_once(self):
        home = Path(self.tmp.name) / "race"
        start, errors = threading.Barrier(8), []
        once = MIGRATIONS + ["INSERT INTO projects (id, git_common_dir, created_at) VALUES ('p', 'x', 'now');"]

        def go():
            start.wait()
            try:
                connect(home).close()
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=go) for _ in range(8)]
        with mock.patch("agent_cowork_memory.db.MIGRATIONS", once):
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        self.assertEqual(errors, [])
        conn = sqlite3.connect(home / "state.sqlite3")
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0], 1)
        conn.close()

    def test_failed_migration_step_changes_nothing(self):
        conn = sqlite3.connect(":memory:", isolation_level=None)
        broken = MIGRATIONS[:1] + ["CREATE TABLE half (x); SELECT * FROM missing;"]
        with mock.patch("agent_cowork_memory.db.MIGRATIONS", broken), self.assertRaises(sqlite3.OperationalError):
            migrate(conn)
        conn.rollback()
        self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 1)
        self.assertIsNone(conn.execute("SELECT name FROM sqlite_master WHERE name = 'half'").fetchone())


if __name__ == "__main__":
    unittest.main()
