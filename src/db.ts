import { mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { DatabaseSync } from "node:sqlite";

export type Db = DatabaseSync;

// One step per schema version; PRAGMA user_version records how many ran.
const MIGRATIONS = [
  `
  CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    root TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
  );
  CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
  );
  -- One row per chat. chat is the agent's chat id, or proc:<pid> when the chat can't be told.
  CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    harness TEXT NOT NULL,
    chat TEXT NOT NULL,
    folder TEXT NOT NULL,
    thread_id TEXT REFERENCES threads(id),
    seen_note INTEGER NOT NULL DEFAULT 0,
    seen_event INTEGER NOT NULL DEFAULT 0,
    seen_job INTEGER NOT NULL DEFAULT 0,
    context_calls INTEGER NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    UNIQUE (project_id, harness, chat)
  );
  -- The thread's timeline. session_id has no foreign key: events outlive pruned sessions.
  CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    thread_id TEXT NOT NULL REFERENCES threads(id),
    session_id TEXT,
    at TEXT NOT NULL,
    kind TEXT NOT NULL,
    text TEXT NOT NULL
  );
  CREATE INDEX events_thread ON events(thread_id, id);
  CREATE TABLE notes (
    seq INTEGER PRIMARY KEY,
    id TEXT NOT NULL UNIQUE,
    project_id TEXT NOT NULL REFERENCES projects(id),
    thread_id TEXT REFERENCES threads(id),
    session_id TEXT,
    harness TEXT NOT NULL,
    tier TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    replaced_by TEXT
  );
  CREATE INDEX notes_project ON notes(project_id, seq);
  -- Repo files a note mentions, with a hash of their content when it was written.
  CREATE TABLE note_files (
    note_id TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    hash TEXT,
    PRIMARY KEY (note_id, path)
  );
  CREATE TABLE jobs (
    seq INTEGER PRIMARY KEY,
    id TEXT NOT NULL UNIQUE,
    project_id TEXT NOT NULL REFERENCES projects(id),
    thread_id TEXT REFERENCES threads(id),
    caller_session_id TEXT NOT NULL,
    worker_session_id TEXT,
    folder TEXT NOT NULL,
    kind TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    pane TEXT,
    summary TEXT NOT NULL,
    task TEXT NOT NULL,
    prompt TEXT NOT NULL,
    transcript TEXT,
    state TEXT NOT NULL,
    result TEXT,
    reported INTEGER NOT NULL DEFAULT 0,
    resent INTEGER NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL,
    finished_at TEXT
  );
  CREATE INDEX jobs_caller ON jobs(caller_session_id, seq);
  CREATE INDEX jobs_folder ON jobs(folder, state);
  CREATE TABLE holds (
    project_id TEXT NOT NULL REFERENCES projects(id),
    path TEXT NOT NULL,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    created_at TEXT NOT NULL,
    PRIMARY KEY (project_id, path)
  );
  -- Live notes and job results, searchable together. ref is a note or job id.
  CREATE VIRTUAL TABLE search USING fts5(ref UNINDEXED, project_id UNINDEXED, body);
  `,
];

export function homeDir(explicit?: string): string {
  return explicit || process.env.ACM_HOME || join(homedir(), ".agent-cowork-memory");
}

export function connect(home: string): Db {
  mkdirSync(home, { recursive: true });
  // Not 0.2's state.sqlite3: that schema is different, and it stays as it was (PLAN-v0.3.0, question 9).
  const db = new DatabaseSync(join(home, "acm.sqlite3"), { timeout: 5000 });
  db.exec("PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON;");
  migrate(db);
  return db;
}

function version(db: Db): number {
  return (db.prepare("PRAGMA user_version").get() as { user_version: number }).user_version;
}

export function migrate(db: Db): void {
  MIGRATIONS.forEach((sql, i) => {
    const step = i + 1;
    if (version(db) >= step) return;
    transaction(db, () => {
      // Read again under the lock: another process may have run this step while we waited.
      if (version(db) < step) {
        db.exec(sql);
        db.exec(`PRAGMA user_version = ${step}`);
      }
    });
  });
}

/** Run fn in a write transaction; roll back if it throws. */
export function transaction<T>(db: Db, fn: () => T): T {
  db.exec("BEGIN IMMEDIATE");
  try {
    const out = fn();
    db.exec("COMMIT");
    return out;
  } catch (err) {
    db.exec("ROLLBACK");
    throw err;
  }
}
