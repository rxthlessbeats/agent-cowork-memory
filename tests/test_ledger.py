import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from agent_cowork_memory.cli import main
from agent_cowork_memory.db import connect
from agent_cowork_memory.ledger import checkpoint


def git_repo(path):
    path.mkdir(parents=True)
    subprocess.run(["git", "-C", path, "init", "-q"], check=True)
    subprocess.run(["git", "-C", path, "config", "user.email", "acm@localhost"], check=True)
    subprocess.run(["git", "-C", path, "config", "user.name", "acm"], check=True)
    (path / "README.md").write_text("playground\n")
    subprocess.run(["git", "-C", path, "add", "README.md"], check=True)
    subprocess.run(["git", "-C", path, "commit", "-q", "-m", "init"], check=True)


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.repo = Path(self.tmp.name) / "repo"
        git_repo(self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def run_acm(self, *args):
        code = main(["--home", str(self.home), *args])
        return code

    def test_two_writers_and_owner(self):
        import io
        from contextlib import redirect_stderr, redirect_stdout

        def call(*args):
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(["--home", str(self.home), *args])
            raw = out.getvalue() or err.getvalue()
            return code, json.loads(raw)

        code, created = call("attach", "--repo", str(self.repo), "--harness", "codex", "--label", "a", "--title", "Fix refresh")
        self.assertEqual(code, 0)
        self.assertEqual(created["version"], 1)
        self.assertTrue(created["session"].startswith("acm_s_"))
        task = created["task"]
        owner = created["session"]

        code, other = call("attach", "--repo", str(self.repo), "--harness", "cursor", "--label", "a", "--task", task)
        self.assertNotEqual(other["session"], owner)

        code, denied = call("checkpoint", "--session", other["session"], "--task", task, "--expect-version", "1", "--summary", "nope")
        self.assertEqual(code, 3)
        self.assertEqual(denied["error"], "not_owner")
        self.assertEqual(denied["hint"], "claim")

        code, wrote = call("checkpoint", "--session", owner, "--task", task, "--expect-version", "1", "--summary", "first")
        self.assertEqual(code, 0)
        self.assertEqual(wrote["version"], 2)

        code, lost = call("checkpoint", "--session", owner, "--task", task, "--expect-version", "1", "--summary", "stale")
        self.assertEqual(code, 3)
        self.assertEqual(lost["error"], "conflict")
        self.assertEqual(lost["version"], 2)

        code, seen = call("context", "--session", other["session"])
        self.assertEqual(seen["summary"], "first")
        self.assertEqual(seen["session"], other["session"])

        code, claimed = call("claim", "--session", other["session"], "--task", task, "--expect-version", "2")
        self.assertEqual(claimed["owner"], other["session"])
        self.assertEqual(claimed["version"], 3)

        code, hist = call("task", "history", "--task", task)
        self.assertEqual([row["version"] for row in hist["history"]], [1, 2, 3])

    def test_worktrees_share_project(self):
        wt = Path(self.tmp.name) / "wt"
        subprocess.run(["git", "-C", self.repo, "worktree", "add", "-q", str(wt)], check=True)
        import io
        from contextlib import redirect_stdout

        def call(*args):
            out = io.StringIO()
            with redirect_stdout(out):
                main(["--home", str(self.home), *args])
            return json.loads(out.getvalue())

        a = call("attach", "--repo", str(self.repo), "--harness", "codex", "--label", "main", "--title", "One")
        b = call("attach", "--repo", str(wt), "--harness", "claude", "--label", "wt", "--task", a["task"])
        self.assertEqual(a["project"], b["project"])

    def test_two_connections(self):
        import io
        from contextlib import redirect_stdout
        out = io.StringIO()
        with redirect_stdout(out):
            main(["--home", str(self.home), "attach", "--repo", str(self.repo), "--harness", "codex", "--label", "a", "--title", "T"])
        created = json.loads(out.getvalue())
        c1 = connect(self.home)
        c2 = connect(self.home)
        try:
            checkpoint(c1, session=created["session"], task=created["task"], expect_version=1, summary="from c1")
            seen = c2.execute("SELECT version, summary FROM tasks WHERE id = ?", (created["task"],)).fetchone()
            self.assertEqual(seen["version"], 2)
            self.assertEqual(seen["summary"], "from c1")
        finally:
            c1.close()
            c2.close()


if __name__ == "__main__":
    unittest.main()
