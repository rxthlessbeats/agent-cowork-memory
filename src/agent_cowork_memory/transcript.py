import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from agent_cowork_memory.ledger import AcmError, new_id
from agent_cowork_memory.readers import claude, codex, cursor

READERS = {"codex": codex, "cursor": cursor, "claude": claude}
_TOOL_MARKERS = ("tool_use", "function_call", "custom_tool_call")
_MAX_SCAN = 1_000_000
# ponytail: one pass over files touched since attach, cap 8MB each. Index if a repo grows past that.


def default_root(harness):
    home = Path.home()
    if harness == "codex":
        return Path(os.environ.get("CODEX_HOME", home / ".codex")) / "sessions"
    if harness == "cursor":
        return Path(os.environ.get("CURSOR_TRANSCRIPTS", home / ".cursor" / "projects"))
    return Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude")) / "projects"


def _attached_epoch(stamp):
    return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


def _fingerprint(raw):
    return hashlib.sha256(raw[:256]).hexdigest()


def _session(conn, session_id):
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        raise AcmError("invalid", message="unknown session", hint="attach", session=session_id)
    return row


def _same_task(conn, caller, target):
    row = conn.execute(
        """SELECT 1 FROM task_sessions a
           JOIN task_sessions b ON a.task_id = b.task_id
           WHERE a.session_id = ? AND b.session_id = ?""",
        (caller, target),
    ).fetchone()
    if row is None:
        raise AcmError("not_found", message="session is not on this task", session=caller)


def _tool_line(text, session_id):
    return session_id in text and any(marker in text for marker in _TOOL_MARKERS)


def bind(conn, session_row, root):
    existing = conn.execute(
        "SELECT * FROM transcript_sources WHERE session_id = ?", (session_row["id"],)
    ).fetchone()
    if existing:
        if not Path(existing["path"]).exists():
            return existing, "unavailable"
        return existing, None
    root = Path(root)
    if not root.exists():
        return None, "pending"
    since = _attached_epoch(session_row["attached_at"]) - 1
    matches = []
    if root.is_file():
        candidates = [root]
    else:
        candidates = [p for p in root.rglob("*.jsonl") if p.is_file() and p.stat().st_mtime >= since]
    for path in candidates:
        try:
            blob = path.read_bytes()[:8_000_000]
        except OSError:
            continue
        text = blob.decode("utf-8", "replace")
        if _tool_line(text, session_row["id"]):
            matches.append(path)
    if not matches:
        return None, "pending"
    if len(matches) > 1:
        return None, "ambiguous"
    path = matches[0]
    native = _native_id(session_row["harness"], path)
    raw = path.read_bytes()
    source_id = new_id("acm_src_")
    conn.execute(
        """INSERT INTO transcript_sources (
            id, session_id, path, native_id, generation, size, fingerprint
        ) VALUES (?, ?, ?, ?, 1, ?, ?)""",
        (source_id, session_row["id"], str(path), native, len(raw), _fingerprint(raw)),
    )
    if native and not session_row["native_id"]:
        conn.execute("UPDATE sessions SET native_id = ?, transcript_path = ? WHERE id = ?", (native, str(path), session_row["id"]))
    else:
        conn.execute("UPDATE sessions SET transcript_path = ? WHERE id = ?", (str(path), session_row["id"]))
    return conn.execute("SELECT * FROM transcript_sources WHERE id = ?", (source_id,)).fetchone(), None


def _native_id(harness, path):
    reader = READERS[harness]
    native = None
    with path.open("rb") as handle:
        for _ in range(20):
            line = handle.readline()
            if not line:
                break
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            found = reader.native_id(obj, path)
            if found:
                native = found
                break
    return native or (path.stem if harness == "claude" else path.parent.name)


def _sync_generation(conn, source):
    path = Path(source["path"])
    if not path.exists():
        return None
    raw = path.read_bytes()
    fingerprint = _fingerprint(raw)
    if len(raw) < source["size"] or fingerprint != source["fingerprint"]:
        generation = source["generation"] + 1
        conn.execute(
            "UPDATE transcript_sources SET generation = ?, size = ?, fingerprint = ? WHERE id = ?",
            (generation, len(raw), fingerprint, source["id"]),
        )
        return conn.execute("SELECT * FROM transcript_sources WHERE id = ?", (source["id"],)).fetchone(), raw
    if len(raw) != source["size"]:
        conn.execute("UPDATE transcript_sources SET size = ? WHERE id = ?", (len(raw), source["id"]))
        source = conn.execute("SELECT * FROM transcript_sources WHERE id = ?", (source["id"],)).fetchone()
    return source, raw


def _parse(harness, raw, start, max_scan=_MAX_SCAN):
    reader = READERS[harness]
    records = []
    unknown = 0
    offset = start
    if offset > 0 and (offset >= len(raw) or raw[offset - 1:offset] != b"\n"):
        newline = raw.find(b"\n", offset)
        offset = len(raw) if newline < 0 else newline + 1
    scanned = 0
    truncated = False
    while offset < len(raw) and scanned < max_scan:
        newline = raw.find(b"\n", offset)
        if newline < 0:
            break
        line_end = newline + 1
        scanned += line_end - offset
        try:
            obj = json.loads(raw[offset:newline])
        except json.JSONDecodeError:
            offset = line_end
            continue
        status, messages = reader.visible(obj)
        if status == "unknown":
            unknown += 1
        for message in messages:
            records.append({
                "start": offset,
                "end": line_end,
                "role": message["role"],
                "text": message["text"],
                "timestamp": message.get("timestamp"),
            })
        offset = line_end
    if offset < len(raw):
        truncated = True
    return records, offset, unknown, truncated


def transcript_read(conn, *, session, target, since_cursor=None, limit=20, root=None):
    _session(conn, session)
    other = _session(conn, target)
    _same_task(conn, session, target)
    source, status = bind(conn, other, root or default_root(other["harness"]))
    if status:
        conn.commit()
        return {"session": session, "status": status, "records": [], "target": target}
    synced = _sync_generation(conn, source)
    if synced is None:
        return {"session": session, "status": "unavailable", "records": [], "target": target, "path": source["path"]}
    source, raw = synced
    if since_cursor is None:
        start = max(0, len(raw) - _MAX_SCAN)
    else:
        start = since_cursor
    records, consumed, unknown, truncated = _parse(other["harness"], raw, start)
    if since_cursor is None:
        if len(records) > limit:
            records = records[-limit:]
    elif len(records) > limit:
        records = records[:limit]
        truncated = True
    diagnostic = None
    if not records and unknown:
        diagnostic = "unrecognized records"
    result = {
        "session": session,
        "status": "ok",
        "target": target,
        "generation": source["generation"],
        "native_id": source["native_id"],
        "next_cursor": records[-1]["end"] if records else consumed,
        "truncated": truncated,
        "records": [
            {
                "source": source["id"],
                "generation": source["generation"],
                "start": rec["start"],
                "end": rec["end"],
                "native_id": source["native_id"],
                "role": rec["role"],
                "text": rec["text"],
                "timestamp": rec["timestamp"],
            }
            for rec in records
        ],
    }
    if diagnostic:
        result["diagnostic"] = diagnostic
    conn.commit()
    return result


def _slug(path):
    return str(path).strip("/").replace("/", "-")


def _related(workspace, repo_root):
    return workspace == repo_root or repo_root in workspace.parents or workspace in repo_root.parents


def latest_chat(harness, repo_root, root=None):
    """Newest chat whose workspace is the repo, inside it, or contains it."""
    repo_root = Path(repo_root)
    base = Path(root) if root else default_root(harness)
    if not base.exists():
        return None, None
    if harness in ("cursor", "claude"):
        found = []
        for workspace in (repo_root, *repo_root.parents):
            if harness == "cursor":
                files = (base / _slug(workspace) / "agent-transcripts").glob("*/*.jsonl")
            else:
                files = (base / ("-" + _slug(workspace))).glob("*.jsonl")
            found += [(p, workspace) for p in files if p.is_file()]
        if not found:
            return None, None
        return max(found, key=lambda item: item[0].stat().st_mtime)
    # ponytail: newest 200 Codex rollouts only. Raise it if older chats need resuming.
    files = sorted(base.rglob("rollout-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:200]
    for path in files:
        with path.open("rb") as handle:
            try:
                meta = json.loads(handle.readline())
            except json.JSONDecodeError:
                continue
        cwd = (meta.get("payload") or {}).get("cwd")
        if cwd and _related(Path(cwd), repo_root):
            return path, Path(cwd)
    return None, None


def _chat_task(conn, source, path, raw, common_dir):
    project = conn.execute("SELECT id FROM projects WHERE git_common_dir = ?", (str(common_dir),)).fetchone()
    if project is None:
        return None
    native = _native_id(source, path)
    row = conn.execute(
        """SELECT active_task_id FROM sessions
           WHERE project_id = ? AND harness = ? AND (native_id = ? OR transcript_path = ?)
             AND active_task_id IS NOT NULL
           ORDER BY attached_at DESC LIMIT 1""",
        (project["id"], source, native, str(path)),
    ).fetchone()
    if row:
        return row["active_task_id"]
    for session_id in reversed(re.findall(rb"acm_s_[0-9a-f]{12}", raw)):
        row = conn.execute(
            "SELECT active_task_id FROM sessions WHERE id = ? AND project_id = ? AND active_task_id IS NOT NULL",
            (session_id.decode(), project["id"]),
        ).fetchone()
        if row:
            return row["active_task_id"]
    return None


def resume(conn, *, harness, repo_path, source, limit=30, budget=12_000, root=None):
    from agent_cowork_memory.ledger import attach, git_identity

    if source not in READERS:
        raise AcmError("invalid", message="source must be codex, cursor, or claude")
    if source == harness:
        raise AcmError("invalid", message="source must be a different harness from this one")
    repo_root, common_dir, _branch = git_identity(repo_path)
    path, workspace = latest_chat(source, repo_root, root)
    if path is None:
        raise AcmError("not_found", message=f"no {source} chat found for this repo")
    raw = path.read_bytes()
    task = _chat_task(conn, source, path, raw, common_dir)
    records, _end, unknown, _truncated = _parse(source, raw, 0, len(raw))
    kept, used = [], 0
    for rec in reversed(records[-limit:]):
        used += len(rec["text"])
        if kept and used > budget:
            break
        kept.append({"role": rec["role"], "text": rec["text"]})
    kept.reverse()
    native = _native_id(source, path)
    if task:
        joined = attach(conn, repo_path=repo_root, harness=harness, label=f"resume-{source}", task=task)
    else:
        first = next((r["text"] for r in records if r["role"] == "user"), "")
        title = " ".join(first.split())[:80] or f"Continued from {source}"
        joined = attach(conn, repo_path=repo_root, harness=harness, label=f"resume-{source}", title=title)
    result = {
        **joined,
        "from": source,
        "chat": str(path),
        "chat_workspace": str(workspace),
        "native_id": native,
        "messages": kept,
        "omitted_messages": len(records) - len(kept),
    }
    if not records and unknown:
        result["diagnostic"] = "unrecognized records"
    return result


def ack(conn, *, consumer, target, byte_offset):
    source = conn.execute(
        "SELECT * FROM transcript_sources WHERE session_id = ?", (target,)
    ).fetchone()
    if source is None or byte_offset is None:
        return
    conn.execute(
        """INSERT INTO transcript_cursors (source_id, consumer_session_id, generation, byte_offset)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(source_id, consumer_session_id) DO UPDATE SET
             generation = excluded.generation,
             byte_offset = excluded.byte_offset""",
        (source["id"], consumer, source["generation"], int(byte_offset)),
    )


def cursor_for(conn, *, consumer, target):
    row = conn.execute(
        """SELECT c.byte_offset, c.generation FROM transcript_cursors c
           JOIN transcript_sources s ON s.id = c.source_id
           WHERE s.session_id = ? AND c.consumer_session_id = ?""",
        (target, consumer),
    ).fetchone()
    return None if row is None else row["byte_offset"]
