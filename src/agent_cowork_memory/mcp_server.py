import json

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from agent_cowork_memory.db import connect
from agent_cowork_memory.ledger import AcmError

ATTACH = (
    "Call this first. repo_path is your working directory. Pass title to create a task "
    "or task to join one. The result's session id is required on every later call."
)
CONTEXT = "Call before doing work. Returns the current checkpoint, then short notes, then long notes."
RESUME = (
    "Call when the user says continue, or wants to pick up a chat from another agent. "
    "source is codex, cursor, or claude. It reads that agent's latest chat for this repo, "
    "attaches you to the same task, and returns the recent messages. Carry on from the "
    "last user message without asking the user to repeat it."
)
NOTE_ADD = "Save a short or long note on this session's task. Short notes expire in 7 days unless days is set."
NOTE_SEARCH = "Search note text in this project. Expired, forgotten, and superseded notes stay out."


def build_server(harness, home):
    mcp = MCPServer("acm")

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
    def attach(repo_path: str, label: str, task: str | None = None, title: str | None = None, goal: str | None = None, native_id: str | None = None) -> dict:
        from agent_cowork_memory.ledger import attach as attach_op
        return run(lambda conn: attach_op(
            conn, repo_path=repo_path, harness=harness, label=label,
            task=task, title=title, goal=goal, native_id=native_id,
        ))

    @mcp.tool(description=CONTEXT)
    def context(session: str) -> dict:
        from agent_cowork_memory.ledger import context as context_op
        return run(lambda conn: context_op(conn, session=session), session)

    @mcp.tool(description=RESUME)
    def resume(repo_path: str, source: str, limit: int = 30) -> dict:
        from agent_cowork_memory.transcript import resume as resume_op
        return run(lambda conn: resume_op(
            conn, harness=harness, repo_path=repo_path, source=source, limit=limit,
        ))

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
