import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath

from agent_cowork_memory.ledger import AcmError, _session_row as _session, new_id, now

_BUDGET = 12_000
_KEEP_RESULTS = 20  # ponytail: one log cap, raise it if a project outgrows the job history
_HOLD_HOURS = 2  # ponytail: a hold lapses once its session has not called acm for this long, unless its job is open
_VISIBLE = """forgotten_at IS NULL AND superseded_at IS NULL AND promoted_at IS NULL
    AND (expires_at IS NULL OR expires_at > ?)"""
OPEN = ("starting", "running", "blocked")
OPEN_SQL = ", ".join(f"'{state}'" for state in OPEN)


def one_line(text, width=200):
    flat = " ".join((text or "").split())
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def short_note_days(conn):
    row = conn.execute("PRAGMA database_list").fetchone()
    path = Path(row["file"]).parent / "config.toml"
    if not path.exists():
        return 7
    match = re.search(r"(?m)^short_note_days\s*=\s*(\d+)\s*$", path.read_text())
    return int(match.group(1)) if match else 7


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
    sweep(conn, owner["project_id"])
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
    sweep(conn, owner["project_id"])
    words = re.findall(r"\w+", query or "")
    if not words:
        raise AcmError("invalid", message="empty search", session=session)
    match = " AND ".join(f'"{word}"*' for word in words)  # a prefix, so rain finds rains
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


def _rel(path):
    text = (path or "").replace("\\", "/").strip()
    if not text or text.startswith("/") or ".." in Path(text).parts:
        raise AcmError("invalid", message="hold paths must be relative to the project, such as src/app.py")
    return PurePosixPath(text).as_posix()


def sweep(conn, project_id):
    """Delete notes nobody can see, job results past the cap, and holds of sessions gone quiet."""
    quiet = (datetime.now(timezone.utc) - timedelta(hours=_HOLD_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute(
        f"""DELETE FROM holds WHERE project_id = ? AND session_id IN (
              SELECT s.id FROM sessions s WHERE s.last_seen_at < ? AND NOT EXISTS (
                SELECT 1 FROM delegations d WHERE d.agent_name = s.label AND d.folder = s.working_directory
                  AND d.state IN ({OPEN_SQL})))""",
        (project_id, quiet),
    )
    dead = [row["id"] for row in conn.execute(
        """SELECT id FROM memories WHERE project_id = ? AND (
             (expires_at IS NOT NULL AND expires_at <= ?)
             OR forgotten_at IS NOT NULL OR superseded_at IS NOT NULL OR promoted_at IS NOT NULL)""",
        (project_id, now()),
    )]
    extra = [row["id"] for row in conn.execute(
        f"""SELECT id FROM memories WHERE project_id = ? AND kind = 'result' AND {_VISIBLE}
            ORDER BY created_at DESC, rowid DESC LIMIT -1 OFFSET ?""",
        (project_id, now(), _KEEP_RESULTS),
    )]
    ids = dead + extra
    if ids:
        marks = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM memories_fts WHERE memory_id IN ({marks})", ids)
        conn.execute(f"DELETE FROM memories WHERE id IN ({marks})", ids)
    conn.commit()


def release(conn, folder, label):
    conn.execute(
        """DELETE FROM holds WHERE session_id IN (
            SELECT id FROM sessions WHERE working_directory = ? AND label = ?)""",
        (folder, label),
    )
    conn.commit()


def claim(conn, session_row, paths):
    """Replace this session's file holds. Returns paths held by someone else, changing nothing then."""
    paths = list(dict.fromkeys(_rel(path) for path in paths))
    project, session = session_row["project_id"], session_row["id"]
    conn.execute("BEGIN IMMEDIATE")
    try:
        taken = {row["path"] for row in conn.execute(
            "SELECT path FROM holds WHERE project_id = ? AND session_id != ?", (project, session),
        )}
        busy = [path for path in paths if path in taken]
        if not busy:
            conn.execute("DELETE FROM holds WHERE session_id = ?", (session,))
            conn.executemany(
                "INSERT INTO holds (project_id, path, session_id, created_at) VALUES (?, ?, ?, ?)",
                [(project, path, session, now()) for path in paths],
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return busy


def activity(conn, session_row):
    """Who is working in this folder, and which files are held. This session is left out of working."""
    working = [
        {"agent": row["agent_name"], "state": row["state"], "task": one_line(row["task"])}
        for row in conn.execute(
            f"""SELECT agent_name, task, state FROM delegations
                WHERE folder = ? AND state IN ({OPEN_SQL}) ORDER BY started_at, rowid""",
            (session_row["working_directory"],),
        )
        if row["agent_name"] != session_row["label"]
    ]
    held = [
        {"path": row["path"], "agent": row["label"] or row["harness"]}
        for row in conn.execute(
            """SELECT h.path, s.label, s.harness FROM holds h
               JOIN sessions s ON s.id = h.session_id
               WHERE h.project_id = ? ORDER BY h.path""",
            (session_row["project_id"],),
        )
    ]
    return working, held


def visible_notes(conn, project_id, task_id):
    """Every live note in the project: this task's first, then the rest, newest first in each."""
    rows = conn.execute(
        f"""SELECT * FROM memories
            WHERE project_id = ? AND {_VISIBLE}
            ORDER BY task_id IS NOT ?, created_at DESC, rowid DESC""",
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
    # Long notes first: decisions and conventions matter more than progress, and results pile up as short notes.
    for key, rows in (("long_notes", long), ("short_notes", short)):
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
