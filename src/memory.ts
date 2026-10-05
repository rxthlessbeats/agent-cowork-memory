import { createHash } from "node:crypto";
import { existsSync, readFileSync, statSync } from "node:fs";
import { isAbsolute, join, relative, sep } from "node:path";
import { type Db, transaction } from "./db.ts";
import { canonical, projectRoot } from "./project.ts";
import { samePath } from "./readers/index.ts";
import { AcmError, daysAgo, inDays, newId, now, oneLine } from "./util.ts";

export const OPEN_JOB = ["starting", "running", "blocked", "queued"]; // queued: waiting for its busy agent
const OPEN_SQL = OPEN_JOB.map((s) => `'${s}'`).join(", ");
const SHORT_DAYS = 7;
const HOLD_HOURS = 2; // ponytail: a hold lapses once its session has been quiet this long, unless its job is open
const IDLE_DAYS = 30; // sessions idle this long are pruned; threads idle this long leave the open list
const OTHER_SHORT = 5; // other threads' short notes in a first context, newest first, one line each
const FIRST_EVENTS = 8;
const OPEN_THREADS = 8;
const RECENT_JOBS = 5;
const CHECK = 3; // notes returned by note_add's contradiction check
const NOTE_FILES = 10;

/** A sessions row, with the project's root. */
type SessionRow = {
  id: string;
  project_id: string;
  root: string;
  harness: string;
  chat: string;
  folder: string;
  thread_id: string | null;
  seen_note: number;
  seen_event: number;
  seen_job: number;
  context_calls: number;
};

export type Session = SessionRow & {
  /** False when the user started this chat, true when acm did for a job; unset when that can't be told. */
  delegated?: boolean;
};

type Row = Record<string, unknown>;
type Note = {
  seq: number;
  id: string;
  thread_id: string | null;
  session_id: string | null;
  harness: string;
  tier: string;
  body: string;
  created_at: string;
};

const LIVE = "replaced_by IS NULL AND (expires_at IS NULL OR expires_at > ?)";

// ---- projects, sessions, threads ----

function projectId(db: Db, root: string): string {
  const row = db.prepare("SELECT id FROM projects WHERE root = ?").get(root) as Row | undefined;
  if (row) return row.id as string;
  const id = newId("p_");
  db.prepare("INSERT INTO projects (id, root, created_at) VALUES (?, ?, ?)").run(id, root, now());
  return id;
}

/** The session for one chat: found by agent and chat id, created on the first call. */
export function sessionFor(db: Db, opts: { harness: string; chat: string; folder: string }): Session {
  const folder = canonical(opts.folder);
  const root = projectRoot(folder);
  const project = projectId(db, root);
  const stamp = now();
  db.prepare(
    `INSERT INTO sessions (id, project_id, harness, chat, folder, started_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT (project_id, harness, chat) DO UPDATE SET last_seen_at = excluded.last_seen_at, folder = excluded.folder`,
  ).run(newId("s_"), project, opts.harness, opts.chat, folder, stamp, stamp);
  const row = db
    .prepare("SELECT * FROM sessions WHERE project_id = ? AND harness = ? AND chat = ?")
    .get(project, opts.harness, opts.chat) as SessionRow;
  return { ...row, root };
}

function reload(db: Db, s: Session): Session {
  return {
    ...(db.prepare("SELECT * FROM sessions WHERE id = ?").get(s.id) as SessionRow),
    root: s.root,
    delegated: s.delegated,
  };
}

export function addEvent(db: Db, threadId: string, sessionId: string | null, kind: string, text: string): void {
  const stamp = now();
  db.prepare("INSERT INTO events (thread_id, session_id, at, kind, text) VALUES (?, ?, ?, ?, ?)").run(
    threadId,
    sessionId,
    stamp,
    kind,
    oneLine(text, 160),
  );
  db.prepare("UPDATE threads SET updated_at = ? WHERE id = ?").run(stamp, threadId);
}

/** The session's thread, started (and named) now if it has none. */
/** New work on a thread that was marked done opens it again, so other chats see it in open_threads. */
function reopen(db: Db, threadId: string, s: Session): void {
  const changed = db.prepare("UPDATE threads SET status = 'open' WHERE id = ? AND status != 'open'").run(threadId);
  if (changed.changes) addEvent(db, threadId, s.id, "reopened", `${s.harness} reopened the thread`);
}

/** The session's thread, started (and named) now if it has none. Called when the chat does new work. */
export function ensureThread(db: Db, s: Session, name: string): string {
  if (s.thread_id) {
    reopen(db, s.thread_id, s);
    return s.thread_id;
  }
  const id = newId("t_");
  const stamp = now();
  db.prepare("INSERT INTO threads (id, project_id, name, created_at, updated_at) VALUES (?, ?, ?, ?, ?)").run(
    id,
    s.project_id,
    oneLine(name, 80),
    stamp,
    stamp,
  );
  db.prepare("UPDATE sessions SET thread_id = ? WHERE id = ?").run(id, s.id);
  s.thread_id = id;
  addEvent(db, id, s.id, "started", `${s.harness} started this thread`);
  return id;
}

/** Put the session on a thread of its project, reopening it if it was done. */
export function joinThread(db: Db, s: Session, threadId: string): void {
  const thread = db.prepare("SELECT * FROM threads WHERE id = ?").get(threadId) as Row | undefined;
  if (!thread || thread.project_id !== s.project_id) {
    throw new AcmError("invalid", "unknown thread in this project; open_threads in context lists them", {
      thread: threadId,
    });
  }
  // A delegated agent joins the thread its brief names: that links it to its open job. A reused agent is
  // often on that thread already, so link first. Never the job's caller, and never a chat the user started:
  // a user's second chat joining the thread is not the worker. sending: the brief is out, its row not yet updated.
  if (s.delegated !== false) {
    db.prepare(
      `UPDATE jobs SET worker_session_id = ? WHERE seq = (
         SELECT seq FROM jobs WHERE thread_id = ? AND kind = ? AND folder = ? AND worker_session_id IS NULL
           AND state IN (${OPEN_SQL}, 'sending') AND caller_session_id != ?
         ORDER BY seq LIMIT 1)`,
    ).run(s.id, threadId, s.harness, s.root, s.id);
  }
  reopen(db, threadId, s);
  if (s.thread_id === threadId) return;
  db.prepare("UPDATE sessions SET thread_id = ? WHERE id = ?").run(threadId, s.id);
  s.thread_id = threadId;
  addEvent(db, threadId, s.id, "joined", `${s.harness} joined`);
}

// ---- notes ----

function liveNote(db: Db, projectId: string, id: string): Note | undefined {
  return db.prepare(`SELECT * FROM notes WHERE id = ? AND project_id = ? AND ${LIVE}`).get(id, projectId, now()) as
    | Note
    | undefined;
}

// context checks every noted file on every call: hash one again only when its size or modified time changed.
const hashes = new Map<string, { stamp: string; hash: string }>();

function hashFile(path: string): string | null {
  try {
    const { size, mtimeMs } = statSync(path);
    const stamp = `${size} ${mtimeMs}`;
    const known = hashes.get(path);
    if (known?.stamp === stamp) return known.hash;
    const hash = createHash("sha256").update(readFileSync(path)).digest("hex");
    hashes.set(path, { stamp, hash });
    return hash;
  } catch {
    return null;
  }
}

/** Repo files a note's text mentions: path-like words that name a file inside the project. */
export function mentionedFiles(root: string, text: string): string[] {
  const found = new Set<string>();
  for (const word of text.match(/[\w.\-/\\]+/g) ?? []) {
    const cleaned = word.replace(/^\.[/\\]/, "").replace(/\.+$/, ""); // "./x" and a sentence's final dot
    if (!/[./\\]/.test(cleaned) || cleaned.includes("..")) continue;
    const full = isAbsolute(cleaned) ? cleaned : join(root, cleaned);
    const rel = relative(root, full);
    if (!rel || rel.startsWith("..") || isAbsolute(rel)) continue;
    try {
      if (existsSync(full) && statSync(full).isFile()) found.add(rel.split(sep).join("/"));
    } catch {
      // unreadable: not a file we can track
    }
    if (found.size >= NOTE_FILES) break;
  }
  return [...found];
}

const STOP = new Set(
  "about after again also because been before being both could does doing done each from have having here into just more most must only other over same should some such than that their them then there these they this those through under until very were what when where which while will with would your".split(
    " ",
  ),
);

function words(text: string): string[] {
  return [
    ...new Set((text.toLowerCase().match(/[\p{L}\p{N}_]+/gu) ?? []).filter((w) => w.length >= 4 && !STOP.has(w))),
  ];
}

/** Live notes on the same topic as text: what a new note might contradict. */
function similar(db: Db, projectId: string, text: string, exclude: string[]): Note[] {
  const terms = words(text).slice(0, 12);
  if (!terms.length) return [];
  const rows = db
    .prepare("SELECT ref FROM search WHERE search MATCH ? AND project_id = ? ORDER BY rank LIMIT 12")
    .all(terms.map((t) => `"${t}"`).join(" OR "), projectId) as Row[];
  // One shared word (a project name, a ticket prefix) is not a topic; ask for two, or all of a short note's.
  const need = Math.min(2, terms.length);
  const out: Note[] = [];
  for (const { ref } of rows) {
    if (typeof ref !== "string" || !ref.startsWith("n_") || exclude.includes(ref)) continue;
    const note = liveNote(db, projectId, ref);
    const shared = note ? words(note.body).filter((w) => terms.includes(w)).length : 0;
    if (note && shared >= need) out.push(note);
    if (out.length >= CHECK) break;
  }
  return out;
}

export function noteAdd(db: Db, s: Session, opts: { text: string; tier?: string; supersedes?: string }) {
  const tier = opts.tier ?? "short";
  if (tier !== "short" && tier !== "long") throw new AcmError("invalid", "tier must be short or long");
  const text = (opts.text ?? "").trim();
  if (!text) throw new AcmError("invalid", "text is required");
  sweep(db, s.project_id);
  const id = newId("n_");
  const outcome = transaction(db, () => {
    const old = opts.supersedes ? liveNote(db, s.project_id, opts.supersedes) : undefined;
    if (opts.supersedes && !old) {
      throw new AcmError("invalid", "supersedes must be a live note of this project", { supersedes: opts.supersedes });
    }
    // A replacement lives where the note it replaces lived, so that thread's timeline shows it.
    const thread = old?.thread_id ?? ensureThread(db, s, text);
    const stamp = now();
    db.prepare(
      `INSERT INTO notes (id, project_id, thread_id, session_id, harness, tier, body, created_at, expires_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    ).run(id, s.project_id, thread, s.id, s.harness, tier, text, stamp, tier === "short" ? inDays(SHORT_DAYS) : null);
    const files = mentionedFiles(s.root, text);
    for (const path of files) {
      db.prepare("INSERT INTO note_files (note_id, path, hash) VALUES (?, ?, ?)").run(
        id,
        path,
        hashFile(join(s.root, path)),
      );
    }
    db.prepare("INSERT INTO search (ref, project_id, body) VALUES (?, ?, ?)").run(id, s.project_id, text);
    if (old) {
      db.prepare("UPDATE notes SET replaced_by = ? WHERE id = ?").run(id, old.id);
      db.prepare("DELETE FROM search WHERE ref = ?").run(old.id);
      const same = oneLine(old.body, 100000) === oneLine(text, 100000);
      addEvent(
        db,
        thread,
        s.id,
        same ? "rechecked" : "replaced",
        same ? `${s.harness} re-checked: ${text}` : `${s.harness} replaced "${old.body}" with "${text}"`,
      );
    } else {
      addEvent(db, thread, s.id, "note", `${s.harness} ${tier} note: ${text}`);
    }
    return { thread, files };
  });
  const out: Record<string, unknown> = { id, tier, thread: outcome.thread };
  if (outcome.files.length) out.files = outcome.files;
  // A replacement can contradict other notes too, so every write is checked; only the replaced note is left out.
  const check = similar(db, s.project_id, text, [id, opts.supersedes ?? ""]);
  if (check.length) {
    out.check = check.map((n) => ({ id: n.id, body: oneLine(n.body, 160) }));
    out.next = "If your note makes one of these false, call note_add again with supersedes set to its id.";
  }
  return out;
}

/** Notes whose mentioned files changed since they were written: id and the changed paths. */
function staleNotes(db: Db, s: Session): Map<string, string[]> {
  const stale = new Map<string, string[]>();
  const rows = db
    .prepare(
      `SELECT f.note_id, f.path, f.hash FROM note_files f JOIN notes n ON n.id = f.note_id
       WHERE n.project_id = ? AND n.replaced_by IS NULL AND (n.expires_at IS NULL OR n.expires_at > ?)`,
    )
    .all(s.project_id, now()) as Row[];
  for (const row of rows) {
    if (hashFile(join(s.root, row.path as string)) === row.hash) continue;
    const list = stale.get(row.note_id as string) ?? [];
    list.push(row.path as string);
    stale.set(row.note_id as string, list);
  }
  return stale;
}

export function noteSearch(db: Db, s: Session, query: string) {
  const terms = (query ?? "").match(/[\p{L}\p{N}_]+/gu) ?? [];
  if (!terms.length) throw new AcmError("invalid", "empty search");
  sweep(db, s.project_id);
  const match = terms.map((t) => `"${t}"*`).join(" AND "); // a prefix, so rain finds rains
  const refs = db
    .prepare("SELECT ref FROM search WHERE search MATCH ? AND project_id = ? ORDER BY rank LIMIT 30")
    .all(match, s.project_id) as Row[];
  const notes: Row[] = [];
  const jobs: Row[] = [];
  for (const { ref } of refs) {
    const id = ref as string;
    if (id.startsWith("n_")) {
      const note = liveNote(db, s.project_id, id);
      if (note) notes.push(publicNote(note, s));
    } else {
      const job = db.prepare("SELECT * FROM jobs WHERE id = ?").get(id) as Row | undefined;
      if (job)
        jobs.push({
          id,
          agent: job.agent_name,
          state: job.state,
          task: oneLine(job.task as string, 160),
          result: job.result,
        });
    }
  }
  return { notes, jobs };
}

function publicNote(n: Note, s: Session, clip?: boolean): Row {
  const out: Row = { id: n.id, tier: n.tier, body: clip ? oneLine(n.body) : n.body, by: n.harness, at: n.created_at };
  if (n.thread_id && n.thread_id !== s.thread_id) out.thread = n.thread_id;
  return out;
}

// ---- holds ----

/** A hold path relative to the project, with forward slashes. */
export function relPath(path: string): string {
  const text = (path ?? "").replaceAll("\\", "/").trim();
  const parts = text.split("/").filter((p) => p && p !== ".");
  if (!text || text.startsWith("/") || /^[A-Za-z]:/.test(text) || parts.includes("..") || !parts.length) {
    throw new AcmError("invalid", "hold paths must be relative to the project, such as src/app.ts");
  }
  return parts.join("/");
}

/**
 * Add to this session's holds; [] releases them all. Returns paths someone else holds, changing nothing then.
 * Adds, not replaces: a worker holds files as it comes to them, and must keep the ones it is still editing.
 */
export function claim(db: Db, s: Session, paths: string[]): string[] {
  const wanted = [...new Set(paths.map(relPath))];
  return transaction(db, () => {
    if (!wanted.length) {
      db.prepare("DELETE FROM holds WHERE session_id = ?").run(s.id);
      return [];
    }
    const taken = (
      db.prepare("SELECT path FROM holds WHERE project_id = ? AND session_id != ?").all(s.project_id, s.id) as Row[]
    ).map((r) => r.path as string);
    // samePath: src/App.ts and src/app.ts are one file where the file system ignores case.
    const busy = wanted.filter((p) => taken.some((t) => samePath(t, p)));
    if (!busy.length) {
      const insert = db.prepare(
        "INSERT OR IGNORE INTO holds (project_id, path, session_id, created_at) VALUES (?, ?, ?, ?)",
      );
      for (const path of wanted) insert.run(s.project_id, path, s.id, now());
    }
    return busy;
  });
}

export function releaseHolds(db: Db, sessionId: string | null): void {
  if (sessionId) db.prepare("DELETE FROM holds WHERE session_id = ?").run(sessionId);
}

/** Who holds what, named by their job's agent when they are a delegated agent. */
export function held(db: Db, projectId: string): Row[] {
  return (
    db
      .prepare(
        `SELECT h.path, s.harness, (SELECT agent_name FROM jobs WHERE worker_session_id = s.id ORDER BY seq DESC LIMIT 1) AS agent
         FROM holds h JOIN sessions s ON s.id = h.session_id WHERE h.project_id = ? ORDER BY h.path`,
      )
      .all(projectId) as Row[]
  ).map((r) => ({ path: r.path, agent: r.agent ?? r.harness }));
}

// ---- context ----

/** A job in one line, like the timeline: what was asked, and how it ended. note_search has the full result. */
function oneLineJob(j: Row): string {
  const result = j.result ? ` → ${oneLine(j.result as string, 100)}` : "";
  return `${j.id} ${j.agent_name} ${j.state}: ${oneLine(j.task as string, 80)}${result}`;
}

function eventLine(e: Row): string {
  return `${(e.at as string).slice(5, 16).replace("T", " ")} ${e.text}`;
}

export function context(db: Db, given: Session, opts: { hold?: string[]; thread?: string; done?: boolean } = {}) {
  sweep(db, given.project_id);
  let s = reload(db, given);
  const switching = Boolean(opts.thread && opts.thread !== s.thread_id);
  if (opts.thread) joinThread(db, s, opts.thread);
  if (opts.done) {
    if (!s.thread_id) throw new AcmError("invalid", "this chat has no thread to mark done");
    db.prepare("UPDATE threads SET status = 'done' WHERE id = ?").run(s.thread_id);
    addEvent(db, s.thread_id, s.id, "done", `${s.harness} marked the thread done`);
  }
  const busy = opts.hold !== undefined ? claim(db, s, opts.hold) : [];
  s = reload(db, s);
  // Read up to these marks, and record them as seen: whatever another agent writes after this is shown next time.
  const maxNote = Number(
    (db.prepare("SELECT MAX(seq) AS m FROM notes WHERE project_id = ?").get(s.project_id) as Row).m ?? 0,
  );
  const maxEvent = s.thread_id
    ? Number((db.prepare("SELECT MAX(id) AS m FROM events WHERE thread_id = ?").get(s.thread_id) as Row).m ?? 0)
    : 0;
  const maxJob = Number(
    (db.prepare("SELECT MAX(seq) AS m FROM jobs WHERE project_id = ?").get(s.project_id) as Row).m ?? 0,
  );
  // A chat's first call, or its first look at a thread it just joined, gets the full picture.
  const first = s.context_calls === 0 || switching;
  const stamp = now();
  const out: Row = {};

  const thread = s.thread_id ? (db.prepare("SELECT * FROM threads WHERE id = ?").get(s.thread_id) as Row) : null;
  if (thread) out.thread = { id: thread.id, name: thread.name, status: thread.status };

  // Notes: this thread's and every long note in full; other threads' short notes one line each.
  const notes = db
    .prepare(`SELECT * FROM notes WHERE project_id = ? AND ${LIVE} AND seq > ? AND seq <= ? ORDER BY seq DESC`)
    .all(s.project_id, stamp, first ? 0 : s.seen_note, maxNote)
    // After the first call, "new" means new from someone else: a chat knows what it wrote itself.
    .filter((n) => first || (n as Note).session_id !== s.id) as Note[];
  const mine = notes.filter((n) => n.tier === "long" || (n.thread_id && n.thread_id === s.thread_id));
  const others = notes.filter((n) => !mine.includes(n));
  const shownOthers = first ? others.slice(0, OTHER_SHORT) : others;
  out.notes = [...mine.map((n) => publicNote(n, s)), ...shownOthers.map((n) => publicNote(n, s, true))];
  const total = (
    db.prepare(`SELECT COUNT(*) AS n FROM notes WHERE project_id = ? AND ${LIVE}`).get(s.project_id, stamp) as Row
  ).n as number;
  const unshown = total - mine.length - shownOthers.length;
  if (first && unshown > 0) out.notes_not_shown = unshown;

  const stale = staleNotes(db, s);
  if (stale.size) {
    out.stale = [...stale].map(([id, files]) => ({ id, files }));
    out.stale_next =
      "These notes mention files that changed since they were written. Check each; then call note_add with supersedes set to its id: the same text if it still holds, a corrected text if not.";
  }

  if (s.thread_id) {
    const events = first
      ? (db
          .prepare("SELECT * FROM events WHERE thread_id = ? AND id <= ? ORDER BY id DESC LIMIT ?")
          .all(s.thread_id, maxEvent, FIRST_EVENTS) as Row[])
      : (db
          .prepare(
            "SELECT * FROM events WHERE thread_id = ? AND id > ? AND id <= ? AND session_id IS NOT ? ORDER BY id DESC",
          )
          .all(s.thread_id, s.seen_event, maxEvent, s.id) as Row[]);
    if (events.length) out.timeline = events.reverse().map(eventLine);
  }

  if (first) {
    const open = db
      .prepare(
        `SELECT t.*, (SELECT text FROM events WHERE thread_id = t.id ORDER BY id DESC LIMIT 1) AS last
         FROM threads t WHERE t.project_id = ? AND t.status = 'open' AND t.updated_at > ? AND t.id IS NOT ?
         ORDER BY t.updated_at DESC LIMIT ?`,
      )
      .all(s.project_id, daysAgo(IDLE_DAYS), s.thread_id, OPEN_THREADS) as Row[];
    if (open.length)
      out.open_threads = open.map((t) => ({
        id: t.id,
        name: t.name,
        updated: t.updated_at,
        last: oneLine(t.last as string, 100),
      }));
    if (!s.thread_id) {
      out.thread_next =
        "This chat has no thread yet. If it continues one of open_threads, call context with thread set to its id; otherwise your first note or delegation starts one.";
    }
  }

  // The first call shows the recent few; later calls every job since, so none is marked seen unshown.
  const jobs = db
    .prepare("SELECT * FROM jobs WHERE project_id = ? AND seq > ? AND seq <= ? ORDER BY seq DESC LIMIT ?")
    .all(s.project_id, first ? 0 : s.seen_job, maxJob, first ? RECENT_JOBS : -1) as Row[];
  if (jobs.length) out.jobs = jobs.map(oneLineJob);

  const working = (
    db
      .prepare(
        `SELECT * FROM jobs WHERE project_id = ? AND state IN (${OPEN_SQL}) AND worker_session_id IS NOT ? ORDER BY seq`,
      )
      .all(s.project_id, s.id) as Row[]
  ).map((j) => ({ agent: j.agent_name, state: j.state, task: oneLine(j.task as string, 120) }));
  if (working.length) out.working = working;
  const holds = held(db, s.project_id);
  if (holds.length) out.held = holds;
  if (busy.length) {
    const owners = new Map(holds.map((h) => [h.path, h.agent]));
    out.busy = busy.map((path) => ({ path, agent: owners.get(path) }));
  }

  db.prepare(
    "UPDATE sessions SET seen_note = ?, seen_event = ?, seen_job = ?, context_calls = context_calls + 1 WHERE id = ?",
  ).run(maxNote, maxEvent, maxJob, s.id);
  return out;
}

// ---- sweep ----

/** Delete expired notes, lapsed holds, and sessions nobody uses. Threads are never deleted. */
export function sweep(db: Db, projectId: string): void {
  const stamp = now();
  const quiet = daysAgo(HOLD_HOURS / 24);
  const workerOfOpenJob = `EXISTS (SELECT 1 FROM jobs j WHERE j.worker_session_id = s.id AND j.state IN (${OPEN_SQL}))`;
  transaction(db, () => {
    const expired = (
      db
        .prepare("SELECT id FROM notes WHERE project_id = ? AND expires_at IS NOT NULL AND expires_at <= ?")
        .all(projectId, stamp) as Row[]
    ).map((r) => r.id as string);
    for (const id of expired) {
      db.prepare("DELETE FROM search WHERE ref = ?").run(id);
      db.prepare("DELETE FROM notes WHERE id = ?").run(id);
    }
    db.prepare(
      `DELETE FROM holds WHERE project_id = ? AND session_id IN (
         SELECT s.id FROM sessions s WHERE s.last_seen_at < ? AND NOT ${workerOfOpenJob})`,
    ).run(projectId, quiet);
    db.prepare(
      `DELETE FROM sessions WHERE project_id = ? AND id IN (
         SELECT s.id FROM sessions s WHERE s.last_seen_at < ?
           AND NOT EXISTS (SELECT 1 FROM holds h WHERE h.session_id = s.id)
           AND NOT ${workerOfOpenJob}
           AND NOT EXISTS (SELECT 1 FROM jobs j WHERE j.caller_session_id = s.id AND j.state IN (${OPEN_SQL})))`,
    ).run(projectId, daysAgo(IDLE_DAYS));
  });
}
