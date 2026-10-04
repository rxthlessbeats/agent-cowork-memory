/** OpenCode keeps chats in SQLite (~/.local/share/opencode/opencode.db) or, on older installs, JSON files under storage/. */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";
import { DatabaseSync } from "node:sqlite";
import { type Chat, isFile, type Json, mtime, obj, type Reader, related, text, upward } from "./index.ts";

function storage(base: string): string {
  const folder = join(base, "storage");
  return existsSync(folder) && statSync(folder).isDirectory() ? folder : base;
}

function dbFor(path: string): string | null {
  return (
    upward(path)
      .map((p) => join(p, "opencode.db"))
      .find(isFile) ?? null
  );
}

/** Milliseconds or seconds, as seconds. */
function stamp(value: unknown): number {
  return typeof value === "number" ? (value > 10_000_000_000 ? value / 1000 : value) : 0;
}

function query<T>(db: string, fn: (conn: DatabaseSync) => T, fallback: T): T {
  let conn: DatabaseSync | undefined;
  try {
    conn = new DatabaseSync(db, { readOnly: true });
    return fn(conn);
  } catch {
    return fallback;
  } finally {
    conn?.close();
  }
}

function dbSessions(db: string): { id: string; workspace: string; mtime: number }[] {
  return query(
    db,
    (c) =>
      (c.prepare("SELECT id, directory, time_updated, parent_id FROM session").all() as Json[])
        .filter((r) => r.directory && !r.parent_id)
        .map((r) => ({ id: text(r.id), workspace: text(r.directory), mtime: stamp(r.time_updated) })),
    [],
  );
}

function inDb(path: string, id: string): boolean {
  const db = dbFor(path);
  return Boolean(db && dbSessions(db).some((s) => s.id === id));
}

function load(path: string): Json | null {
  try {
    return obj(JSON.parse(readFileSync(path, "utf8")));
  } catch {
    return null;
  }
}

function walk(folder: string, keep: (name: string) => boolean): string[] {
  try {
    return (readdirSync(folder, { recursive: true }) as string[])
      .filter((p) => keep(basename(p)))
      .map((p) => join(folder, p))
      .filter(isFile);
  } catch {
    return [];
  }
}

function fileSessions(base: string): Chat[] {
  const out: Chat[] = [];
  for (const path of walk(join(storage(base), "session"), (n) => n.endsWith(".json"))) {
    const meta = load(path);
    if (!meta || meta.parentID || !text(meta.directory)) continue;
    out.push({ path, workspace: text(meta.directory), mtime: mtime(path) });
  }
  return out;
}

/** messages: each message and its parts. An assistant turn ends when it finished without calling a tool. */
function jsonl(messages: [Json, Json[]][]): Buffer {
  const lines: string[] = [];
  for (const [msg, parts] of messages) {
    const role = text(msg.role);
    const body = parts
      .filter((p) => p.type === "text" && text(p.text))
      .map((p) => text(p.text))
      .join("\n");
    if ((role !== "user" && role !== "assistant") || !body) continue;
    lines.push(JSON.stringify({ role, text: body }));
    const time = obj(msg.time);
    if (role === "assistant" && msg.finish !== "tool-calls" && (!Object.keys(time).length || time.completed)) {
      lines.push(JSON.stringify({ type: "turn_ended" }));
    }
  }
  return Buffer.from(lines.map((l) => `${l}\n`).join(""));
}

function fromFiles(path: string): Buffer {
  const store = basename(dirname(path)) === "session" ? dirname(dirname(path)) : dirname(dirname(dirname(path)));
  const id = basename(path, ".json");
  const found = walk(join(store, "message", id), (n) => n.endsWith(".json"))
    .map(load)
    .filter((m): m is Json => m !== null)
    .sort((a, b) => stamp(obj(a.time).created) - stamp(obj(b.time).created));
  return jsonl(
    found.map((msg) => [
      msg,
      walk(join(store, "part", text(msg.id)), (n) => n.endsWith(".json"))
        .sort()
        .map(load)
        .filter((p): p is Json => p !== null),
    ]),
  );
}

function fromDb(db: string, id: string): Buffer {
  return query(
    db,
    (c) => {
      const parts = c.prepare("SELECT data FROM part WHERE message_id = ? ORDER BY time_created, rowid");
      const rows = c
        .prepare("SELECT id, data FROM message WHERE session_id = ? ORDER BY time_created")
        .all(id) as Json[];
      return jsonl(
        rows.map((r) => [
          obj(JSON.parse(text(r.data))),
          (parts.all(text(r.id)) as Json[]).map((p) => obj(JSON.parse(text(p.data)))),
        ]),
      );
    },
    Buffer.alloc(0),
  );
}

export const opencode: Reader = {
  root: () => process.env.OPENCODE_DATA || join(homedir(), ".local", "share", "opencode"),

  chats(base, repoRoot) {
    const found = fileSessions(base).filter((c) => related(c.workspace, repoRoot));
    const db = dbFor(base);
    if (db) {
      for (const s of dbSessions(db)) {
        if (related(s.workspace, repoRoot)) {
          found.push({ path: join(storage(base), "session", `${s.id}.json`), workspace: s.workspace, mtime: s.mtime });
        }
      }
    }
    // A chat can be in both the old files and the database; keep the newer one.
    const newest = new Map<string, Chat>();
    for (const c of found.sort((a, b) => a.mtime - b.mtime)) newest.set(basename(c.path, ".json"), c);
    return [...newest.values()];
  },

  find(base, native) {
    const folder = join(storage(base), "session");
    const file = walk(folder, (n) => n === `${native}.json`)[0];
    if (file) return file;
    return inDb(base, native) ? join(folder, `${native}.json`) : null;
  },

  exists: (path) => isFile(path) || inDb(path, basename(path, ".json")),

  read(path) {
    if (isFile(path) && path.endsWith(".json")) return fromFiles(path);
    const db = dbFor(path);
    return db ? fromDb(db, basename(path, ".json")) : Buffer.alloc(0);
  },

  nativeId: (path) => basename(path, ".json"),

  turnEnded: (o) => o.type === "turn_ended",

  visible(o) {
    if (o.type === "turn_ended") return ["skip", []];
    const role = text(o.role);
    const body = text(o.text);
    if ((role === "user" || role === "assistant") && body) {
      return ["message", [{ role, text: body, timestamp: text(o.timestamp) || null }]];
    }
    return ["skip", []];
  },
};
