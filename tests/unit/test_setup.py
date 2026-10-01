import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_cowork_memory.cli import mcp_command, setup_clients


class SetupTest(unittest.TestCase):
    def test_setup_preserves_other_servers_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            cursor_file = home / ".cursor" / "mcp.json"
            cursor_file.parent.mkdir()
            cursor_file.write_text(json.dumps({"mcpServers": {"other": {"command": "other"}}}))
            calls = []

            def run(command, **kwargs):
                calls.append(command)
                codex_file = home / ".codex" / "config.toml"
                codex_file.parent.mkdir()
                codex_file.write_text('[mcp_servers.acm]\ncommand = "/tmp/acm"\n')

            def which(name):
                self.assertNotEqual(name, "acm")
                return f"/tmp/{name}"

            with patch("agent_cowork_memory.cli.Path.home", return_value=home), \
                 patch("agent_cowork_memory.cli.shutil.which", side_effect=which), \
                 patch("agent_cowork_memory.cli.subprocess.run", side_effect=run), \
                 patch.dict("agent_cowork_memory.cli.os.environ", {"CODEX_HOME": str(home / ".codex")}, clear=True):
                self.assertEqual(setup_clients(), {"codex": "configured", "cursor": "configured", "opencode": "configured"})
                self.assertEqual(setup_clients(), {
                    "codex": "already configured (left unchanged)",
                    "cursor": "already configured (left unchanged)",
                    "opencode": "already configured (left unchanged)",
                })
            opencode = json.loads((home / ".config" / "opencode" / "opencode.json").read_text())
            self.assertEqual(opencode["mcp"]["acm"]["command"][-1], "opencode")

            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0], ["/tmp/codex", "mcp", "add", "acm", "--", *mcp_command("/tmp/uvx", "codex")])
            servers = json.loads(cursor_file.read_text())["mcpServers"]
            self.assertEqual(servers["other"], {"command": "other"})
            cursor = mcp_command("/tmp/uvx", "cursor")
            self.assertEqual(servers["acm"], {"command": cursor[0], "args": cursor[1:]})

    def test_opencode_jsonc_is_used_and_never_loses_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            folder = home / ".config" / "opencode"
            folder.mkdir(parents=True)
            jsonc = folder / "opencode.jsonc"

            def which(name):
                return None if name == "codex" else f"/tmp/{name}"

            with patch("agent_cowork_memory.cli.Path.home", return_value=home), \
                 patch("agent_cowork_memory.cli.shutil.which", side_effect=which), \
                 patch.dict("agent_cowork_memory.cli.os.environ", {}, clear=True):
                jsonc.write_text('{\n  // my theme\n  "theme": "dark"\n}\n')
                kept = setup_clients()["opencode"]
                self.assertTrue(kept.startswith("not changed"))
                self.assertIn("// my theme", jsonc.read_text())

                jsonc.write_text('{"theme": "dark"}\n')
                self.assertEqual(setup_clients()["opencode"], "configured")
                self.assertIn("acm", json.loads(jsonc.read_text())["mcp"])
                self.assertFalse((folder / "opencode.json").exists())
