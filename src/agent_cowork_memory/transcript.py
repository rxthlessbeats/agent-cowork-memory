import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from agent_cowork_memory.ledger import AcmError, new_id
from agent_cowork_memory.readers import claude, codex, cursor, opencode

READERS = {"codex": codex, "cursor": cursor, "claude": claude, "opencode": opencode}


def chat_bytes(harness, path):
    read = getattr(READERS[harness], "read", None)
    return read(Path(path)) if read else Path(path).read_bytes()


def chat_exists(harness, path):
    exists = getattr(READERS[harness], "exists", None)
    return exists(Path(path)) if exists else Path(path).exists()
_TOOL_MARKERS = ("tool_use", "function_call", "custom_tool_call")
_MAX_SCAN = 1_000_000
# ponytail: one pass over files touched since attach, cap 8MB each. Index if a repo grows past that.


def default_root(harness):
    return READERS[harness].root()


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
        if not chat_exists(session_row["harness"], existing["path"]):
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
    raw = chat_bytes(session_row["harness"], path)
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
    return READERS[harness].native_id(path)


def _sync_generation(conn, source):
    path = Path(source["path"])
    harness = conn.execute("SELECT harness FROM sessions WHERE id = ?", (source["session_id"],)).fetchone()["harness"]
    if not chat_exists(harness, path):
        return None
    raw = chat_bytes(harness, path)
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


_JOB = re.compile(r"\[acm job (acm_j_[0-9a-f]+)\]")
_QUERY = re.compile(r"<user_query>(.*?)</user_query>", re.S)
_TAG = re.compile(r"</?[A-Za-z_][\w-]*[^>]*>")


def _all_chats(harness, repo_root, root=None):
    """Chats whose workspace is the repo, inside it, or contains it, newest first."""
    base = Path(root) if root else default_root(harness)
    if not base.exists():
        return []
    return sorted(READERS[harness].chats(base, Path(repo_root)), key=lambda item: item[2], reverse=True)


def _opening(harness, raw):
    """The chat's first user message, without Cursor's wrappers, and the acm job id if acm sent it."""
    records = _parse(harness, raw, 0, 200_000)[0]
    first = next((r["text"] for r in records if r["role"] == "user"), "")
    query = _QUERY.search(first)
    text = " ".join(_TAG.sub(" ", query.group(1) if query else first).split())
    job = _JOB.match(text)
    return text, job.group(1) if job else None


def _listing(harnesses, repo_root, roots):
    """(mtime, harness, path, workspace) for every chat of these agents in the repo, newest first,
    with chats opened in a folder above the repo after all the others."""
    found = [
        (mtime, harness, path, workspace)
        for harness in harnesses
        for path, workspace, mtime in _all_chats(harness, repo_root, roots.get(harness))
    ]
    above = Path(repo_root).parents
    return sorted(found, key=lambda item: (Path(item[3]) in above, -item[0]))


def _entry(conn, item, common_dir):
    mtime, harness, path, workspace = item
    raw = chat_bytes(harness, path)
    first, job = _opening(harness, raw)
    task = _chat_task(conn, harness, path, raw, common_dir)
    title = conn.execute("SELECT title FROM tasks WHERE id = ?", (task,)).fetchone() if task else None
    return {
        "agent": harness,
        "chat": _native_id(harness, path),
        "updated": datetime.fromtimestamp(mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "folder": str(workspace),
        "task": title["title"] if title else None,
        "first": first[:160],
        "job": job,
    }


def chats(conn, *, repo_path, limit=20, roots=None):
    from agent_cowork_memory.ledger import git_identity

    repo_root, common_dir, _branch = git_identity(repo_path)
    return {"chats": [_entry(conn, item, common_dir) for item in _listing(READERS, repo_root, roots or {})[:limit]]}


def _chat_task(conn, source, path, raw, common_dir):
    project = conn.execute("SELECT id FROM projects WHERE git_common_dir = ?", (str(common_dir),)).fetchone()
    if project is None:
        return None
    native = _native_id(source, path)
    row = conn.execute(
        """SELECT s.active_task_id FROM sessions s JOIN tasks t ON t.id = s.active_task_id
           WHERE s.project_id = ? AND s.harness = ? AND (s.native_id = ? OR s.transcript_path = ?)
             AND t.archived_at IS NULL
           ORDER BY s.attached_at DESC LIMIT 1""",
        (project["id"], source, native, str(path)),
    ).fetchone()
    if row:
        return row["active_task_id"]
    for session_id in reversed(re.findall(rb"acm_s_[0-9a-f]{12}", raw)):
        row = conn.execute(
            """SELECT s.active_task_id FROM sessions s JOIN tasks t ON t.id = s.active_task_id
               WHERE s.id = ? AND s.project_id = ? AND t.archived_at IS NULL""",
            (session_id.decode(), project["id"]),
        ).fetchone()
        if row:
            return row["active_task_id"]
    return None


def _clip(text, size):
    """Keep the start and end of a message that alone is over the budget."""
    half = size // 2
    return f"{text[:half]}\n[... {len(text) - 2 * half} characters cut ...]\n{text[-half:]}"


_CHOICES = 10


def resume(conn, *, harness, repo_path, source=None, chat=None, limit=30, budget=12_000, root=None, roots=None):
    """Read one chat. Without chat, the user picks: if more than one chat matches, the list comes back as choose."""
    from agent_cowork_memory.ledger import attach, git_identity

    if source is not None and source not in READERS:
        raise AcmError("invalid", message=f"source must be {', '.join(READERS)}")
    roots = dict(roots or {})
    if root and source:
        roots[source] = root
    repo_root, common_dir, _branch = git_identity(repo_path)
    listed = _listing([source] if source else list(READERS), repo_root, roots)
    if chat:
        hit = next((item for item in listed if _native_id(item[1], item[2]) == chat), None)
        if hit is None:
            raise AcmError("not_found", message=f"no chat {chat} in this repo; call resume without chat to list them")
    elif len(listed) == 1:
        hit = listed[0]
    elif listed:
        return {
            "choose": [_entry(conn, item, common_dir) for item in listed[:_CHOICES]],
            "more": max(0, len(listed) - _CHOICES),
            "next": "Show the user these chats (agent, updated, folder, task, first message, and whether acm "
                    "started it as a job) and ask which one to continue. Then call resume with that chat id. "
                    "Do not pick one yourself. If more is above 0, chats lists older ones.",
        }
    else:
        raise AcmError("not_found", message=f"no {source or 'agent'} chat found for this repo")
    _mtime, source, path, workspace = hit
    raw = chat_bytes(source, path)
    task = _chat_task(conn, source, path, raw, common_dir)
    records, _end, unknown, _truncated = _parse(source, raw, 0, len(raw))
    kept, used, clipped = [], 0, 0
    for rec in reversed(records[-limit:]):
        text = rec["text"]
        if len(text) > budget:
            text, clipped = _clip(text, budget), clipped + 1
        used += len(text)
        if kept and used > budget:
            break
        kept.append({"role": rec["role"], "text": text})
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
        "clipped_messages": clipped,
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
