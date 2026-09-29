import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent_cowork_memory.ledger import AcmError, new_id, now

_BUDGET = 12_000
_VISIBLE = """forgotten_at IS NULL AND superseded_at IS NULL AND promoted_at IS NULL
    AND (expires_at IS NULL OR expires_at > ?)"""


def short_note_days(conn):
    row = conn.execute("PRAGMA database_list").fetchone()
    path = Path(row["file"]).parent / "config.toml"
    if not path.exists():
        return 7
    match = re.search(r"(?m)^short_note_days\s*=\s*(\d+)\s*$", path.read_text())
    return int(match.group(1)) if match else 7


def _session(conn, session_id):
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        raise AcmError("invalid", message="unknown session", hint="attach", session=session_id)
    return row


def _note(conn, note_id, project_id):
    row = conn.execute("SELECT * FROM memories WHERE id = ? AND project_id = ?", (note_id, project_id)).fetchone()
    if row is None:
        raise AcmError("invalid", message="unknown note", session=None)
    return row


def _index(conn, note_id, body):
    conn.execute("DELETE FROM memories_fts WHERE memory_id = ?", (note_id,))
    conn.execute("INSERT INTO memories_fts (memory_id, body) VALUES (?, ?)", (note_id, body))


def _drop_index(conn, note_id):
    conn.execute("DELETE FROM memories_fts WHERE memory_id = ?", (note_id,))


def _public(row):
    return {
        "id": row["id"],
        "tier": row["tier"],
        "kind": row["kind"],
        "body": row["body"],
        "source": row["source"],
        "expires_at": row["expires_at"],
        "task": row["task_id"],
    }


def note_add(conn, *, session, text, tier="short", kind=None, days=None, supersedes=None, source=None, task=None, ack_target=None, ack_cursor=None):
    if tier not in ("short", "long"):
        raise AcmError("invalid", message="tier must be short or long", session=session)
    owner = _session(conn, session)
    if not text:
        raise AcmError("invalid", message="text is required", session=session)
    task_id = task or owner["active_task_id"]
    expires = None
    if tier == "short":
        span = short_note_days(conn) if days is None else days
        expires = (datetime.now(timezone.utc) + timedelta(days=span)).strftime("%Y-%m-%dT%H:%M:%SZ")
        kind = kind or "observation"
    note_id = new_id("acm_n_")
    conn.execute("BEGIN IMMEDIATE")
    try:
        if supersedes:
            old = _note(conn, supersedes, owner["project_id"])
            conn.execute("UPDATE memories SET superseded_at = ? WHERE id = ?", (now(), old["id"]))
            _drop_index(conn, old["id"])
        conn.execute(
            """INSERT INTO memories (
                id, project_id, task_id, author_session_id, tier, kind, body, source,
                supersedes_id, expires_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (note_id, owner["project_id"], task_id, session, tier, kind, text, source, supersedes, expires, now()),
        )
        _index(conn, note_id, text)
        if ack_target is not None and ack_cursor is not None:
            from agent_cowork_memory.transcript import ack
            ack(conn, consumer=session, target=ack_target, byte_offset=ack_cursor)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    row = conn.execute("SELECT * FROM memories WHERE id = ?", (note_id,)).fetchone()
    return {"session": session, **_public(row)}


def note_search(conn, *, session, query, task=None):
    owner = _session(conn, session)
    words = re.findall(r"\w+", query or "")
    if not words:
        raise AcmError("invalid", message="empty search", session=session)
    match = " AND ".join(words)
    sql = f"""SELECT m.* FROM memories_fts f
              JOIN memories m ON m.id = f.memory_id
              WHERE memories_fts MATCH ? AND m.project_id = ? AND {_VISIBLE}"""
    args = [match, owner["project_id"], now()]
    if task:
        sql += " AND m.task_id = ?"
        args.append(task)
    rows = conn.execute(sql, args).fetchall()
    return {"session": session, "notes": [_public(row) for row in rows]}


def note_promote(conn, *, session, note, text, reason):
    owner = _session(conn, session)
    conn.execute("BEGIN IMMEDIATE")
    try:
        old = _note(conn, note, owner["project_id"])
        if old["tier"] != "short":
            raise AcmError("invalid", message="only a short note can be promoted", session=session)
        note_id = new_id("acm_n_")
        conn.execute("UPDATE memories SET promoted_at = ? WHERE id = ?", (now(), old["id"]))
        _drop_index(conn, old["id"])
        conn.execute(
            """INSERT INTO memories (
                id, project_id, task_id, author_session_id, tier, body, source, reason, created_at
            ) VALUES (?, ?, ?, ?, 'long', ?, ?, ?, ?)""",
            (note_id, owner["project_id"], old["task_id"], session, text, old["id"], reason, now()),
        )
        _index(conn, note_id, text)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    row = conn.execute("SELECT * FROM memories WHERE id = ?", (note_id,)).fetchone()
    return {"session": session, **_public(row)}


def note_forget(conn, *, session, note):
    owner = _session(conn, session)
    conn.execute("BEGIN IMMEDIATE")
    try:
        row = _note(conn, note, owner["project_id"])
        conn.execute("UPDATE memories SET forgotten_at = ? WHERE id = ?", (now(), row["id"]))
        _drop_index(conn, row["id"])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return {"session": session, "id": note, "forgotten": True}


def visible_notes(conn, project_id, task_id):
    rows = conn.execute(
        f"""SELECT * FROM memories
            WHERE project_id = ? AND {_VISIBLE}
              AND (task_id = ? OR task_id IS NULL)
            ORDER BY created_at""",
        (project_id, now(), task_id),
    ).fetchall()
    short = [_public(row) for row in rows if row["tier"] == "short"]
    long = [_public(row) for row in rows if row["tier"] == "long"]
    return short, long


def fit_notes(checkpoint, short, long):
    body = dict(checkpoint)
    body["short_notes"] = []
    body["long_notes"] = []
    body["omitted"] = {"short": 0, "long": 0}
    used = len(json.dumps(body))
    for key, rows in (("short_notes", short), ("long_notes", long)):
        kept = []
        for note in rows:
            extra = len(json.dumps(note)) + 1
            if used + extra > _BUDGET:
                break
            kept.append(note)
            used += extra
        body[key] = kept
        omitted_key = "short" if key.startswith("short") else "long"
        body["omitted"][omitted_key] = len(rows) - len(kept)
    return body
