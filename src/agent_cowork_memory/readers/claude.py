import os
import re
from pathlib import Path

from agent_cowork_memory.readers import first_objects, in_workspaces, newest

_SKIP = {"queue-operation", "attachment", "atis-latch", "last-prompt", "cost-state", "system", "summary"}


def root():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "projects"


def chats(base, repo_root):
    return in_workspaces(base, repo_root, lambda workspace: re.sub(r"[^A-Za-z0-9]", "-", str(workspace)), "*.jsonl")


def latest(base, repo_root):
    return newest(chats(base, repo_root))


def find(base, native):
    return next((p for p in base.glob(f"*/{native}.jsonl") if p.is_file()), None)


def turn_ended(obj):
    return obj.get("type") == "system" and obj.get("subtype") == "turn_duration"


def native_id(path):
    return next((o["sessionId"] for o in first_objects(path) if o.get("sessionId")), path.stem)


def visible(obj):
    kind = obj.get("type")
    if kind in _SKIP:
        return "skip", []
    if kind not in ("user", "assistant"):
        return "unknown", []
    content = (obj.get("message") or {}).get("content")
    role = kind
    if isinstance(content, str):
        return "message", [{"role": role, "text": content, "timestamp": obj.get("timestamp")}]
    if not isinstance(content, list):
        return "unknown", []
    texts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        if btype == "text" and block.get("text"):
            texts.append(block["text"])
    if not texts:
        return "skip", []
    return "message", [{"role": role, "text": "\n".join(texts), "timestamp": obj.get("timestamp")}]
