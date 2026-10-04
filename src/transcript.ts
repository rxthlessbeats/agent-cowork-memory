import { closeSync, existsSync, openSync, readFileSync, readSync, statSync } from "node:fs";
import type { Db } from "./db.ts";
import { ensureThread, joinThread, type Session, sessionFor } from "./memory.ts";
import { claude } from "./readers/claude.ts";
import { codex } from "./readers/codex.ts";
import { cursor } from "./readers/cursor.ts";
import { type Chat, type Json, obj, type Reader, within } from "./readers/index.ts";
import { opencode } from "./readers/opencode.ts";
import { AcmError, now, oneLine } from "./util.ts";

export const READERS: Record<string, Reader> = { codex, cursor, claude, opencode };
export const HARNESSES = Object.keys(READERS);
export type Roots = Record<string, string>;

const MAX_SCAN = 1_000_000;
const CHOICES = 10;
const SCAN = 30; // ponytail: the user's own chats go before job chats among the newest 30; raise it if jobs crowd them out
const JOB = /\[acm job ((?:acm_)?j_[0-9a-f]+)\]/;
const QUERY = /<user_query>([\s\S]*?)<\/user_query>/;
// Blocks a client wraps around a message that the user never typed: dropped whole, not just untagged.
const WRAPPERS =
  /<(local-command-caveat|local-command-stdout|local-command-stderr|command-name|command-message|command-args|system-reminder|codex_internal_context)\b[^>]*>[\s\S]*?<\/\1>/g;
const TAG = /<\/?[A-Za-z_][\w-]*[^>]*>/g;

export function rootOf(harness: string, roots: Roots = {}): string {
  return roots[harness] ?? READERS[harness].root();
}

export function chatBytes(harness: string, path: string): Buffer {
  const reader = READERS[harness];
  return reader.read ? reader.read(path) : readFileSync(path);
}

/** Part of a chat file, without reading the rest: `bytes` from the start, or from the end when negative. */
function chatPart(harness: string, path: string, bytes: number): Buffer {
  const reader = READERS[harness];
  if (reader.read) return reader.read(path); // built from a database: already small
  const size = statSync(path).size;
  const length = Math.min(Math.abs(bytes), size);
  const part = Buffer.alloc(length);
  const fd = openSync(path, "r");
  try {
    readSync(fd, part, 0, length, bytes < 0 ? size - length : 0);
  } finally {
    closeSync(fd);
  }
  return part;
}

const HEAD = 200_000; // enough for a chat's first message
const TAIL = -1_000_000; // where a chat's latest thread id is

export function chatExists(harness: string, path: string): boolean {
  const reader = READERS[harness];
  return reader.exists ? reader.exists(path) : existsSync(path);
}

export type Line = { start: number; end: number; role: string; text: string; timestamp?: string | null };

/** The visible messages of a chat from byte `start`, scanning at most maxScan bytes. */
export function parse(harness: string, raw: Buffer, start = 0, maxScan = MAX_SCAN) {
  const reader = READERS[harness];
  const records: Line[] = [];
  let unknown = 0;
  let offset = start;
  if (offset > 0 && (offset >= raw.length || raw[offset - 1] !== 10)) {
    const newline = raw.indexOf(10, offset);
    offset = newline < 0 ? raw.length : newline + 1;
  }
  let scanned = 0;
  while (offset < raw.length && scanned < maxScan) {
    const newline = raw.indexOf(10, offset);
    if (newline < 0) break;
    const end = newline + 1;
    scanned += end - offset;
    let o: Json;
    try {
      o = obj(JSON.parse(raw.subarray(offset, newline).toString("utf8")));
    } catch {
      offset = end;
      continue;
    }
    const [status, messages] = reader.visible(o);
    if (status === "unknown") unknown += 1;
    for (const m of messages) records.push({ start: offset, end, role: m.role, text: m.text, timestamp: m.timestamp });
    offset = end;
  }
  return { records, end: offset, unknown, truncated: offset < raw.length };
}

/** What the user typed, without wrappers a client adds around it. */
export function typed(message: string): string {
  const query = QUERY.exec(message);
  return oneLine((query ? query[1] : message).replace(WRAPPERS, " ").replace(TAG, " "), 100_000);
}

/** The chat's first message the user typed, and the acm job id if acm sent the chat. Give it the chat's bytes,
 * or its path to read only the start of the file. */
export function opening(harness: string, chat: Buffer | string): { first: string; job: string | null } {
  const raw = typeof chat === "string" ? chatPart(harness, chat, HEAD) : chat;
  const users = parse(harness, raw, 0, HEAD).records.filter((r) => r.role === "user");
  const first = users.map((r) => typed(r.text)).find(Boolean) ?? "";
  // Clients may put a note before the brief (OpenCode: "Note: The user opened the file …"), so look past it.
  const job = JOB.exec(first.slice(0, 600));
  return { first, job: job ? job[1] : null };
}

type Item = Chat & { harness: string };

/** Every chat of these agents in the repo, newest first, with chats opened in a folder above the repo last. */
function listing(harnesses: string[], repoRoot: string, roots: Roots): Item[] {
  const found: Item[] = [];
  for (const harness of harnesses) {
    const base = rootOf(harness, roots);
    if (!existsSync(base)) continue;
    for (const chat of READERS[harness].chats(base, repoRoot)) found.push({ ...chat, harness });
  }
  const above = (i: Item) => (within(i.workspace, repoRoot) ? 0 : 1);
  return found.sort((a, b) => above(a) - above(b) || b.mtime - a.mtime);
}

/** The thread a chat worked on: its session's, or the last thread id its tool results carry. The chat's bytes
 * are only fetched when no session knows. */
function chatThread(db: Db, s: Session, harness: string, native: string, bytes: () => Buffer): string | null {
  const row = db
    .prepare(
      "SELECT thread_id FROM sessions WHERE project_id = ? AND harness = ? AND chat = ? AND thread_id IS NOT NULL",
    )
    .get(s.project_id, harness, native) as Json | undefined;
  if (row) return row.thread_id as string;
  const ids =
    bytes()
      .toString("latin1")
      .match(/t_[0-9a-f]{12}/g) ?? [];
  for (const id of ids.reverse()) {
    const found = db.prepare("SELECT id FROM threads WHERE id = ? AND project_id = ?").get(id, s.project_id);
    if (found) return id;
  }
  return null;
}

function entry(db: Db, s: Session, item: Item) {
  const native = READERS[item.harness].nativeId(item.path);
  const { first, job } = opening(item.harness, item.path);
  const thread = chatThread(db, s, item.harness, native, () => chatPart(item.harness, item.path, TAIL));
  const name = thread ? (db.prepare("SELECT name FROM threads WHERE id = ?").get(thread) as Json).name : null;
  return {
    agent: item.harness,
    chat: native,
    updated: now(new Date(item.mtime * 1000)),
    folder: item.workspace,
    thread: name ? { id: thread, name } : null,
    first: oneLine(first, 160),
    job,
  };
}

export function chats(db: Db, s: Session, limit = 20, roots: Roots = {}) {
  return {
    chats: listing(HARNESSES, s.root, roots)
      .slice(0, limit)
      .map((i) => entry(db, s, i)),
  };
}

/** Keep the start and end of a message that alone is over the budget. */
function clip(message: string, size: number): string {
  const half = Math.floor(size / 2);
  return `${message.slice(0, half)}\n[... ${message.length - 2 * half} characters cut ...]\n${message.slice(-half)}`;
}

/** The chat an acm server process is in, and the chats that existed when it settled there. */
export type Pin = { chat: string; known: Set<string>; jobs: Map<string, boolean> };

/**
 * Which chat a call comes from, for agents that don't say (all but Codex). An agent keeps one acm server
 * across its chats, so "the newest chat" would be wrong as soon as another chat of that agent is written to,
 * such as the worker's when a chat delegates to its own kind. Instead the process remembers its chat:
 *
 * - a chat acm started for a job stays the process's chat;
 * - a chat the user started moves only to a newer chat the user started after it (a /clear or new chat);
 * - with no chat yet, a delegated process takes the newest job chat and the user's process the newest chat
 *   that isn't one. `delegated` is null for agents that hide acm's environment variable (Cursor): newest wins.
 *
 * Two chats of one agent that the user runs side by side in one repo can still share a session.
 */
export function currentChat(
  harness: string,
  repoRoot: string,
  roots: Roots,
  pin: Pin | undefined,
  delegated: boolean | null,
): Pin | null {
  const base = rootOf(harness, roots);
  if (!existsSync(base)) return null;
  const reader = READERS[harness];
  const all = reader
    .chats(base, repoRoot)
    .sort((a, b) => b.mtime - a.mtime)
    .map((c) => ({ ...c, id: reader.nativeId(c.path) }));
  if (!all.length) return null;
  const jobs = pin?.jobs ?? new Map<string, boolean>();
  const isJob = (c: { id: string; path: string }) => {
    if (!jobs.has(c.id)) jobs.set(c.id, opening(harness, c.path).job !== null);
    return jobs.get(c.id) as boolean;
  };
  const settle = (chat: string): Pin => ({ chat, known: new Set(all.map((c) => c.id)), jobs });
  const mine = pin && all.find((c) => c.id === pin.chat);
  if (pin && mine) {
    if (isJob(mine)) return pin;
    const next = all.find((c) => c.mtime > mine.mtime && !pin.known.has(c.id) && !isJob(c));
    return next ? settle(next.id) : pin;
  }
  const pick = delegated === true ? all.find(isJob) : delegated === false ? all.find((c) => !isJob(c)) : undefined;
  return settle((pick ?? all[0]).id);
}

export function resume(
  db: Db,
  s: Session,
  opts: { source?: string; chat?: string; limit?: number; budget?: number; roots?: Roots } = {},
) {
  const { source, chat, limit = 30, budget = 12_000, roots = {} } = opts;
  if (source !== undefined && !(source in READERS)) {
    throw new AcmError("invalid", `source must be one of ${HARNESSES.join(", ")}`);
  }
  // Without a chat id, this chat itself is the newest of its kind; leave it out.
  const unknownSelf = s.chat.startsWith("proc:");
  if (source === s.harness && !chat && unknownSelf) {
    throw new AcmError(
      "invalid",
      "your own chat would be in the list; to resume another chat of your own agent, pass chat (from chats)",
    );
  }
  const kinds = source ? [source] : HARNESSES.filter((k) => chat || k !== s.harness || !unknownSelf);
  const listed = listing(kinds, s.root, roots).filter(
    (i) => !(i.harness === s.harness && READERS[i.harness].nativeId(i.path) === s.chat),
  );
  const inRepo = listed.filter((i) => within(i.workspace, s.root));
  let hit: Item | undefined;
  if (chat) {
    hit = listed.find((i) => READERS[i.harness].nativeId(i.path) === chat);
    if (!hit) throw new AcmError("not_found", `no chat ${chat} in this repo; call chats to list them`);
  } else {
    // The user's own chats in the repo folder; chats acm started for jobs don't count.
    // Only "exactly one?" matters, so stop reading at the second.
    const mine: Item[] = [];
    for (const i of inRepo) {
      if (opening(i.harness, i.path).job === null && mine.push(i) === 2) break;
    }
    if (mine.length === 1 || listed.length === 1) hit = mine[0] ?? listed[0];
    else if (listed.length) {
      const entries = listed.slice(0, SCAN).map((i) => entry(db, s, i));
      const above = (e: { folder: string }) => (within(e.folder, s.root) ? 0 : 1);
      entries.sort((a, b) => above(a) - above(b) || Number(a.job !== null) - Number(b.job !== null));
      return {
        choose: entries.slice(0, CHOICES),
        more: Math.max(0, listed.length - CHOICES),
        next: "Show the user these chats (agent, updated, folder, thread, first message, and whether acm started it as a job) and ask which to continue. Then call resume with that chat id. Don't pick one yourself; if more is above 0, chats lists older ones.",
      };
    } else {
      throw new AcmError("not_found", `no ${source ?? "agent"} chat found for this repo`);
    }
  }
  const raw = chatBytes(hit.harness, hit.path);
  const native = READERS[hit.harness].nativeId(hit.path);
  const { records, unknown } = parse(hit.harness, raw, 0, raw.length);
  const kept: { role: string; text: string }[] = [];
  let used = 0;
  let clipped = 0;
  for (const rec of records.slice(-limit).reverse()) {
    const body = rec.text.length > budget ? clip(rec.text, budget) : rec.text;
    used += body.length;
    if (kept.length && used > budget) break;
    if (body !== rec.text) clipped += 1;
    kept.push({ role: rec.role, text: body });
  }
  kept.reverse();
  // Continuing a chat continues its thread; a chat that never used acm starts one named after it.
  const thread = chatThread(db, s, hit.harness, native, () => raw);
  if (thread) joinThread(db, s, thread);
  else {
    s.thread_id = null;
    const started = ensureThread(db, s, opening(hit.harness, raw).first || `continued from ${hit.harness}`);
    // Record the old chat as on that thread too, so the next chat that resumes it lands here as well.
    const old = sessionFor(db, { harness: hit.harness, chat: native, folder: s.root });
    db.prepare("UPDATE sessions SET thread_id = ? WHERE id = ?").run(started, old.id);
  }
  const out: Json = {
    thread: s.thread_id,
    from: hit.harness,
    chat: native,
    folder: hit.workspace,
    messages: kept,
    omitted_messages: records.length - kept.length,
    clipped_messages: clipped,
  };
  if (!records.length && unknown) out.diagnostic = "unrecognized records";
  return out;
}
