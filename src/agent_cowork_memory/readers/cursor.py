import os
from pathlib import Path

from agent_cowork_memory.readers import dashes, newest, slug


def root():
    return Path(os.environ.get("CURSOR_TRANSCRIPTS", Path.home() / ".cursor" / "projects"))


def _folders(workspace):
    """Cursor's folder name for a workspace. Paths with only letters, digits and / are known to map to
    slug(); for other characters it is unconfirmed, so both the slug and the all-dashes form are tried."""
    names = {slug(workspace), dashes(workspace).strip("-")}
    return [Path(name) / "agent-transcripts" for name in sorted(names)]


def chats(base, repo_root):
    found = {}
    for workspace in (repo_root, *repo_root.parents):
        for folder in _folders(workspace):
            for path in (base / folder).glob("*/*.jsonl"):
                if path.is_file():
                    found.setdefault(path, (path, workspace, path.stat().st_mtime))
    return list(found.values())


def latest(base, repo_root):
    return newest(chats(base, repo_root))


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
