import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

from agent_cowork_memory.data import backup
from agent_cowork_memory.db import connect, fts5_ok, home_dir
from agent_cowork_memory.ledger import HARNESSES, AcmError, attach, checkpoint, claim, context, session_list, task_history, task_list
from agent_cowork_memory.memory import note_add, note_forget, note_promote, note_search
from agent_cowork_memory.transcript import chats, resume, transcript_read

EXIT = {"invalid": 2, "conflict": 3, "not_owner": 3, "not_allowed": 3, "unavailable": 4, "not_found": 4}


def mcp_command(uvx, harness):
    return [uvx, "agent-cowork-memory", "mcp", "--harness", harness]


def _print(payload, *, err=False):
    text = json.dumps(payload)
    print(text, file=sys.stderr if err else sys.stdout)


def _run(args, fn):
    home = home_dir(args.home)
    conn = connect(home)
    try:
        _print(fn(conn))
        return 0
    except AcmError as exc:
        _print({"error": exc.code, **exc.payload}, err=True)
        return EXIT.get(exc.code, 5)
    except sqlite3.OperationalError as exc:
        _print({"error": "database", "message": str(exc)}, err=True)
        return 5
    finally:
        conn.close()


def doctor(conn, home):
    db = home / "state.sqlite3"
    return {
        "session": None,
        "home": str(home),
        "database": db.exists(),
        "fts5": fts5_ok(),
        "writable": os.access(home if home.exists() else home.parent, os.W_OK),
    }


def _write_json(path, data):
    """Replace the file in one step, so an interrupted setup never leaves half a config."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as out:
        json.dump(data, out, indent=2)
        out.write("\n")
        temporary = out.name
    try:
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _opencode_file(home):
    if os.environ.get("OPENCODE_CONFIG"):
        return Path(os.environ["OPENCODE_CONFIG"])
    folder = home / ".config" / "opencode"
    return next((p for p in (folder / "opencode.json", folder / "opencode.jsonc") if p.exists()), folder / "opencode.json")


def setup_clients():
    uvx = shutil.which("uvx")
    if not uvx:
        raise RuntimeError("Install uv before running ACM setup.")
    uvx = str(Path(uvx).absolute())
    home = Path.home()
    cursor_file = (home / ".cursor" / "mcp.json").resolve()
    cursor_config = json.loads(cursor_file.read_text()) if cursor_file.exists() else {}
    if not isinstance(cursor_config, dict) or not isinstance(cursor_config.get("mcpServers", {}), dict):
        raise ValueError(f"Invalid MCP config: {cursor_file}")

    codex = shutil.which("codex")
    codex_file = Path(os.environ.get("CODEX_HOME", home / ".codex")) / "config.toml"
    codex_config = tomllib.loads(codex_file.read_text()) if codex and codex_file.exists() else {}
    servers = codex_config.get("mcp_servers", {})
    if not isinstance(servers, dict):
        raise ValueError(f"Invalid MCP config: {codex_file}")

    result = {}
    if not codex:
        result["codex"] = "not installed"
    elif "acm" in servers:
        result["codex"] = "already configured (left unchanged)"
    else:
        subprocess.run(
            [codex, "mcp", "add", "acm", "--", *mcp_command(uvx, "codex")],
            cwd=home, check=True, capture_output=True, text=True, timeout=15,
        )
        result["codex"] = "configured"

    cursor_servers = cursor_config.setdefault("mcpServers", {})
    if "acm" in cursor_servers:
        result["cursor"] = "already configured (left unchanged)"
    else:
        command = mcp_command(uvx, "cursor")
        cursor_servers["acm"] = {"command": command[0], "args": command[1:]}
        _write_json(cursor_file, cursor_config)
        result["cursor"] = "configured"

    opencode = shutil.which("opencode")
    opencode_file = _opencode_file(home)
    if not opencode:
        result["opencode"] = "not installed"
        return result
    entry = {"type": "local", "command": mcp_command(uvx, "opencode"), "enabled": True}
    try:
        config = json.loads(opencode_file.read_text()) if opencode_file.exists() else {}
    except json.JSONDecodeError:
        if opencode_file.suffix != ".jsonc":
            raise ValueError(f"Invalid MCP config: {opencode_file}") from None
        result["opencode"] = (
            f"not changed: {opencode_file} has comments, which setup would lose. "
            f'Add this under "mcp" yourself: "acm": {json.dumps(entry)}'
        )
        return result
    if not isinstance(config, dict) or not isinstance(config.get("mcp", {}), dict):
        raise ValueError(f"Invalid MCP config: {opencode_file}")
    servers = config.setdefault("mcp", {})
    if "acm" in servers:
        result["opencode"] = "already configured (left unchanged)"
    else:
        servers["acm"] = entry
        _write_json(opencode_file, config)
        result["opencode"] = "configured"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(prog="acm")
    parser.add_argument("--home", help="state directory (default ~/.agent-cowork-memory or ACM_HOME)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("attach")
    p.add_argument("--repo", required=True)
    p.add_argument("--harness", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--task")
    p.add_argument("--title")
    p.add_argument("--goal")
    p.add_argument("--native-id")

    p = sub.add_parser("context")
    p.add_argument("--session", required=True)

    p = sub.add_parser("claim")
    p.add_argument("--session", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--expect-version", type=int, required=True)

    p = sub.add_parser("checkpoint")
    p.add_argument("--session", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--expect-version", type=int, required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--next-action")
    p.add_argument("--blockers")
    p.add_argument("--status")
    p.add_argument("--ack-target")
    p.add_argument("--ack-cursor", type=int)

    p = sub.add_parser("transcript")
    tr = p.add_subparsers(dest="transcript_cmd", required=True)
    r = tr.add_parser("read")
    r.add_argument("--session", required=True)
    r.add_argument("--target", required=True)
    r.add_argument("--since-cursor", type=int)
    r.add_argument("--limit", type=int, default=20)

    d = sub.add_parser("delegate")
    d.add_argument("--repo", required=True)
    d.add_argument("--harness", required=True)
    d.add_argument("--summary", required=True)
    d.add_argument("--to", nargs=2, action="append", required=True, metavar=("AGENT", "TASK"))
    d.add_argument("--session")
    sub.add_parser("delegate-wait").add_argument("--session", required=True)

    r = sub.add_parser("resume")
    r.add_argument("--repo", required=True)
    r.add_argument("--harness", required=True)
    r.add_argument("--source", choices=HARNESSES)
    r.add_argument("--chat")
    r.add_argument("--limit", type=int, default=30)

    r = sub.add_parser("chats")
    r.add_argument("--repo", required=True)
    r.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("note")
    note = p.add_subparsers(dest="note_cmd", required=True)
    n = note.add_parser("add")
    n.add_argument("--session", required=True)
    n.add_argument("--text", required=True)
    n.add_argument("--tier", default="short")
    n.add_argument("--kind")
    n.add_argument("--days", type=int)
    n.add_argument("--supersedes")
    n.add_argument("--source")
    n.add_argument("--ack-target")
    n.add_argument("--ack-cursor", type=int)
    n = note.add_parser("search")
    n.add_argument("--session", required=True)
    n.add_argument("--query", required=True)
    n.add_argument("--task")
    n = note.add_parser("promote")
    n.add_argument("--session", required=True)
    n.add_argument("--note", required=True)
    n.add_argument("--text", required=True)
    n.add_argument("--reason", required=True)
    n = note.add_parser("forget")
    n.add_argument("--session", required=True)
    n.add_argument("--note", required=True)

    sub.add_parser("backup").add_argument("--to")

    p = sub.add_parser("task")
    task_sub = p.add_subparsers(dest="task_cmd", required=True)
    task_sub.add_parser("list").add_argument("--repo", required=True)
    task_sub.add_parser("history").add_argument("--task", required=True)

    p = sub.add_parser("session")
    session_sub = p.add_subparsers(dest="session_cmd", required=True)
    session_sub.add_parser("list").add_argument("--repo", required=True)

    sub.add_parser("doctor")
    sub.add_parser("setup")
    p = sub.add_parser("mcp")
    p.add_argument("--harness", choices=HARNESSES)

    args = parser.parse_args(argv)
    if args.cmd == "mcp":
        from agent_cowork_memory.mcp_server import serve
        serve(args.harness, home_dir(args.home))
        return 0
    if args.cmd == "setup":
        try:
            _print(setup_clients())
            return 0
        except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            _print({"error": "setup", "message": getattr(exc, "stderr", None) or str(exc)}, err=True)
            return 5
    if args.cmd == "doctor":
        home = home_dir(args.home)
        _print(doctor(None, home))
        return 0
    if args.cmd == "backup":
        if not (home_dir(args.home) / "state.sqlite3").exists():
            _print({"error": "not_found", "message": "no acm database to back up"}, err=True)
            return 4
        _print(backup(home_dir(args.home), args.to))
        return 0

    def go(conn):
        if args.cmd == "attach":
            return attach(
                conn, repo_path=args.repo, harness=args.harness, label=args.label,
                task=args.task, title=args.title, goal=args.goal, native_id=args.native_id,
            )
        if args.cmd == "context":
            return context(conn, session=args.session)
        if args.cmd == "claim":
            return claim(conn, session=args.session, task=args.task, expect_version=args.expect_version)
        if args.cmd == "checkpoint":
            return checkpoint(
                conn, session=args.session, task=args.task, expect_version=args.expect_version,
                summary=args.summary, next_action=args.next_action, blockers=args.blockers,
                status=args.status, ack_target=args.ack_target, ack_cursor=args.ack_cursor,
            )
        if args.cmd == "transcript" and args.transcript_cmd == "read":
            return transcript_read(
                conn, session=args.session, target=args.target,
                since_cursor=args.since_cursor, limit=args.limit,
            )
        if args.cmd == "delegate":
            from agent_cowork_memory.delegate import delegate
            return delegate(
                conn, harness=args.harness, repo_path=args.repo, summary=args.summary,
                tasks=[{"to": to, "task": task} for to, task in args.to], session=args.session,
            )
        if args.cmd == "delegate-wait":
            from agent_cowork_memory.delegate import delegate_wait
            return delegate_wait(conn, session=args.session)
        if args.cmd == "resume":
            return resume(conn, harness=args.harness, repo_path=args.repo, source=args.source, chat=args.chat, limit=args.limit)
        if args.cmd == "chats":
            return chats(conn, repo_path=args.repo, limit=args.limit)
        if args.cmd == "note" and args.note_cmd == "add":
            return note_add(
                conn, session=args.session, text=args.text, tier=args.tier, kind=args.kind,
                days=args.days, supersedes=args.supersedes, source=args.source,
                ack_target=args.ack_target, ack_cursor=args.ack_cursor,
            )
        if args.cmd == "note" and args.note_cmd == "search":
            return note_search(conn, session=args.session, query=args.query, task=args.task)
        if args.cmd == "note" and args.note_cmd == "promote":
            return note_promote(conn, session=args.session, note=args.note, text=args.text, reason=args.reason)
        if args.cmd == "note" and args.note_cmd == "forget":
            return note_forget(conn, session=args.session, note=args.note)
        if args.cmd == "task" and args.task_cmd == "list":
            return task_list(conn, repo_path=args.repo)
        if args.cmd == "task" and args.task_cmd == "history":
            return task_history(conn, task=args.task)
        if args.cmd == "session" and args.session_cmd == "list":
            return session_list(conn, repo_path=args.repo)
        raise AcmError("invalid", message="unknown command")

    return _run(args, go)


if __name__ == "__main__":
    sys.exit(main())
