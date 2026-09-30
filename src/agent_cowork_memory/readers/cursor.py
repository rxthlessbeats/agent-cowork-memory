import os
from pathlib import Path

from agent_cowork_memory.readers import newest, slug


def root():
    return Path(os.environ.get("CURSOR_TRANSCRIPTS", Path.home() / ".cursor" / "projects"))


def latest(base, repo_root):
    found = []
    for workspace in (repo_root, *repo_root.parents):
        files = (base / slug(workspace) / "agent-transcripts").glob("*/*.jsonl")
        found += [(p, workspace) for p in files if p.is_file()]
    return newest(found)


def find(base, native):
    return next((p for p in base.glob(f"*/agent-transcripts/{native}/{native}.jsonl") if p.is_file()), None)


def turn_ended(obj):
    return obj.get("type") == "turn_ended"


def native_id(path):
    return path.parent.name


def visible(obj):
    if obj.get("type") == "turn_ended" or "role" not in obj:
        return "skip", []
    role = obj.get("role")
    if role not in ("user", "assistant"):
        return "skip", []
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        return "message", [{"role": role, "text": content, "timestamp": None}]
    if not isinstance(content, list):
        return "unknown", []
    texts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use":
            continue
        if block.get("type") == "text" and block.get("text"):
            texts.append(block["text"])
        elif block.get("type") not in ("text", "tool_use"):
            return "unknown", []
    if not texts:
        return "skip", []
    return "message", [{"role": role, "text": "\n".join(texts), "timestamp": None}]
