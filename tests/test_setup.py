import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_cowork_memory.cli import PACKAGE_SOURCE, setup_clients


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
                self.assertEqual(setup_clients(), {"codex": "configured", "cursor": "configured"})
                self.assertEqual(setup_clients(), {
                    "codex": "already configured (left unchanged)",
                    "cursor": "already configured (left unchanged)",
                })

            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0], [
                "/tmp/codex", "mcp", "add", "acm", "--",
                "/tmp/uvx", "--from", PACKAGE_SOURCE, "acm", "mcp", "--harness", "codex",
            ])
            servers = json.loads(cursor_file.read_text())["mcpServers"]
            self.assertEqual(servers["other"], {"command": "other"})
            self.assertEqual(servers["acm"], {
                "command": "/tmp/uvx",
                "args": ["--from", PACKAGE_SOURCE, "acm", "mcp", "--harness", "cursor"],
            })
