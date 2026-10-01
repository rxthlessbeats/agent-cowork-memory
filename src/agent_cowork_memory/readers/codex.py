import os
from pathlib import Path

from agent_cowork_memory.readers import first_objects, newest, related

_SKIP_TYPES = {"session_meta", "event_msg", "token_usage_record", "turn_context", "world_state"}
_SKIP_PAYLOAD = {"reasoning", "function_call", "function_call_output", "custom_tool_call", "custom_tool_call_output"}
# ponytail: only the newest 200 rollouts are checked. Raise it if older chats need resuming.
_RECENT = 200


def root():
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"


def _meta(path):
    obj = next(first_objects(path, 1), {})
    return (obj.get("payload") or {}) if obj.get("type") == "session_meta" else {}


def chats(base, repo_root):
    files = sorted(((p.stat().st_mtime, p) for p in base.rglob("rollout-*.jsonl")), reverse=True)
    found = []
    for mtime, path in files[:_RECENT]:
        cwd = _meta(path).get("cwd")
        if cwd and related(Path(cwd), repo_root):
            found.append((path, Path(cwd), mtime))
    return found


def latest(base, repo_root):
    return newest(chats(base, repo_root))


def find(base, native):
    return next((p for p in base.rglob(f"rollout-*{native}.jsonl") if p.is_file()), None)


def turn_ended(obj):
    return obj.get("type") == "event_msg" and (obj.get("payload") or {}).get("type") == "task_complete"


def native_id(path):
    return _meta(path).get("session_id") or path.stem


def visible(obj):
    kind = obj.get("type")
    if kind in _SKIP_TYPES:
        return "skip", []
    if kind != "response_item":
        return "unknown", []
    payload = obj.get("payload") or {}
    ptype = payload.get("type")
    if ptype in _SKIP_PAYLOAD or payload.get("role") == "developer":
        return "skip", []
    if ptype != "message" or payload.get("role") not in ("user", "assistant"):
        return "unknown", []
    texts = []
    for block in payload.get("content") or []:
        if isinstance(block, dict) and block.get("type") in ("input_text", "output_text") and block.get("text"):
            if not block["text"].lstrip().startswith(("<environment_context>", "# AGENTS.md instructions")):
                texts.append(block["text"])
    if not texts:
        return "skip", []
    return "message", [{"role": payload["role"], "text": "\n".join(texts), "timestamp": obj.get("timestamp")}]
