"""Start other agents, send each a brief, and wait for them: in herdr panes if herdr is installed, else in the background."""
import json
import os
import re
import shutil
import subprocess
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from agent_cowork_memory.ledger import AcmError, attach, git_identity, new_id, now
from agent_cowork_memory.memory import OPEN_SQL, note_add, one_line, release
from agent_cowork_memory.transcript import READERS, _parse, chat_bytes, chat_exists

SESSION = "acm"
FLAGS = {
    "codex": ["--approve-for-me"],
    "claude": ["--permission-mode", "auto"],
    "cursor": ["--auto-review", "--trust", "--approve-mcps"],
    "opencode": ["--auto"],
}
WAIT_SECONDS = 45
POLL_SECONDS = 2
RESEND_AFTER = 10
JOB_FILE_DAYS = 7  # ponytail: output files of finished jobs are kept this long, for debugging
WATCH = f"herdr session attach {SESSION}"
BACKGROUND = "background"


def _headless(kind, prompt, folder, answer):
    return {
        "codex": ["codex", "exec", *FLAGS["codex"], "--skip-git-repo-check", "--cd", str(folder), "-o", str(answer), prompt],
        "claude": ["claude", "-p", *FLAGS["claude"], prompt],
        "cursor": ["cursor-agent", "-p", *FLAGS["cursor"], prompt],
        "opencode": ["opencode", "run", "--auto", "--dir", str(folder), prompt],
    }[kind]


def spawn_background(cmd, folder, out, log, exit_file):
    subprocess.Popen(
        ["sh", "-c", '"$@" > "$ACM_OUT" 2> "$ACM_LOG" < /dev/null; echo $? > "$ACM_EXIT.tmp"; mv "$ACM_EXIT.tmp" "$ACM_EXIT"', "sh", *cmd],
        cwd=folder, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={**os.environ, "ACM_DELEGATED": "1", "ACM_OUT": str(out), "ACM_LOG": str(log), "ACM_EXIT": str(exit_file)},
        start_new_session=True,
    )


class HerdrError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def run_herdr(*args, raw=False):
    try:
        proc = subprocess.run(["herdr", "--session", SESSION, *args], capture_output=True, text=True)
    except FileNotFoundError:
        raise AcmError("unavailable", message="herdr is not installed; see https://herdr.dev") from None
    if raw and proc.returncode == 0:
        return proc.stdout
    out = (proc.stdout.strip() or proc.stderr.strip()).splitlines()
    try:
        data = json.loads(out[-1]) if out else {}
    except json.JSONDecodeError:
        raise AcmError("unavailable", message=f"herdr: {out[-1][:200]}") from None
    if "error" in data:
        raise HerdrError(data["error"].get("code"), data["error"].get("message"))
    return data.get("result", {})


def start_server():
    subprocess.Popen(
        ["herdr", "--session", SESSION, "server"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def is_delegated():
    if os.environ.get("ACM_DELEGATED") == "1":
        return True
    pid = os.getppid()
    while pid > 1:
        try:
            if b"ACM_DELEGATED=1" in Path(f"/proc/{pid}/environ").read_bytes().split(b"\0"):
                return True
        except OSError:
            pass
        try:
            pid = int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            return False
    return False


@dataclass
class Deps:
    herdr: Callable = run_herdr
    start_server: Callable = start_server
    use_herdr: Callable = lambda: shutil.which("herdr") is not None
    spawn: Callable = spawn_background
    installed: Callable = shutil.which
    delegated: Callable = is_delegated
    sleep: Callable = time.sleep
    clock: Callable = time.monotonic
    roots: dict = field(default_factory=dict)

    def root(self, kind):
        return Path(self.roots[kind]) if kind in self.roots else READERS[kind].root()


def _ensure_server(deps):
    try:
        deps.herdr("workspace", "list")
        return
    except HerdrError as exc:
        if exc.code != "server_not_running":
            raise AcmError("unavailable", message=f"herdr: {exc}") from None
    deps.start_server()
    for _ in range(50):
        deps.sleep(0.1)
        try:
            deps.herdr("workspace", "list")
            return
        except HerdrError:
            continue
    raise AcmError("unavailable", message=f"could not start herdr; run: {WATCH}")


def _workspace(deps, folder):
    """(workspace id, its fresh empty root pane or None)."""
    for pane in deps.herdr("pane", "list").get("panes", []):
        if pane.get("cwd") == str(folder):
            return pane["workspace_id"], None
    made = deps.herdr(
        "workspace", "create", "--cwd", str(folder), "--label", folder.name,
        "--env", "ACM_DELEGATED=1", "--no-focus",
    )
    return made["workspace"]["workspace_id"], made["root_pane"]["pane_id"]


def _new_pane(deps, workspace, folder):
    """A pane for a new agent. A tab holds two panes side by side, so agents stay wide enough to draw."""
    panes = [p for p in deps.herdr("pane", "list").get("panes", []) if p.get("workspace_id") == workspace]
    per_tab = Counter(p.get("tab_id") for p in panes)
    lone = next((p for p in panes if per_tab[p.get("tab_id")] == 1), None)
    where = ["--cwd", str(folder), "--env", "ACM_DELEGATED=1", "--no-focus"]
    if lone:
        return deps.herdr("pane", "split", lone["pane_id"], "--direction", "right", *where)["pane"]["pane_id"]
    return deps.herdr("tab", "create", "--workspace", workspace, "--label", folder.name, *where)["root_pane"]["pane_id"]


def agent_name(kind, folder):
    slug = re.sub(r"[^a-z0-9]+", "-", folder.name.lower()).strip("-") or "folder"
    return f"{kind}-{slug}"[:32].rstrip("-")


def _agents(deps):
    if not deps.use_herdr():
        return {}
    return {a["name"]: a for a in deps.herdr("agent", "list").get("agents", []) if a.get("name")}


def _jobs_dir(conn):
    return Path(conn.execute("PRAGMA database_list").fetchone()["file"]).parent / "jobs"


def _clean_jobs(conn):
    folder = _jobs_dir(conn)
    if not folder.is_dir():
        return
    running = {row["id"] for row in conn.execute(f"SELECT id FROM delegations WHERE state IN ({OPEN_SQL})")}
    cutoff = time.time() - JOB_FILE_DAYS * 86400
    for path in folder.iterdir():
        if path.stem not in running and path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)


def _job_files(conn, job):
    base = _jobs_dir(conn) / job
    return base.with_suffix(".out"), base.with_suffix(".log"), base.with_suffix(".exit"), base.with_suffix(".answer")


def _start_background(conn, deps, kind, job, prompt, folder):
    binary = "cursor-agent" if kind == "cursor" else kind
    if not deps.installed(binary):
        raise AcmError("unavailable", message=f"{binary} is not installed or not on PATH")
    out, log, exit_file, answer = _job_files(conn, job)
    out.parent.mkdir(parents=True, exist_ok=True)
    deps.spawn(_headless(kind, prompt, folder, answer), folder, out, log, exit_file)


def _check_background(conn, row):
    out, log, exit_file, answer = _job_files(conn, row["id"])
    try:
        code = int(exit_file.read_text().strip())
    except (OSError, ValueError):
        return "running", None
    text = answer if row["kind"] == "codex" and answer.exists() else out
    reply = text.read_text(errors="replace").strip() if text.exists() else ""
    if code == 0:
        return "done", reply
    tail = log.read_text(errors="replace").strip()[-800:] if log.exists() else ""
    return "gone", f"The agent exited with code {code}. Last lines: " + (tail or reply[-800:] or "(none)")


def _pane_tail(deps, pane, lines=12):
    try:
        text = deps.herdr("pane", "read", pane, "--source", "recent-unwrapped", "--lines", str(lines), raw=True)
    except (HerdrError, AcmError):
        return ""
    return "\n".join(line for line in text.splitlines() if line.strip())[-800:]


def build_prompt(*, job, harness, session, folder, summary, task, done_when=None, context=None, others=(), problem=True):
    parts = [f"[acm job {job}] A {harness} chat asked for this in {folder}. Your acm session is {session}."]
    if problem:
        parts.append(f"## Problem\n{summary.strip()}")
    parts.append(f"## Your task\n{task.strip()}")
    parts.append(f"## Done when\n{(done_when or 'You decide; say what you checked.').strip()}")
    if context:
        parts.append(f"## Context\n{context.strip()}")
    if others:
        lines = "\n".join(f"- {name}: {one_line(text.splitlines()[0], 120)}" for name, text in others)
        parts.append(f"## Others working in this folder right now\n{lines}\nDon't edit files another agent is working on.")
    parts.append(
        "## Before you edit\nCall acm context with your session and hold set to every file you will "
        "create or edit, relative to this folder. If a path comes back busy, leave it alone. "
        "Call context again before you edit a file you have not held."
    )
    parts.append(
        "## When you finish\nReply with a one-paragraph summary of what you did and what you checked; "
        "acm saves it for the other agents. Don't delegate this job to other agents."
    )
    return "\n\n".join(parts)


def _caller(conn, harness, root, summary, session):
    if session:
        row = conn.execute("SELECT id FROM sessions WHERE id = ?", (session,)).fetchone()
        if row is None:
            raise AcmError("invalid", message="unknown session", hint="omit session to attach", session=session)
        return session
    last = conn.execute(
        """SELECT t.id FROM delegations d
           JOIN sessions s ON s.id = d.caller_session_id
           JOIN tasks t ON t.id = s.active_task_id
           WHERE d.folder = ? AND t.status = 'open' AND t.archived_at IS NULL
           ORDER BY d.started_at DESC, d.rowid DESC LIMIT 1""",
        (str(root),),
    ).fetchone()
    joined = {"task": last["id"]} if last else {"title": one_line(summary, 80)}
    return attach(conn, repo_path=root, harness=harness, label="delegate", **joined)["session"]


def _worker_session(conn, row):
    """The acm session that speaks for a delegated agent, on its caller's task."""
    task = conn.execute(
        "SELECT active_task_id FROM sessions WHERE id = ?", (row["caller_session_id"],),
    ).fetchone()["active_task_id"]
    found = conn.execute(
        "SELECT id FROM sessions WHERE label = ? AND harness = ? AND working_directory = ?",
        (row["agent_name"], row["kind"], row["folder"]),
    ).fetchone()
    if found is None:
        return attach(conn, repo_path=row["folder"], harness=row["kind"], label=row["agent_name"], task=task)["session"]
    conn.execute("INSERT OR IGNORE INTO task_sessions (task_id, session_id) VALUES (?, ?)", (task, found["id"]))
    conn.execute("UPDATE sessions SET active_task_id = ?, last_seen_at = ? WHERE id = ?", (task, now(), found["id"]))
    conn.commit()
    return found["id"]


def _save_result(conn, row, answer):
    author = _worker_session(conn, row)
    text = f"{row['agent_name']} did: {one_line(row['task'], 300)}\nResult: {answer.strip() or '(no summary)'}"
    note_add(conn, session=author, text=text, kind="result", source=row["id"])


def _on_acm_job(conn, deps, harness, root):
    """True while this delegated agent is still working on a job acm sent it."""
    if deps.use_herdr():
        _ensure_server(deps)
    query = f"SELECT * FROM delegations WHERE agent_name = ? AND folder = ? AND state IN ({OPEN_SQL})"
    args = (agent_name(harness, root), str(root))
    _refresh(conn, deps, conn.execute(query, args).fetchall(), _agents(deps))
    return conn.execute(query, args).fetchone() is not None


def delegate(conn, *, harness, repo_path, summary, tasks, session=None, deps=None):
    deps = deps or Deps()
    started = deps.clock()
    if not (summary or "").strip():
        raise AcmError("invalid", message="summary is required: the problem, for someone who has not seen this chat")
    if not tasks:
        raise AcmError("invalid", message="tasks must list at least one {to, task}")
    for item in tasks:
        if item.get("to") not in FLAGS:
            raise AcmError("invalid", message=f"to must be one of {', '.join(FLAGS)}")
        if not (item.get("task") or "").strip():
            raise AcmError("invalid", message="every task needs task text")
    root, _common, _branch = git_identity(repo_path)
    if root in (Path.home().resolve(), Path("/")):
        raise AcmError("invalid", message="refusing to delegate in the home folder or /; pass a project folder")
    _clean_jobs(conn)
    if deps.delegated() and _on_acm_job(conn, deps, harness, root):
        raise AcmError(
            "not_allowed", message="this agent is working on a job acm sent it and cannot delegate until that job is done",
        )
    session = _caller(conn, harness, root, summary, session)

    herdr = deps.use_herdr()
    if herdr:
        _ensure_server(deps)
        workspace, fresh = _workspace(deps, root)
    agents = _agents(deps)
    query = f"SELECT * FROM delegations WHERE folder = ? AND state IN ({OPEN_SQL})"
    _refresh(conn, deps, conn.execute(query, (str(root),)).fetchall(), agents)
    running = {r["agent_name"]: r["task"] for r in conn.execute(query, (str(root),))}
    others = list(running.items())
    plan, busy = [], []
    for item in tasks:
        kind = item["to"]
        name = agent_name(kind, root)
        agent = agents.get(name)
        if agent and agent.get("workspace_id") != workspace:
            raise AcmError("invalid", message=f"herdr agent {name} belongs to another folder; close it or rename this folder")
        working = agent is not None and agent.get("agent_status") not in ("idle", "done")
        if name in running or working or any(n == name for _i, n, _r, _p in plan):
            doing = running.get(name) or next((i["task"] for i, n, _r, _p in plan if n == name), None)
            busy.append({
                "to": kind, "agent": name, "state": "busy",
                "result": f"{name} is still working" + (f" on: {one_line(doing, 120)}" if doing else "") + ". Try again when it finishes.",
            })
            continue
        last = conn.execute(
            "SELECT summary FROM delegations WHERE agent_name = ? AND folder = ? ORDER BY started_at DESC, rowid DESC LIMIT 1",
            (name, str(root)),
        ).fetchone()
        reuse = agent is not None
        plan.append((item, name, reuse, not (reuse and last and last["summary"] == summary)))
    for item, name, _reuse, _problem in plan:
        others.append((name, item["task"]))

    for item, name, reuse, problem in plan:
        kind, job = item["to"], new_id("acm_j_")
        mates = [(n, t) for n, t in others if n != name]
        worker = _worker_session(conn, {
            "caller_session_id": session, "agent_name": name, "kind": kind, "folder": str(root),
        })
        prompt = build_prompt(
            job=job, harness=harness, session=worker, folder=root, summary=summary, task=item["task"],
            done_when=item.get("done_when"), context=item.get("context"), others=mates, problem=problem,
        )
        state, pane = "running", agents.get(name, {}).get("pane_id")
        if not herdr:
            _start_background(conn, deps, kind, job, prompt, root)
            pane = BACKGROUND
        elif not reuse:
            pane, fresh = fresh or _new_pane(deps, workspace, root), None
            agents[name] = {"name": name, "pane_id": pane}
            try:
                budget = max(1000, int((started + WAIT_SECONDS - deps.clock()) * 1000))
                deps.herdr("agent", "start", name, "--kind", kind, "--pane", pane, "--timeout", str(budget), "--", *FLAGS[kind])
            except HerdrError as exc:
                if exc.code != "agent_not_ready":
                    raise AcmError("unavailable", message=f"herdr could not start {kind}: {exc}") from None
                state = "starting"
        if herdr and state == "running":
            state = _send(deps, name, prompt)
        conn.execute(
            """INSERT INTO delegations (id, caller_session_id, folder, kind, agent_name, pane_id, summary, task, prompt, state, started_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (job, session, str(root), kind, name, pane, summary, item["task"], prompt, state, now()),
        )
        conn.commit()
    result = _wait(conn, deps, session, started)
    result["jobs"] = busy + result["jobs"]
    return result


def _send(deps, name, prompt):
    try:
        deps.herdr("agent", "prompt", name, prompt)
    except HerdrError as exc:
        if exc.code == "agent_blocked":
            return "starting"
        raise AcmError("unavailable", message=f"herdr could not prompt {name}: {exc}") from None
    return "running"


def delegate_wait(conn, *, session, deps=None):
    deps = deps or Deps()
    if conn.execute("SELECT 1 FROM sessions WHERE id = ?", (session,)).fetchone() is None:
        raise AcmError("invalid", message="unknown session", session=session)
    return _wait(conn, deps, session, deps.clock())


def _transcript(deps, row, agent):
    if row["transcript_path"] and chat_exists(row["kind"], row["transcript_path"]):
        return Path(row["transcript_path"])
    kind, base = row["kind"], deps.root(row["kind"])
    if not base.exists():
        return None
    native = (agent.get("agent_session") or {}).get("value")
    if native:
        found = READERS[kind].find(base, native)
        if found:
            return found
    tag = row["id"].encode()
    if kind == "opencode":
        path, _workspace = READERS[kind].latest(base, Path(row["folder"]))
        return path if path and tag in chat_bytes(kind, path) else None
    since = datetime.strptime(row["started_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() - 5
    for path in base.rglob("*.jsonl"):
        try:
            if path.stat().st_mtime >= since and tag in path.read_bytes():
                return path
        except OSError:
            continue
    return None


def _finished(kind, raw, job):
    offset = raw.find(job.encode())
    if offset < 0:
        return None
    reader = READERS[kind]
    newline = raw.find(b"\n", offset)
    ended = False
    for line in raw[newline + 1:].splitlines() if newline >= 0 else []:
        try:
            if reader.turn_ended(json.loads(line)):
                ended = True
        except json.JSONDecodeError:
            continue
    if not ended:
        return None
    records = _parse(kind, raw, offset, len(raw))[0]
    answers = [r["text"] for r in records if r["role"] == "assistant"]
    return answers[-1] if answers else ""


def _check(conn, deps, row, agents):
    if row["pane_id"] == BACKGROUND:
        return _check_background(conn, row)
    agent = agents.get(row["agent_name"])
    if agent is None:
        return "gone", "The agent exited or its pane was closed. Last lines: " + (_pane_tail(deps, row["pane_id"]) or "(none)")
    status = agent.get("agent_status")
    if row["state"] == "starting":
        if status in ("idle", "done"):
            return _send(deps, row["agent_name"], row["prompt"]), None
        return "starting", _pane_tail(deps, row["pane_id"])
    path = _transcript(deps, row, agent)
    if path and not row["transcript_path"]:
        conn.execute("UPDATE delegations SET transcript_path = ? WHERE id = ?", (str(path), row["id"]))
    raw = chat_bytes(row["kind"], path) if path else b""
    answer = _finished(row["kind"], raw, row["id"]) if raw else None
    if answer is not None:
        return "done", answer
    if status == "blocked":
        return "blocked", _pane_tail(deps, row["pane_id"])
    if status in ("idle", "done") and not row["resent"] and row["id"].encode() not in raw and _age(row) > RESEND_AFTER:
        conn.execute("UPDATE delegations SET resent = 1 WHERE id = ?", (row["id"],))
        return _send(deps, row["agent_name"], row["prompt"]), None
    return "running", None


def _age(row):
    started = datetime.strptime(row["started_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - started).total_seconds()


def _refresh(conn, deps, rows, agents):
    for row in rows:
        state, text = _check(conn, deps, row, agents)
        if state != row["state"] or text is not None:
            finished = now() if state in ("done", "gone") else None
            conn.execute(
                "UPDATE delegations SET state = ?, result = COALESCE(?, result), finished_at = COALESCE(?, finished_at) WHERE id = ?",
                (state, text, finished, row["id"]),
            )
            conn.commit()
            if state == "done":
                _save_result(conn, row, text)
            if state in ("done", "gone"):
                release(conn, row["folder"], row["agent_name"])
    conn.commit()


def _wait(conn, deps, session, started):
    deadline = started + WAIT_SECONDS
    while True:
        rows = conn.execute(
            f"SELECT * FROM delegations WHERE caller_session_id = ? AND state IN ({OPEN_SQL})", (session,),
        ).fetchall()
        _refresh(conn, deps, rows, _agents(deps))
        pending = conn.execute(
            "SELECT COUNT(*) FROM delegations WHERE caller_session_id = ? AND state IN ('starting', 'running')",
            (session,),
        ).fetchone()[0]
        if not pending or deps.clock() + POLL_SECONDS > deadline:
            break
        deps.sleep(POLL_SECONDS)
    rows = conn.execute(
        f"SELECT * FROM delegations WHERE caller_session_id = ? AND (reported = 0 OR state IN ({OPEN_SQL})) ORDER BY started_at, rowid",
        (session,),
    ).fetchall()
    jobs = []
    for row in rows:
        jobs.append({
            "job": row["id"], "to": row["kind"], "agent": row["agent_name"], "pane": row["pane_id"],
            "state": row["state"], "result": one_line(row["result"]) if row["state"] in ("done", "gone") else row["result"],
        })
        if row["state"] in ("done", "gone"):
            conn.execute("UPDATE delegations SET reported = 1 WHERE id = ?", (row["id"],))
    conn.commit()
    watch = WATCH if deps.use_herdr() else f"tail -f {_jobs_dir(conn)}/<job>.log"
    out = {"session": session, "watch": watch, "jobs": jobs}
    if any(j["state"] in ("starting", "running", "blocked") for j in jobs):
        out["next"] = (
            "Some agents are not finished. Call delegate_wait with this session until none are running; "
            "for a blocked one, call it again after the user has answered in its pane."
        )
    if any(j["state"] in ("starting", "blocked") for j in jobs):
        out["blocked"] = "An agent is waiting on a question or approval. Tell the user; do not answer it for them."
    return out
