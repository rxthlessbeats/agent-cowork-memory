import asyncio
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

from agent_cowork_memory.mcp_server import build_server


def git_repo(path):
    path.mkdir()
    subprocess.run(["git", "-C", path, "init", "-q"], check=True)
    subprocess.run(["git", "-C", path, "config", "user.email", "acm@localhost"], check=True)
    subprocess.run(["git", "-C", path, "config", "user.name", "acm"], check=True)
    (path / "README.md").write_text("playground\n")
    subprocess.run(["git", "-C", path, "add", "README.md"], check=True)
    subprocess.run(["git", "-C", path, "commit", "-q", "-m", "init"], check=True)


def payload(result):
    if getattr(result, "structuredContent", None):
        return result.structuredContent
    text = result.content[0].text
    return json.loads(text)


class McpTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.repo = Path(self.tmp.name) / "repo"
        git_repo(self.repo)
        self.server = build_server("cursor", self.home)

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, name, args):
        return asyncio.run(self.server.call_tool(name, args))

    def test_tools_and_conflict(self):
        tools = asyncio.run(self.server.list_tools())
        names = sorted(t.name for t in tools)
        self.assertEqual(names, [
            "attach", "context", "note_add", "note_search", "resume",
        ])

        created = payload(self.call("attach", {
            "repo_path": str(self.repo), "label": "cursor", "title": "Fix refresh",
        }))
        self.assertTrue(created["session"].startswith("acm_s_"))
        session = created["session"]
        task = created["task"]

        with self.assertRaises(ToolError) as caught:
            self.call("context", {"session": "acm_s_missing"})
        text = str(caught.exception)
        denied = json.loads(text[text.index("{"):])
        self.assertEqual(denied["error"], "invalid")
        self.assertEqual(denied["session"], "acm_s_missing")

        other = payload(self.call("attach", {
            "repo_path": str(self.repo), "label": "cursor", "task": task,
        }))
        self.call("note_add", {"session": session, "text": "refresh token lives in keychain"})
        seen = payload(self.call("context", {"session": other["session"]}))
        self.assertEqual(seen["session"], other["session"])
        self.assertIn("refresh token lives in keychain", json.dumps(seen))


if __name__ == "__main__":
    unittest.main()
