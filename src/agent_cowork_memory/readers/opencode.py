"""OpenCode chats live in SQLite (~/.local/share/opencode/opencode.db) or, on older installs, JSON files under storage/."""
import json
import os
import sqlite3
from pathlib import Path

from agent_cowork_memory.readers import newest, related


def root():
    return Path(os.environ.get("OPENCODE_DATA", Path.home() / ".local" / "share" / "opencode"))


def _storage(base):
    return base / "storage" if (base / "storage").is_dir() else base


def _db_for(path):
    for parent in (path, *path.parents):
        db = parent / "opencode.db"
        if db.is_file():
            return db
    return None


def _connect(db):
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)


def _stamp(value, fallback=0):
    if isinstance(value, (int, float)) and value > 10_000_000_000:
        return value / 1000
    return value or fallback


def _sessions_db(db):
    try:
        conn = _connect(db)
        rows = conn.execute("SELECT id, directory, time_updated, parent_id FROM session").fetchall()
        conn.close()
    except sqlite3.Error:
        return []
    return [(sid, Path(directory), _stamp(stamp)) for sid, directory, stamp, parent in rows if directory and not parent]


def _in_db(path, sid):
    db = _db_for(path)
    return bool(db and any(found == sid for found, _dir, _stamp in _sessions_db(db)))


def _file_sessions(base):
    folder = _storage(base) / "session"
    out = []
    for path in folder.rglob("*.json") if folder.is_dir() else []:
        try:
            meta = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if meta.get("parentID") or not meta.get("directory"):
            continue
        out.append((path, Path(meta["directory"]), path.stat().st_mtime))
    return out


def chats(base, repo_root):
    found = [item for item in _file_sessions(base) if related(item[1], repo_root)]
    db = _db_for(base)
    if db:
        found += [
            (_storage(base) / "session" / f"{sid}.json", workspace, stamp)
            for sid, workspace, stamp in _sessions_db(db) if related(workspace, repo_root)
        ]
    return found


def latest(base, repo_root):
    return newest(chats(base, repo_root))


def find(base, native):
    folder = _storage(base) / "session"
    found = next((p for p in folder.glob(f"**/{native}.json") if p.is_file()), None) if folder.is_dir() else None
    if found:
        return found
    return folder / f"{native}.json" if _in_db(base, native) else None


def exists(path):
    return path.is_file() or _in_db(path, path.stem)


def native_id(path):
    return path.stem


def _jsonl(messages):
    """messages: (message info, its parts). An assistant turn ends when it finished without calling a tool."""
    lines = []
    for msg, parts in messages:
        role = msg.get("role")
        text = "\n".join(p["text"] for p in parts if p.get("type") == "text" and p.get("text"))
        if role not in ("user", "assistant") or not text:
            continue
        lines.append(json.dumps({"role": role, "text": text}))
        time = msg.get("time") or {}
        if role == "assistant" and msg.get("finish") != "tool-calls" and (not time or time.get("completed")):
            lines.append(json.dumps({"type": "turn_ended"}))
    return "".join(line + "\n" for line in lines).encode()


def _load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def _from_files(path):
    storage = path.parent.parent if path.parent.name == "session" else path.parents[2]
    found = [msg for msg in map(_load, (storage / "message" / path.stem).glob("*.json")) if msg]
    found.sort(key=lambda msg: _stamp((msg.get("time") or {}).get("created")))
    return _jsonl(
        (msg, [p for p in map(_load, sorted((storage / "part" / str(msg.get("id", ""))).glob("*.json"))) if p])
        for msg in found
    )


def _from_db(db, sid):
    conn = _connect(db)
    messages = conn.execute(
        "SELECT id, data FROM message WHERE session_id = ? ORDER BY time_created", (sid,),
    ).fetchall()
    out = [
        (json.loads(data), [json.loads(blob) for (blob,) in conn.execute(
            "SELECT data FROM part WHERE message_id = ? ORDER BY time_created, rowid", (mid,),
        )])
        for mid, data in messages
    ]
    conn.close()
    return _jsonl(out)


def read(path):
    if path.is_file() and path.suffix == ".json":
        return _from_files(path)
    db = _db_for(path)
    return _from_db(db, path.stem) if db else b""


def turn_ended(obj):
    return obj.get("type") == "turn_ended"


def visible(obj):
    if obj.get("type") == "turn_ended":
        return "skip", []
    role, text = obj.get("role"), obj.get("text")
    if role in ("user", "assistant") and text:
        return "message", [{"role": role, "text": text, "timestamp": obj.get("timestamp")}]
    return "skip", []
