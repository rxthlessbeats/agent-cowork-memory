"""One module per harness. Each exposes the same functions:

root()                 default transcript directory
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
    return max(found, key=lambda item: item[0].stat().st_mtime) if found else (None, None)


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
