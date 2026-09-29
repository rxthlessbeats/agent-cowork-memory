import os
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  git_common_dir TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id),
  harness TEXT NOT NULL,
  native_id TEXT,
  label TEXT,
  working_directory TEXT,
  active_task_id TEXT,
  attached_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL
);
CREATE UNIQUE INDEX sessions_native
  ON sessions(project_id, harness, native_id) WHERE native_id IS NOT NULL;
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id),
  title TEXT NOT NULL,
  goal TEXT,
  status TEXT NOT NULL,
  owner_session_id TEXT,
  summary TEXT,
  next_action TEXT,
  blockers TEXT,
  version INTEGER NOT NULL,
  updated_at TEXT NOT NULL,
  archived_at TEXT
);
CREATE TABLE task_sessions (
  task_id TEXT NOT NULL REFERENCES tasks(id),
  session_id TEXT NOT NULL REFERENCES sessions(id),
  PRIMARY KEY (task_id, session_id)
);
CREATE TABLE checkpoints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT NOT NULL REFERENCES tasks(id),
  version INTEGER NOT NULL,
  session_id TEXT,
  status TEXT,
  summary TEXT,
  next_action TEXT,
  blockers TEXT,
  owner_session_id TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(task_id, version)
);
"""


def home_dir(explicit=None):
    if explicit:
        return Path(explicit)
    env = os.environ.get("ACM_HOME")
    if env:
        return Path(env)
    return Path.home() / ".agent-cowork-memory"


V2 = """
ALTER TABLE sessions ADD COLUMN transcript_path TEXT;
CREATE TABLE transcript_sources (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL UNIQUE REFERENCES sessions(id),
  path TEXT NOT NULL,
  native_id TEXT,
  generation INTEGER NOT NULL,
  size INTEGER NOT NULL,
  fingerprint TEXT NOT NULL
);
CREATE TABLE transcript_cursors (
  source_id TEXT NOT NULL REFERENCES transcript_sources(id),
  consumer_session_id TEXT NOT NULL REFERENCES sessions(id),
  generation INTEGER NOT NULL,
  byte_offset INTEGER NOT NULL,
  PRIMARY KEY (source_id, consumer_session_id)
);
"""

V3 = """
CREATE TABLE memories (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id),
  task_id TEXT REFERENCES tasks(id),
  author_session_id TEXT NOT NULL,
  tier TEXT NOT NULL,
  kind TEXT,
  body TEXT NOT NULL,
  source TEXT,
  reason TEXT,
  supersedes_id TEXT,
  expires_at TEXT,
  forgotten_at TEXT,
  superseded_at TEXT,
  promoted_at TEXT,
  created_at TEXT NOT NULL
);
CREATE VIRTUAL TABLE memories_fts USING fts5(memory_id UNINDEXED, body);
"""


def migrate(conn):
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version < 1:
        conn.executescript(SCHEMA)
        conn.execute("PRAGMA user_version=1")
        version = 1
    if version < 2:
        conn.executescript(V2)
        conn.execute("PRAGMA user_version=2")
        version = 2
    if version < 3:
        conn.executescript(V3)
        conn.execute("PRAGMA user_version=3")
    conn.commit()


def connect(home):
    home = Path(home)
    home.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(home / "state.sqlite3", timeout=5, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    migrate(conn)
    return conn


def fts5_ok():
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE VIRTUAL TABLE fts_probe USING fts5(body)")
        return True
    except sqlite3.OperationalError:
        return False
    finally:
        conn.close()
