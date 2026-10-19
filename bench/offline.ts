/**
 * Offline checks of ACM's memory, with no agent and no network: how much of a chat a handoff carries, whether a
 * saved note is found again, whether a contradicting note is pointed out, whether a note goes stale when its file
 * changes, and what ACM costs in tokens. The notes are bench/notes.json, written by a model that never saw ACM's code.
 *
 * usage: node bench/offline.ts [--out bench/results/offline.json]
 */
import { spawn } from "node:child_process";
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  realpathSync,
  rmSync,
  unlinkSync,
  utimesSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { createInterface } from "node:readline";
import { parseArgs } from "node:util";
import { connect, type Db } from "../src/db.ts";
import { context, noteAdd, noteSearch, sessionFor } from "../src/memory.ts";
import { dashes, slug } from "../src/readers/index.ts";
import { resume } from "../src/transcript.ts";

const CLI = join(import.meta.dirname, "..", "src", "cli.ts");
const FORMATS = ["codex", "claude", "cursor", "opencode"];

const { values: opt } = parseArgs({
  options: { out: { type: "string", default: join(import.meta.dirname, "results", "offline.json") } },
});

type Entry = {
  id: string;
  text: string;
  keyword_query: string;
  question_query: string;
  update: string;
  related: string;
};
const entries: Entry[] = JSON.parse(readFileSync(join(import.meta.dirname, "notes.json"), "utf8")).notes;

const scratch = mkdtempSync(join(tmpdir(), "acm-offline-"));
let made = 0;

/** A fresh ACM database and project folder. */
function project() {
  const dir = join(scratch, String(made++));
  const repo = join(dir, "repo");
  mkdirSync(repo, { recursive: true });
  const db: Db = connect(join(dir, "home"));
  const root = realpathSync.native(repo);
  return { dir, repo: root, db, chat: (id: string) => sessionFor(db, { harness: "codex", chat: id, folder: root }) };
}

function write(path: string, body: string): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, body);
}

const jsonl = (rows: unknown[]) => rows.map((r) => `${JSON.stringify(r)}\n`).join("");

/** A chat as each agent stores it. */
function writeChat(base: string, format: string, repo: string, messages: { role: string; text: string }[]): void {
  const id = "c0ffee00-0000-4000-8000-000000000001";
  if (format === "codex") {
    write(
      join(base, "codex", "2026", "10", "01", `rollout-2026-10-01T00-00-00-${id}.jsonl`),
      jsonl([
        { type: "session_meta", payload: { session_id: id, cwd: repo, source: "cli", thread_source: "user" } },
        ...messages.map((m) => ({
          type: "response_item",
          payload: {
            type: "message",
            role: m.role,
            content: [{ type: m.role === "user" ? "input_text" : "output_text", text: m.text }],
          },
        })),
      ]),
    );
  } else if (format === "claude") {
    write(
      join(base, "claude", dashes(repo), `${id}.jsonl`),
      jsonl(messages.map((m) => ({ type: m.role, sessionId: id, message: { role: m.role, content: m.text } }))),
    );
  } else if (format === "cursor") {
    write(
      join(base, "cursor", slug(repo), "agent-transcripts", id, `${id}.jsonl`),
      jsonl(messages.map((m) => ({ role: m.role, message: { content: [{ type: "text", text: m.text }] } }))),
    );
  } else {
    const store = join(base, "opencode", "storage");
    write(join(store, "session", "proj", `${id}.json`), JSON.stringify({ id, directory: repo }));
    messages.forEach((m, i) => {
      write(
        join(store, "message", id, `m${i}.json`),
        JSON.stringify({ id: `m${i}`, role: m.role, time: { created: i + 1 } }),
      );
      write(join(store, "part", `m${i}`, "p.json"), JSON.stringify({ type: "text", text: m.text }));
    });
  }
}

// ---- 1. handoff ----

const SENTENCE = "We looked at the options again and kept the plan, with small changes to names and tests. ";

/** Which of three requests in a chat (the opening one, one midway, the latest) a resume from another agent carries. */
function handoff() {
  const rows = [];
  for (const sentences of [4, 20]) {
    for (const length of [10, 40, 160]) {
      const kept = { opening: 0, middle: 0, latest: 0 };
      for (const format of FORMATS) {
        const p = project();
        const messages = Array.from({ length }, (_, i) => ({
          role: i % 2 ? "assistant" : "user",
          text: SENTENCE.repeat(sentences),
        }));
        const asks = messages.flatMap((m, i) => (m.role === "user" ? [i] : []));
        const at = { opening: asks[0], middle: asks[Math.floor(asks.length / 2)], latest: asks[asks.length - 1] };
        for (const [name, i] of Object.entries(at)) messages[i].text = `FACT-${name} ${messages[i].text}`;
        const chats = join(p.dir, "chats");
        writeChat(chats, format, p.repo, messages);
        const roots = Object.fromEntries(FORMATS.map((f) => [f, join(chats, f)]));
        const reader = sessionFor(p.db, {
          harness: format === "codex" ? "claude" : "codex",
          chat: "x",
          folder: p.repo,
        });
        const carried = JSON.stringify(resume(p.db, reader, { source: format, roots })); // all the agent sees
        for (const name of Object.keys(kept) as (keyof typeof kept)[])
          if (carried.includes(`FACT-${name}`)) kept[name] += 1;
        p.db.close();
      }
      rows.push({ messages: length, chars_each: SENTENCE.length * sentences, ...kept });
    }
  }
  return rows;
}

// ---- 2. finding notes ----

function addAll(p: ReturnType<typeof project>): Map<string, string> {
  const writer = p.chat("writer");
  return new Map(entries.map((e) => [e.id, String(noteAdd(p.db, writer, { text: e.text, tier: "long" }).id)]));
}

/** How often a note is in the top 3 results for the words an agent would search with. */
function search() {
  const p = project();
  const ids = addAll(p);
  const reader = p.chat("reader");
  const found = (query: string, id: string) =>
    noteSearch(p.db, reader, query)
      .notes.slice(0, 3)
      .some((n) => n.id === ids.get(id));
  const out = {
    notes: entries.length,
    keywords: entries.filter((e) => found(e.keyword_query, e.id)).length,
    questions: entries.filter((e) => found(e.question_query, e.id)).length,
  };
  p.db.close();
  return out;
}

// ---- 3. contradictions ----

/** Whether note_add points out the note a later note makes false, and how many unrelated notes it shows with it. */
function contradictions() {
  let caught = 0;
  let others = 0;
  let related = 0;
  for (const e of entries) {
    for (const kind of ["update", "related"] as const) {
      const p = project();
      const ids = addAll(p);
      const check = (
        (noteAdd(p.db, p.chat("later"), { text: e[kind], tier: "long" }).check ?? []) as { id: string }[]
      ).map((n) => n.id);
      const target = ids.get(e.id) as string;
      if (kind === "related") related += Number(check.includes(target));
      else {
        caught += Number(check.includes(target));
        others += check.filter((id) => id !== target).length;
      }
      p.db.close();
    }
  }
  return { notes: entries.length, caught, unrelated_shown: others, related_shown: related };
}

// ---- 4. stale notes ----

const MENTIONS: Record<string, (root: string) => string> = {
  "src/db/pool.ts": () => "src/db/pool.ts",
  "./src/db/pool.ts": () => "./src/db/pool.ts",
  "`src/db/pool.ts`": () => "`src/db/pool.ts`",
  "src/db/pool.ts:42": () => "src/db/pool.ts:42",
  "absolute path": (root) => join(root, "src", "db", "pool.ts"),
  "pool.ts (file name only)": () => "pool.ts",
};

/** Whether context marks a note stale when the file it mentions is edited or deleted, and not when only touched. */
function stale() {
  return Object.entries(MENTIONS).map(([style, mention]) => {
    const row: Record<string, string | boolean> = { mention: style };
    for (const change of ["edited", "deleted", "touched"]) {
      const p = project();
      const file = join(p.repo, "src", "db", "pool.ts");
      write(file, "export const MAX = 20;\n");
      const note = noteAdd(p.db, p.chat("writer"), {
        text: `The pool size is set in ${mention(p.repo)}; keep it at 20.`,
      });
      if (change === "edited") writeFileSync(file, "export const MAX = 50;\n");
      if (change === "deleted") unlinkSync(file);
      if (change === "touched") utimesSync(file, new Date(Date.now() + 60_000), new Date(Date.now() + 60_000));
      const marked = (context(p.db, p.chat("reader")).stale ?? []) as { id: string }[];
      row[change] = marked.some((s) => s.id === note.id);
      p.db.close();
    }
    return row;
  });
}

// ---- 5. tokens ----

/** Characters of ACM's tool names, descriptions and schemas, as an agent's tools/list returns them. */
async function schemas(): Promise<number> {
  const child = spawn(process.execPath, [CLI, "mcp", "--harness", "codex"], {
    env: { ...process.env, ACM_HOME: join(scratch, "schemas") },
    stdio: ["pipe", "pipe", "ignore"],
  });
  const send = (msg: object) => child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", ...msg })}\n`);
  const tools = await new Promise<{ name: string; description: string; inputSchema: unknown }[]>((resolve) => {
    createInterface({ input: child.stdout }).on("line", (line) => {
      const msg = JSON.parse(line);
      if (msg.id === 1) {
        send({ method: "notifications/initialized" });
        send({ id: 2, method: "tools/list" });
      }
      if (msg.id === 2) resolve(msg.result.tools);
    });
    send({
      id: 1,
      method: "initialize",
      params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "bench", version: "1" } },
    });
  });
  child.kill();
  return JSON.stringify(tools.map((t) => ({ name: t.name, description: t.description, inputSchema: t.inputSchema })))
    .length;
}

/** Characters of a chat's first context call, and of a later one with nothing new, as long notes pile up. */
function contextSize() {
  return [0, 10, 40, 160].map((count) => {
    const p = project();
    const writer = p.chat("writer");
    for (let i = 0; i < count; i++) {
      const e = entries[i % entries.length];
      const copy = Math.floor(i / entries.length);
      noteAdd(p.db, writer, { text: copy ? `${e.text} (${copy + 1})` : e.text, tier: "long" });
    }
    const reader = p.chat("reader");
    const first = JSON.stringify(context(p.db, reader)).length;
    const later = JSON.stringify(context(p.db, reader)).length;
    p.db.close();
    return { long_notes: count, first, later };
  });
}

// ---- report ----

const tokens = (chars: number) =>
  `${chars.toLocaleString("en")} chars (≈${Math.round(chars / 4).toLocaleString("en")} tokens)`;
const pct = (k: number, n: number) => `${k}/${n} (${Math.round((100 * k) / n)}%)`;
const yes = (b: unknown) => (b ? "yes" : "no");

const result = {
  date: new Date().toISOString(),
  handoff: handoff(),
  search: search(),
  contradictions: contradictions(),
  stale: stale(),
  schema_chars: await schemas(),
  context: contextSize(),
};
rmSync(scratch, { recursive: true, force: true, maxRetries: 5, retryDelay: 50 });
mkdirSync(dirname(opt.out), { recursive: true });
writeFileSync(opt.out, `${JSON.stringify(result, null, 1)}\n`);

const n = FORMATS.length;
const c = result.contradictions;
console.log(
  [
    "### Handoff: which requests a resume carries (out of 4 chat formats)",
    "",
    "| Chat length | Opening request | Request midway | Latest request |",
    "|---|---|---|---|",
    ...result.handoff.map(
      (r) =>
        `| ${r.messages} messages of ${r.chars_each} chars | ${r.opening}/${n} | ${r.middle}/${n} | ${r.latest}/${n} |`,
    ),
    "",
    "### Notes",
    "",
    "| Measure | Result |",
    "|---|---|",
    `| Note found in the top 3, keyword search | ${pct(result.search.keywords, result.search.notes)} |`,
    `| Note found in the top 3, question search | ${pct(result.search.questions, result.search.notes)} |`,
    `| Contradicted note pointed out on note_add | ${pct(c.caught, c.notes)} |`,
    `| Unrelated notes shown with it, per note_add | ${(c.unrelated_shown / c.notes).toFixed(2)} |`,
    `| Same-topic, compatible note pointed out | ${pct(c.related_shown, c.notes)} |`,
    "",
    "### Stale notes: is the note marked when its file changes?",
    "",
    "| Mention in the note | File edited | File deleted | Only touched (should be no) |",
    "|---|---|---|---|",
    ...result.stale.map((r) => `| ${r.mention} | ${yes(r.edited)} | ${yes(r.deleted)} | ${yes(r.touched)} |`),
    "",
    "### Tokens",
    "",
    `Tool names, descriptions, and schemas: ${tokens(result.schema_chars)}, in every chat.`,
    "",
    "| Long notes in the project | First context | Later context, nothing new |",
    "|---|---|---|",
    ...result.context.map((r) => `| ${r.long_notes} | ${tokens(r.first)} | ${tokens(r.later)} |`),
  ].join("\n"),
);
