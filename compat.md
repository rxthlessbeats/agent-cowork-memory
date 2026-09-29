# M0 compatibility record

Recorded 2026-09-29 on this machine. No hooks were installed.

| Component | Version |
| --- | --- |
| Python | 3.12.14 |
| SQLite | 3.53.1, FTS5 available |
| uv | 0.12.17 |
| Codex CLI | 0.158.0 |
| Claude Code | 2.1.284 |
| Cursor | 3.22.12 (`3a92974361033b2051526321308c2740fe5912c0`) |

`acm` is not on `PATH`. The old no-op `/home/user/code/agent-share/agent_share.py` is gone, and `~/.cursor/hooks.json` does not call it.

`~/.agent-cowork-memory/` is writable by this user (uid 1000). Codex, Cursor, and Claude Code run as that user, so they can write the same directory. This was not rechecked by launching each harness.

## Transcripts

Synthetic shapes, not copies of real chats, are in `tests/fixtures/`.

| Harness | Path | Tool-call arguments | When the file is written |
| --- | --- | --- | --- |
| Codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | `response_item` payload `function_call.arguments` is a JSON **string**. `custom_tool_call.input` is also a string. | Present in finished session files. Not timed while a turn was still running. |
| Cursor | `~/.cursor/projects/<project>/agent-transcripts/<id>/<id>.jsonl` | Assistant `message.content[]` block `tool_use.input` is an object. The id is the filename, not a field in the line. | Completed turns are already in the file before the conversation ends. A turn still running may be absent. |
| Claude Code | `~/.claude/projects/<path-with-dashes>/<session-id>.jsonl` | Not seen. The captured session (`81931fb1-502b-44b5-9cdc-8eb06f07d90f` in `acm-playground`) only said "pong" and has no `tool_use`. The fixture's `tool_use` block follows the published content-block shape (`type`, `name`, `input`). | The file existed as soon as `claude -p` exited. Mid-turn writes were not sampled. Official docs say the file is append-only. |

Claude user `message.content` in that print session is a string. Assistant `message.content` is a list of blocks. Codex message content is a list of `input_text` / `output_text`. Cursor content is a list of `text` and `tool_use` blocks.

Session ids worth knowing: Codex `session_meta.payload.session_id` (and `CODEX_THREAD_ID` in the shell, not in the MCP server). Claude filename and `sessionId`. Cursor transcript filename (and hooks, not the MCP server).

## Project identity

`acm-playground` is a plain folder (no git) at `/home/user/code/magnusl/acm-playground`, so it exercises the no-git fallback: the folder path is the project. Worktree sharing, for folders inside a git repo, is implemented as: one project per `git rev-parse --git-common-dir`, so linked worktrees match and a separate clone does not.

## Still manual

- Trust the playground in Codex or its project `.codex/config.toml` is ignored. Codex Desktop still ignores project MCP config.
- Enable the server in Cursor's MCP settings after `.cursor/mcp.json` exists.
- Approve Claude's project `.mcp.json` once.
