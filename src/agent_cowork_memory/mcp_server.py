import json

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from agent_cowork_memory.db import connect
from agent_cowork_memory.ledger import HARNESSES, AcmError

ATTACH = (
    "Call this first. repo_path is your working directory. Pass title to create a task "
    "or task to join one. The result's session id is required on every later call."
)
CONTEXT = (
    "Call before doing work, and again before you edit a file. Returns your task, this project's "
    "notes, who is working in this folder, and which files are held. Pass hold with repo-relative "
    "paths to claim them before you write; a path in busy is held by someone else, so leave it alone. "
    "Pass hold as an empty list to release yours."
)
RESUME = (
    "Call when the user says continue, or wants to pick up a chat from another agent. "
    "source is codex, cursor, claude, or opencode. It reads that agent's latest chat for this repo, "
    "attaches you to the same task, and returns the recent messages. Carry on from the "
    "last user message without asking the user to repeat it."
)
DELEGATE = (
    "Call when the user asks another agent (codex, claude, cursor, or opencode) to do something, e.g. "
    "'tell codex to X and claude to Y'. Each agent starts in this project with a brief, in a herdr "
    "pane if herdr is installed, else in the background. There is one agent per kind per folder; a "
    "task for a busy agent comes back as busy. While you are working on a job acm sent you, this "
    "fails with not_allowed. summary: the problem, written for someone who has not seen this chat. "
    "tasks: [{to, task, done_when?, context?}]. Pass session if you have one from acm; otherwise "
    "keep the returned one. If the result has 'next', call delegate_wait with that session until "
    "no job is running. Report each job's state and result. If an agent is blocked, tell the user "
    "and do not answer it for them."
)
DELEGATE_WAIT = "Wait up to 45 seconds more for this session's delegated agents, then report their states."
NOTE_ADD = (
    "Save a note every agent in this project will see. Use tier='long' for things that stay true: "
    "decisions, the user's preferences, project conventions, gotchas. Use the default short tier "
    "for progress and findings; short notes expire in 7 days unless days is set. Pass supersedes "
    "with a note id to replace a note that is out of date. acm already records delegated job "
    "results, so don't save those."
)
NOTE_SEARCH = "Search note text in this project. Expired, forgotten, and superseded notes stay out."


def client_harness(name):
    name = (name or "").lower()
    return next((h for h in HARNESSES if h in name), None)


def build_server(harness, home):
    mcp = MCPServer("acm")

    def who(ctx):
        if harness:
            return harness
        params = ctx.request_context.session.client_params
        name = params.client_info.name if params else ""
        found = client_harness(name)
        if found is None:
            raise ToolError(json.dumps({
                "error": "harness",
                "message": f"Unknown MCP client {name!r}. Start acm with: acm mcp --harness {'|'.join(HARNESSES)}",
            }))
        return found

    def run(fn, session=None):
        conn = connect(home)
        try:
            try:
                data = fn(conn)
            except AcmError as exc:
                payload = {"error": exc.code, **exc.payload}
                payload.setdefault("session", session)
                raise ToolError(json.dumps(payload)) from exc
            data.setdefault("session", session)
            return data
        finally:
            conn.close()

    @mcp.tool(description=ATTACH)
    def attach(ctx: Context, repo_path: str, label: str, task: str | None = None, title: str | None = None, goal: str | None = None, native_id: str | None = None) -> dict:
        from agent_cowork_memory.ledger import attach as attach_op
        kind = who(ctx)
        return run(lambda conn: attach_op(
            conn, repo_path=repo_path, harness=kind, label=label,
            task=task, title=title, goal=goal, native_id=native_id,
        ))

    @mcp.tool(description=CONTEXT)
    def context(session: str, hold: list[str] | None = None) -> dict:
        from agent_cowork_memory.ledger import context as context_op
        return run(lambda conn: context_op(conn, session=session, hold=hold), session)

    @mcp.tool(description=RESUME)
    def resume(ctx: Context, repo_path: str, source: str, limit: int = 30) -> dict:
        from agent_cowork_memory.transcript import resume as resume_op
        kind = who(ctx)
        return run(lambda conn: resume_op(
            conn, harness=kind, repo_path=repo_path, source=source, limit=limit,
        ))

    @mcp.tool(description=DELEGATE)
    def delegate(ctx: Context, repo_path: str, summary: str, tasks: list[dict], session: str | None = None) -> dict:
        from agent_cowork_memory.delegate import delegate as delegate_op
        kind = who(ctx)
        return run(lambda conn: delegate_op(
            conn, harness=kind, repo_path=repo_path, summary=summary, tasks=tasks, session=session,
        ), session)

    @mcp.tool(description=DELEGATE_WAIT)
    def delegate_wait(session: str) -> dict:
        from agent_cowork_memory.delegate import delegate_wait as wait_op
        return run(lambda conn: wait_op(conn, session=session), session)

    @mcp.tool(description=NOTE_ADD)
    def note_add(session: str, text: str, tier: str = "short", kind: str | None = None, days: int | None = None, supersedes: str | None = None, source: str | None = None) -> dict:
        from agent_cowork_memory.memory import note_add as add_op
        return run(lambda conn: add_op(
            conn, session=session, text=text, tier=tier, kind=kind, days=days,
            supersedes=supersedes, source=source,
        ), session)

    @mcp.tool(description=NOTE_SEARCH)
    def note_search(session: str, query: str, task: str | None = None) -> dict:
        from agent_cowork_memory.memory import note_search as search_op
        return run(lambda conn: search_op(conn, session=session, query=query, task=task), session)

    return mcp


def serve(harness, home):
    build_server(harness, home).run(transport="stdio")
