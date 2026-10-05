import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, realpathSync, rmSync, utimesSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { DatabaseSync } from "node:sqlite";
import { afterEach, beforeEach, test } from "node:test";
import { connect, type Db } from "../src/db.ts";
import { context, noteAdd, sessionFor } from "../src/memory.ts";
import { dashes, slug } from "../src/readers/index.ts";
import { opencode } from "../src/readers/opencode.ts";
import { chats, currentChat, resume } from "../src/transcript.ts";

let dir: string;
let db: Db;
let repo: string;
let root: string;

function gitRepo(path: string): string {
  mkdirSync(path, { recursive: true });
  execFileSync("git", ["-C", path, "init", "-q"]);
  return realpathSync.native(path);
}

function write(path: string, ...lines: unknown[]): string {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, lines.map((l) => `${typeof l === "string" ? l : JSON.stringify(l)}\n`).join(""));
  return path;
}

const cursorUser = (text: string) => ({ role: "user", message: { content: [{ type: "text", text }] } });
const cursorReply = (text: string) => ({ role: "assistant", message: { content: [{ type: "text", text }] } });
const codexMsg = (role: string, text: string) => ({
  type: "response_item",
  payload: { type: "message", role, content: [{ type: role === "user" ? "input_text" : "output_text", text }] },
});
const session = (harness: string, chat: string, folder = repo) => sessionFor(db, { harness, chat, folder });
const cursorChat = (folder: string, id: string, ...lines: unknown[]) =>
  write(join(root, "cursor", folder, "agent-transcripts", id, `${id}.jsonl`), ...lines);
const roots = () => ({
  cursor: join(root, "cursor"),
  codex: join(root, "codex"),
  claude: join(root, "claude"),
  opencode: join(root, "opencode"),
});

beforeEach(() => {
  dir = mkdtempSync(join(tmpdir(), "acm-"));
  db = connect(join(dir, "home"));
  repo = gitRepo(join(dir, "repo"));
  root = join(dir, "transcripts");
});

afterEach(() => {
  db.close();
  rmSync(dir, { recursive: true, force: true, maxRetries: 5, retryDelay: 50 });
});

test("resume reads each agent's newest chat and continues its thread", () => {
  // A Cursor chat opened in the folder above the repo, whose session worked on a thread.
  const parent = slug(dirname(repo));
  cursorChat(parent, "c1", cursorUser("pick a city"), cursorReply("Lisbon"));
  const owner = session("cursor", "c1");
  noteAdd(db, owner, { text: "the trip is Lisbon" });
  const got = resume(db, session("codex", "x1"), { source: "cursor", roots: roots() });
  assert.deepEqual(
    (got.messages as { text: string }[]).map((m) => m.text),
    ["pick a city", "Lisbon"],
  );
  assert.equal(got.folder, dirname(repo));
  assert.equal(got.thread, db.prepare("SELECT thread_id FROM sessions WHERE id = ?").get(owner.id)?.thread_id);

  write(
    join(root, "codex", "2026", "rollout-x.jsonl"),
    { type: "session_meta", payload: { session_id: "cx", cwd: repo } },
    codexMsg("user", "plan it"),
  );
  const fresh = resume(db, session("claude", "x2"), { source: "codex", roots: roots() });
  assert.notEqual(fresh.thread, got.thread);
  assert.equal(db.prepare("SELECT name FROM threads WHERE id = ?").get(fresh.thread as string)?.name, "plan it");

  write(join(root, "claude", dashes(repo), "s1.jsonl"), {
    type: "user",
    sessionId: "s1",
    message: { role: "user", content: "hi" },
  });
  const back = resume(db, session("cursor", "x3"), { source: "claude", roots: roots() });
  assert.deepEqual(back.messages, [{ role: "user", text: "hi" }]);
});

test("a chat whose id is known leaves itself out, so its own kind can be resumed", () => {
  cursorChat(slug(repo), "c1", cursorUser("first chat"));
  cursorChat(slug(repo), "c2", cursorUser("this chat"));
  const got = resume(db, session("cursor", "c2"), { source: "cursor", roots: roots() });
  assert.equal(got.chat, "c1");
  assert.throws(() => resume(db, session("cursor", "proc:1"), { source: "cursor", roots: roots() }), /own chat/);
});

test("with several chats the user chooses; the user's own come before job chats", () => {
  const mine = cursorChat(slug(repo), "c1", cursorUser("plan the trip"));
  cursorChat(slug(repo), "c2", cursorUser("[acm job j_0123456789ab] A codex chat asked for this"));
  const older = cursorChat(slug(repo), "c3", cursorUser("pack bags"));
  utimesSync(mine, 1000, 1000);
  utimesSync(older, 500, 500);
  const listed = chats(db, session("codex", "x"), 20, roots()).chats;
  assert.deepEqual(
    listed.map((c) => [c.chat, c.job]),
    [
      ["c2", "j_0123456789ab"],
      ["c1", null],
      ["c3", null],
    ],
  );
  const asked = resume(db, session("codex", "x"), { roots: roots() });
  assert.deepEqual(
    (asked.choose as { chat: string }[]).map((c) => c.chat),
    ["c1", "c3", "c2"],
  );
  const picked = resume(db, session("codex", "x"), { chat: "c1", roots: roots() });
  assert.equal(picked.chat, "c1");
  assert.throws(() => resume(db, session("codex", "x"), { chat: "nope", roots: roots() }), /no chat nope/);
});

test("the user's one chat is resumed over job chats, even when a client note comes before the job tag", () => {
  cursorChat(slug(repo), "c1", cursorUser("plan the trip"));
  cursorChat(slug(repo), "j1", cursorUser("[acm job j_0123456789ab] A codex chat asked"));
  cursorChat(slug(repo), "j2", cursorUser("Note: The user opened the file x.md. [acm job j_ba9876543210] asked"));
  assert.equal(resume(db, session("codex", "x"), { roots: roots() }).chat, "c1");
});

test("the one chat in the repo wins over chats in a folder above; long messages are clipped", () => {
  cursorChat(slug(repo), "c1", cursorUser("x".repeat(30_000)), cursorUser("y".repeat(2_000)));
  cursorChat(slug(dirname(repo)), "c2", cursorUser("home chat"));
  const got = resume(db, session("codex", "x"), { roots: roots() });
  assert.equal(got.chat, "c1");
  assert.equal(got.omitted_messages, 1);

  const huge = `start ${"x".repeat(50_000)} end`;
  const odd = gitRepo(join(dir, "my_app.v2"));
  cursorChat(dashes(odd).replace(/^-+/, ""), "c9", cursorUser(huge));
  const clipped = resume(db, sessionFor(db, { harness: "codex", chat: "y", folder: odd }), {
    source: "cursor",
    budget: 1_000,
    roots: roots(),
  });
  const text = (clipped.messages as { text: string }[])[0].text;
  assert.equal(clipped.clipped_messages, 1);
  assert.ok(
    text.length < 1_100 && text.startsWith("start ") && text.endsWith(" end") && text.includes("characters cut"),
  );
});

test("Claude chats in dotted folders, with images, resume twice onto the same thread", () => {
  const dotted = gitRepo(join(dir, "my.app_x"));
  const image = { type: "image", source: { type: "base64", media_type: "image/png", data: "x" } };
  write(join(root, "claude", dashes(dotted), "s1.jsonl"), {
    type: "user",
    sessionId: "s1",
    message: { role: "user", content: [image, { type: "text", text: "fix this screen" }] },
  });
  const first = resume(db, sessionFor(db, { harness: "cursor", chat: "a", folder: dotted }), {
    source: "claude",
    roots: roots(),
  });
  assert.deepEqual(first.messages, [{ role: "user", text: "fix this screen" }]);
  const a = sessionFor(db, { harness: "cursor", chat: "a", folder: dotted });
  context(db, a, { done: true });
  const again = resume(db, sessionFor(db, { harness: "codex", chat: "b", folder: dotted }), {
    source: "claude",
    roots: roots(),
  });
  assert.equal(again.thread, first.thread);
});

test("Claude Code's command wrappers never become a chat's first message or thread name", () => {
  write(
    join(root, "claude", dashes(repo), "s1.jsonl"),
    {
      type: "user",
      sessionId: "s1",
      message: {
        role: "user",
        content:
          "<local-command-caveat>The command below was run directly in Claude Code</local-command-caveat><command-name>/clear</command-name>",
      },
    },
    { type: "user", sessionId: "s1", message: { role: "user", content: "rename the cart helpers" } },
  );
  const got = resume(db, session("codex", "x"), { source: "claude", roots: roots() });
  assert.equal(
    db.prepare("SELECT name FROM threads WHERE id = ?").get(got.thread as string)?.name,
    "rename the cart helpers",
  );
  assert.equal(chats(db, session("codex", "x"), 5, roots()).chats[0].first, "rename the cart helpers");
});

test("OpenCode chats from old files and SQLite, newest first", () => {
  const base = join(root, "opencode");
  const old = write(join(base, "storage", "session", "proj", "ses_old.json"), { id: "ses_old", directory: repo });
  write(join(base, "storage", "message", "ses_old", "m1.json"), { id: "m1", role: "user" });
  write(join(base, "storage", "part", "m1", "p1.json"), { type: "text", text: "from files" });
  utimesSync(old, 1000, 1000);
  const db2 = new DatabaseSync(join(base, "opencode.db"));
  db2.exec(`CREATE TABLE session (id TEXT, directory TEXT, time_updated INTEGER, parent_id TEXT);
    CREATE TABLE message (id TEXT, session_id TEXT, time_created INTEGER, data TEXT);
    CREATE TABLE part (id TEXT, message_id TEXT, time_created INTEGER, data TEXT);`);
  db2.prepare("INSERT INTO session VALUES ('ses_new', ?, ?, NULL)").run(repo, 1_010_000);
  db2.prepare("INSERT INTO message VALUES ('m2', 'ses_new', 2, ?)").run(JSON.stringify({ role: "user" }));
  db2.prepare("INSERT INTO part VALUES ('p2', 'm2', 2, ?)").run(JSON.stringify({ type: "text", text: "from sqlite" }));
  const asked = resume(db, session("cursor", "x"), { source: "opencode", roots: roots() });
  assert.deepEqual(
    (asked.choose as { chat: string }[]).map((c) => c.chat),
    ["ses_new", "ses_old"],
  );
  const got = resume(db, session("cursor", "x"), { source: "opencode", chat: "ses_new", roots: roots() });
  assert.deepEqual(
    (got.messages as { text: string }[]).map((m) => m.text),
    ["from sqlite"],
  );
  db2.prepare("INSERT INTO session VALUES ('ses_old', ?, ?, NULL)").run(repo, 1_020_000);
  db2.close();
  const reordered = resume(db, session("cursor", "x"), { source: "opencode", roots: roots() });
  assert.deepEqual(
    (reordered.choose as { chat: string }[]).map((c) => c.chat),
    ["ses_old", "ses_new"],
  );
});

test("an OpenCode turn ends only after a finished reply", () => {
  const base = join(root, "oc");
  const sess = write(join(base, "session", "ses_1.json"), { id: "ses_1", directory: "/w" });
  const msgs: [string, object, string][] = [
    ["m1", { role: "user", time: { created: 1 } }, "go"],
    ["m2", { role: "assistant", finish: "tool-calls", time: { created: 2, completed: 3 } }, "reading"],
    ["m3", { role: "assistant", finish: "stop", time: { created: 4 } }, "still writing"],
  ];
  for (const [id, msg, text] of msgs) {
    write(join(base, "message", "ses_1", `${id}.json`), { id, ...msg });
    write(join(base, "part", id, "p.json"), { type: "text", text });
  }
  assert.ok(!opencode.read?.(sess).includes("turn_ended"));
  write(join(base, "message", "ses_1", "m3.json"), {
    id: "m3",
    role: "assistant",
    finish: "stop",
    time: { created: 4, completed: 5 },
  });
  assert.equal(opencode.read?.(sess).toString().split("turn_ended").length, 2);
});

test("recent messages survive a huge tool output before them", () => {
  write(
    join(root, "codex", "2026", "rollout-large.jsonl"),
    { type: "session_meta", payload: { session_id: "cx", cwd: repo } },
    codexMsg("user", "install grill-me"),
    codexMsg("assistant", "Installed grill-me"),
    { type: "response_item", payload: { type: "function_call_output", output: "x".repeat(1_100_000) } },
    codexMsg("user", "what happened?"),
  );
  const got = resume(db, session("cursor", "x"), { source: "codex", roots: roots() });
  assert.deepEqual(
    (got.messages as { text: string }[]).map((m) => m.text),
    ["install grill-me", "Installed grill-me", "what happened?"],
  );
  assert.equal(got.omitted_messages, 0);
});

test("Codex's own review subagents and internal context blocks are not the user's chats", () => {
  write(
    join(root, "codex", "2026", "rollout-guardian.jsonl"),
    {
      type: "session_meta",
      payload: {
        session_id: "g1",
        cwd: repo,
        source: { subagent: { other: "guardian" } },
        thread_source: "guardian_review",
      },
    },
    codexMsg("user", "The following is the Codex agent history whose request action you are assessing"),
  );
  write(
    join(root, "codex", "2026", "rollout-user.jsonl"),
    { type: "session_meta", payload: { session_id: "u1", cwd: repo, source: "cli", thread_source: "user" } },
    codexMsg("user", '<codex_internal_context source="goal">Continue working toward the goal</codex_internal_context>'),
    codexMsg("user", "ship the cart fix"),
  );
  const listed = chats(db, session("claude", "x"), 10, roots()).chats;
  assert.deepEqual(
    listed.map((c) => [c.chat, c.first]),
    [["u1", "ship the cart fix"]],
  );
});

test("a process keeps its chat when a worker's chat is newer, and moves only to a new chat the user started", () => {
  const r = roots();
  const mine = cursorChat(slug(repo), "mine", cursorUser("plan the trip"));
  utimesSync(mine, 1000, 1000);
  // The caller's process settles on its chat.
  let caller = currentChat("cursor", repo, r, undefined, null);
  assert.equal(caller?.chat, "mine");
  // It delegates to its own kind: the worker's chat appears and is newer. The caller stays where it is.
  const job = cursorChat(slug(repo), "job", cursorUser("[acm job j_0123456789ab] A cursor chat asked for this"));
  utimesSync(job, 2000, 2000);
  caller = currentChat("cursor", repo, r, caller ?? undefined, null);
  assert.equal(caller?.chat, "mine");
  // The worker's process: with no chat yet it takes the job chat, and stays there when the caller's is newer.
  utimesSync(mine, 3000, 3000);
  let worker = currentChat("cursor", repo, r, undefined, true);
  assert.equal(worker?.chat, "job");
  worker = currentChat("cursor", repo, r, worker ?? undefined, true);
  assert.equal(worker?.chat, "job");
  // A user's process starting while a job chat is the newest takes the newest chat that isn't a job.
  utimesSync(job, 4000, 4000);
  assert.equal(currentChat("cursor", repo, r, undefined, false)?.chat, "mine");
  // The user starts a new chat in the caller's window (/clear): the caller moves to it.
  const fresh = cursorChat(slug(repo), "fresh", cursorUser("something new"));
  utimesSync(fresh, 5000, 5000);
  caller = currentChat("cursor", repo, r, caller ?? undefined, null);
  assert.equal(caller?.chat, "fresh");
  // A chat that already existed doesn't pull it back, however recently it was written.
  utimesSync(mine, 6000, 6000);
  assert.equal(currentChat("cursor", repo, r, caller ?? undefined, null)?.chat, "fresh");
  assert.equal(currentChat("codex", repo, r, undefined, null), null);
});

test("listing chats and finding the user's one chat read only the start of each file", () => {
  // A first message past the part that is read doesn't count; one inside it does, whatever follows it.
  cursorChat(slug(repo), "big", cursorUser("the question"), cursorReply("x".repeat(600_000)), cursorUser("later"));
  const listed = chats(db, session("codex", "x"), 5, roots()).chats;
  assert.equal(listed[0].first, "the question");
  assert.equal(resume(db, session("codex", "x"), { roots: roots() }).chat, "big");
});
