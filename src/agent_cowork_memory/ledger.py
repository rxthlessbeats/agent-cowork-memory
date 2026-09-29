import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HARNESSES = ("codex", "cursor", "claude")


class AcmError(Exception):
    def __init__(self, code, **payload):
        self.code = code
        self.payload = payload
        super().__init__(code)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_id(prefix):
    return prefix + secrets.token_hex(6)


def git_identity(repo_path):
    path = Path(repo_path).expanduser()
    if not path.exists():
        raise AcmError("invalid", message="repo_path does not exist")
    top = _git(path, "rev-parse", "--show-toplevel")
    if top is None:
        root = path.resolve()
        return root, root, None
    root = Path(top).resolve()
    common = _git(root, "rev-parse", "--git-common-dir")
    common_dir = Path(common)
    if not common_dir.is_absolute():
        common_dir = (root / common_dir).resolve()
    else:
        common_dir = common_dir.resolve()
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    return root, common_dir, branch


def _git(cwd, *args):
    proc = subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _project(conn, common_dir):
    row = conn.execute(
        "SELECT * FROM projects WHERE git_common_dir = ?", (str(common_dir),)
    ).fetchone()
    if row:
        return row
    project_id = new_id("acm_p_")
    conn.execute(
        "INSERT INTO projects (id, git_common_dir, created_at) VALUES (?, ?, ?)",
        (project_id, str(common_dir), now()),
    )
    return conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()


def _session_row(conn, session_id):
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        raise AcmError("invalid", message="unknown session", hint="attach", session=session_id)
    return row


def _task_row(conn, task_id):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise AcmError("invalid", message="unknown task")
    return row


def _public_task(row, session_id):
    return {
        "session": session_id,
        "task": row["id"],
        "project": row["project_id"],
        "title": row["title"],
        "goal": row["goal"],
        "status": row["status"],
        "owner": row["owner_session_id"],
        "summary": row["summary"],
        "next_action": row["next_action"],
        "blockers": row["blockers"],
        "version": row["version"],
    }


def attach(conn, *, repo_path, harness, label, task=None, title=None, goal=None, native_id=None):
    if harness not in HARNESSES:
        raise AcmError("invalid", message="harness must be codex, cursor, or claude")
    if bool(task) == bool(title):
        raise AcmError("invalid", message="pass a task to join or a title to create, not both")
    root, common_dir, _branch = git_identity(repo_path)
    conn.execute("BEGIN IMMEDIATE")
    try:
        project = _project(conn, common_dir)
        if native_id:
            taken = conn.execute(
                "SELECT id FROM sessions WHERE project_id = ? AND harness = ? AND native_id = ?",
                (project["id"], harness, native_id),
            ).fetchone()
            if taken:
                raise AcmError("invalid", message="native_id already attached", session=taken["id"])
        if task:
            row = _task_row(conn, task)
            if row["project_id"] != project["id"]:
                raise AcmError("invalid", message="task is in another project")
        else:
            task_id = new_id("acm_t_")
            stamp = now()
            conn.execute(
                """INSERT INTO tasks (
                    id, project_id, title, goal, status, owner_session_id,
                    summary, next_action, blockers, version, updated_at
                ) VALUES (?, ?, ?, ?, 'open', NULL, NULL, NULL, NULL, 1, ?)""",
                (task_id, project["id"], title, goal, stamp),
            )
            task = task_id
        session_id = new_id("acm_s_")
        stamp = now()
        conn.execute(
            """INSERT INTO sessions (
                id, project_id, harness, native_id, label, working_directory,
                active_task_id, attached_at, last_seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, project["id"], harness, native_id, label, str(root), task, stamp, stamp),
        )
        conn.execute(
            "INSERT INTO task_sessions (task_id, session_id) VALUES (?, ?)",
            (task, session_id),
        )
        if title:
            conn.execute(
                "UPDATE tasks SET owner_session_id = ? WHERE id = ?",
                (session_id, task),
            )
            conn.execute(
                """INSERT INTO checkpoints (
                    task_id, version, session_id, status, owner_session_id, created_at
                ) VALUES (?, 1, ?, 'open', ?, ?)""",
                (task, session_id, session_id, stamp),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return _public_task(_task_row(conn, task), session_id)


def _linked(conn, task_id, session_id):
    row = conn.execute(
        "SELECT 1 FROM task_sessions WHERE task_id = ? AND session_id = ?",
        (task_id, session_id),
    ).fetchone()
    if row is None:
        raise AcmError("invalid", message="session is not on this task", session=session_id)


def _bump(conn, task, session_id, *, status, summary, next_action, blockers, owner, expect_version):
    if task["version"] != expect_version:
        body = _public_task(task, session_id)
        body.pop("session", None)
        raise AcmError("conflict", session=session_id, **body)
    if task["archived_at"]:
        raise AcmError("invalid", message="task is archived", session=session_id)
    version = task["version"] + 1
    stamp = now()
    archived = stamp if status == "done" else None
    conn.execute(
        """UPDATE tasks SET status = ?, owner_session_id = ?, summary = ?,
           next_action = ?, blockers = ?, version = ?, updated_at = ?, archived_at = ?
           WHERE id = ?""",
        (status, owner, summary, next_action, blockers, version, stamp, archived, task["id"]),
    )
    conn.execute(
        """INSERT INTO checkpoints (
            task_id, version, session_id, status, summary, next_action, blockers,
            owner_session_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (task["id"], version, session_id, status, summary, next_action, blockers, owner, stamp),
    )


def claim(conn, *, session, task, expect_version):
    _session_row(conn, session)
    conn.execute("BEGIN IMMEDIATE")
    try:
        row = _task_row(conn, task)
        _linked(conn, task, session)
        _bump(
            conn, row, session,
            status=row["status"],
            summary=row["summary"],
            next_action=row["next_action"],
            blockers=row["blockers"],
            owner=session,
            expect_version=expect_version,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return _public_task(_task_row(conn, task), session)


def checkpoint(conn, *, session, task, expect_version, summary, next_action=None, blockers=None, status=None, ack_target=None, ack_cursor=None):
    _session_row(conn, session)
    conn.execute("BEGIN IMMEDIATE")
    try:
        row = _task_row(conn, task)
        _linked(conn, task, session)
        if row["owner_session_id"] != session:
            raise AcmError(
                "not_owner", hint="claim", session=session, **{
                    k: v for k, v in _public_task(row, session).items() if k != "session"
                },
            )
        _bump(
            conn, row, session,
            status=status or row["status"],
            summary=summary,
            next_action=next_action if next_action is not None else row["next_action"],
            blockers=blockers if blockers is not None else row["blockers"],
            owner=row["owner_session_id"],
            expect_version=expect_version,
        )
        if ack_target is not None and ack_cursor is not None:
            from agent_cowork_memory.transcript import ack
            ack(conn, consumer=session, target=ack_target, byte_offset=ack_cursor)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return _public_task(_task_row(conn, task), session)


def context(conn, *, session):
    row = _session_row(conn, session)
    if not row["active_task_id"]:
        raise AcmError("invalid", message="session has no task", hint="attach", session=session)
    conn.execute(
        "UPDATE sessions SET last_seen_at = ? WHERE id = ?", (now(), session)
    )
    conn.commit()
    from agent_cowork_memory.memory import fit_notes, visible_notes
    task = _task_row(conn, row["active_task_id"])
    short, long = visible_notes(conn, task["project_id"], task["id"])
    return fit_notes(_public_task(task, session), short, long)


def task_list(conn, *, repo_path):
    _root, common_dir, _branch = git_identity(repo_path)
    project = conn.execute(
        "SELECT * FROM projects WHERE git_common_dir = ?", (str(common_dir),)
    ).fetchone()
    if project is None:
        return {"session": None, "tasks": []}
    rows = conn.execute(
        "SELECT * FROM tasks WHERE project_id = ? ORDER BY updated_at",
        (project["id"],),
    ).fetchall()
    return {"session": None, "tasks": [_public_task(r, None) for r in rows]}


def task_history(conn, *, task):
    row = _task_row(conn, task)
    rows = conn.execute(
        "SELECT version, session_id, status, summary, next_action, blockers, owner_session_id, created_at FROM checkpoints WHERE task_id = ? ORDER BY version",
        (task,),
    ).fetchall()
    return {
        "session": None,
        "task": row["id"],
        "version": row["version"],
        "history": [dict(r) for r in rows],
    }


def session_list(conn, *, repo_path):
    _root, common_dir, _branch = git_identity(repo_path)
    project = conn.execute(
        "SELECT * FROM projects WHERE git_common_dir = ?", (str(common_dir),)
    ).fetchone()
    if project is None:
        return {"session": None, "sessions": []}
    rows = conn.execute(
        """SELECT id, harness, label, active_task_id, attached_at
           FROM sessions WHERE project_id = ? ORDER BY attached_at""",
        (project["id"],),
    ).fetchall()
    return {"session": None, "sessions": [dict(r) for r in rows]}
