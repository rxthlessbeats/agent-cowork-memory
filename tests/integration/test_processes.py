"""Real processes: fake agent binaries on PATH, and `acm mcp` over stdio."""
import asyncio
import json
import os
import sys
import tempfile
import time
import unittest
import warnings
from pathlib import Path
from unittest import mock

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import Implementation

from agent_cowork_memory.db import connect
from agent_cowork_memory.delegate import Deps, delegate
from agent_cowork_memory.ledger import context

FAKE_CODEX = """#!/bin/sh
while [ $# -gt 1 ]; do
  [ "$1" = "-o" ] && answer="$2"
  shift
done
printf '%s' "$1" > codex-prompt.txt
echo "# plan" > plan.md
printf 'codex wrote plan.md, delegated=%s' "$ACM_DELEGATED" > "$answer"
"""
FAKE_CLAUDE = """#!/bin/sh
echo boom >&2
exit 3
"""
ACM = "import sys; from agent_cowork_memory.cli import main; sys.exit(main(sys.argv[1:]))"


class Agents(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home, self.work, bin_dir = base / "home", base / "work", base / "bin"
        self.work.mkdir()
        bin_dir.mkdir()
        for name, script in (("codex", FAKE_CODEX), ("claude", FAKE_CLAUDE)):
            (bin_dir / name).write_text(script)
            (bin_dir / name).chmod(0o755)
        self.path = f"{bin_dir}:/usr/bin:/bin"

    def tearDown(self):
        self.tmp.cleanup()


class BackgroundTest(Agents):
    def test_real_processes_finish_and_fail(self):
        conn = connect(self.home)
        self.addCleanup(conn.close)
        deps = Deps(use_herdr=lambda: False, delegated=lambda: False, sleep=lambda s: time.sleep(0.05))
        with mock.patch.dict(os.environ, {"PATH": self.path}), warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            out = delegate(conn, harness="cursor", repo_path=self.work, summary="Plan a trip.", tasks=[
                {"to": "codex", "task": "Write plan.md."},
                {"to": "claude", "task": "Write packing.md."},
            ], deps=deps)

        jobs = {j["to"]: j for j in out["jobs"]}
        self.assertEqual(jobs["codex"]["state"], "done")
        self.assertEqual(jobs["codex"]["result"], "codex wrote plan.md, delegated=1")
        self.assertEqual(jobs["claude"]["state"], "gone")
        self.assertIn("code 3", jobs["claude"]["result"])
        self.assertIn("boom", jobs["claude"]["result"])
        self.assertTrue((self.work / "plan.md").exists())
        prompt = (self.work / "codex-prompt.txt").read_text()
        self.assertIn(f"[acm job {jobs['codex']['job']}]", prompt)
        self.assertIn("## Your task\nWrite plan.md.", prompt)
        self.assertIn("tail -f", out["watch"])
        self.assertIn("codex wrote plan.md", json.dumps(context(conn, session=out["session"])))


class StdioTest(Agents):
    def test_acm_mcp_over_stdio(self):
        params = StdioServerParameters(
            command=sys.executable, args=["-c", ACM, "--home", str(self.home), "mcp", "--harness", "cursor"],
            env={"PATH": self.path},
        )

        cards = []

        async def run():
            async with stdio_client(params) as (read, write), ClientSession(read, write) as client:
                await client.initialize()
                tools = sorted(t.name for t in (await client.list_tools()).tools)

                async def call(name, args):
                    result = await client.call_tool(name, args)
                    self.assertFalse(result.is_error, result.content)
                    if name == "delegate":
                        cards.append(result.content[0].text)
                    return result.structured_content or json.loads(result.content[-1].text)

                attached = await call("attach", {"repo_path": str(self.work), "label": "cursor", "title": "Trip"})
                await call("note_add", {"session": attached["session"], "text": "trip is 3 days", "tier": "long"})
                held = await call("context", {"session": attached["session"], "hold": ["notes.md"]})
                sent = await call("delegate", {
                    "repo_path": str(self.work), "summary": "Plan a trip.",
                    "tasks": [{"to": "codex", "task": "Write plan.md."}],
                })
                return tools, held, sent

        tools, held, sent = asyncio.run(run())
        self.assertIn("delegate", tools)
        self.assertIn("trip is 3 days", json.dumps(held))
        self.assertIn("notes.md", json.dumps(held["held"]))
        self.assertEqual([(j["to"], j["state"]) for j in sent["jobs"]], [("codex", "done")])
        self.assertTrue(cards[0].startswith("acm · delegate(tasks=1 · background)\n\ncodex\nWrite plan.md."), cards[0])
        self.assertTrue((self.work / "plan.md").exists())

    def test_harness_comes_from_the_client_name(self):
        params = StdioServerParameters(
            command=sys.executable, args=["-c", ACM, "--home", str(self.home), "mcp"], env={"PATH": self.path},
        )

        async def attach_as(name):
            info = Implementation(name=name, version="1")
            async with stdio_client(params) as (read, write), ClientSession(read, write, client_info=info) as client:
                await client.initialize()
                return await client.call_tool("attach", {"repo_path": str(self.work), "label": name, "title": "Trip"})

        self.assertFalse(asyncio.run(attach_as("claude-code")).is_error)
        unknown = asyncio.run(attach_as("some-editor"))
        self.assertTrue(unknown.is_error)
        self.assertIn("--harness", unknown.content[0].text)
        conn = connect(self.home)
        self.assertEqual([r["harness"] for r in conn.execute("SELECT harness FROM sessions")], ["claude"])
        conn.close()


if __name__ == "__main__":
    unittest.main()
