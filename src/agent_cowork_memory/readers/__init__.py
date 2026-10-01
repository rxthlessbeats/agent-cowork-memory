"""One module per harness. Each exposes the same functions:

root()                 default transcript directory
chats(base, repo)      [(chat path, its workspace, mtime)] for every chat of a repo
latest(base, repo)     (newest chat path, its workspace) for a repo, or (None, None)
find(base, native)     the chat file for a native id, or None
native_id(path)        the harness's own id for a chat file
visible(obj)           ("message" | "skip" | "unknown", [{"role", "text", "timestamp"}])
turn_ended(obj)        True for the record that closes an agent turn

Readers whose chats are not one jsonl file also expose read(path) -> jsonl bytes and exists(path).
"""
import json


def slug(path):
    return str(path).strip("/").replace("/", "-")


def related(workspace, repo_root):
    return workspace == repo_root or repo_root in workspace.parents or workspace in repo_root.parents


def newest(found):
    if not found:
        return None, None
    path, workspace, _mtime = max(found, key=lambda item: item[2])
    return path, workspace


def in_workspaces(base, repo_root, folder, pattern):
    """Chats stored per workspace folder, for the repo and each folder above it."""
    found = []
    for workspace in (repo_root, *repo_root.parents):
        found += [(p, workspace, p.stat().st_mtime) for p in (base / folder(workspace)).glob(pattern) if p.is_file()]
    return found


def first_objects(path, count=20):
    with path.open("rb") as handle:
        for _ in range(count):
            line = handle.readline()
            if not line:
                return
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue
