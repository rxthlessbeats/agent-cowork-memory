import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { connect, type Db } from "../src/db.ts";
import { claim, context, noteAdd, noteSearch, relPath, type Session, sessionFor, sweep } from "../src/memory.ts";
import { projectRoot } from "../src/project.ts";

let dir: string;
let db: Db;
let repo: string;

function git(cwd: string, ...args: string[]) {
  execFileSync("git", ["-C", cwd, ...args], { stdio: "ignore" });
}

function gitRepo(path: string): string {
  mkdirSync(path, { recursive: true });
  git(path, "init", "-q");
  git(path, "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init");
  return realpathSync.native(path);
}

function chat(harness: string, id: string, folder = repo): Session {
  return sessionFor(db, { harness, chat: id, folder });
}

function ago(days: number): string {
  return `${new Date(Date.now() - days * 86_400_000).toISOString().slice(0, 19)}Z`;
}

beforeEach(() => {
  dir = mkdtempSync(join(tmpdir(), "acm-"));
  db = connect(join(dir, "home"));
  repo = gitRepo(join(dir, "repo"));
});

afterEach(() => {
  db.close();
  rmSync(dir, { recursive: true, force: true, maxRetries: 5, retryDelay: 50 });
});

describe("projects and sessions", () => {
  test("one chat is one session; another chat is another", () => {
    const a = chat("claude", "c1");
    assert.equal(chat("claude", "c1").id, a.id);
    assert.notEqual(chat("claude", "c2").id, a.id);
    assert.notEqual(chat("codex", "c1").id, a.id);
  });

  test("a project is the repo's top folder, from a subfolder, a plain folder, or a worktree", () => {
    mkdirSync(join(repo, "sub"));
    assert.equal(projectRoot(join(repo, "sub")), repo);
    const plain = join(dir, "plain");
    mkdirSync(plain);
    assert.equal(projectRoot(plain), realpathSync.native(plain));
    git(repo, "worktree", "add", "-q", join(dir, "wt"));
    assert.equal(projectRoot(join(dir, "wt")), repo);
    assert.equal(chat("claude", "x", join(dir, "wt")).project_id, chat("codex", "y").project_id);
  });
});

describe("threads", () => {
  test("a first note starts a thread; another chat sees it open and joins by choice", () => {
    const a = chat("claude", "a");
    const added = noteAdd(db, a, { text: "checkout flake: the seed insert isn't awaited" });
    const b = chat("codex", "b");
    const seen = context(db, b);
    assert.equal(seen.thread, undefined);
    assert.ok(seen.thread_next);
    assert.deepEqual(
      (seen.open_threads as { id: string }[]).map((t) => t.id),
      [added.thread],
    );
    const joined = context(db, b, { thread: added.thread as string });
    assert.equal((joined.thread as { id: string }).id, added.thread);
    assert.match((joined.timeline as string[]).at(-1) ?? "", /codex joined/);
  });

  test("done closes the thread; joining it again reopens it", () => {
    const a = chat("claude", "a");
    const { thread } = noteAdd(db, a, { text: "migrate to node 24" });
    context(db, a, { done: true });
    assert.equal(context(db, chat("codex", "b")).open_threads, undefined);
    const again = context(db, chat("cursor", "c"), { thread: thread as string });
    assert.equal((again.thread as { status: string }).status, "open");
  });

  test("new work on a done thread reopens it: a note, or a chat already on it joining again", () => {
    const a = chat("claude", "a");
    const { thread } = noteAdd(db, a, { text: "migrate to node 24" });
    const openFor = (id: string) => (context(db, chat("codex", id)).open_threads as { id: string }[] | undefined) ?? [];
    context(db, a, { done: true });
    assert.deepEqual(openFor("b1"), []);
    noteAdd(db, chat("claude", "a"), { text: "one more thing about node 24" });
    assert.deepEqual(
      openFor("b2").map((t) => t.id),
      [thread],
    );
    context(db, chat("claude", "a"), { done: true });
    context(db, chat("claude", "a"), { thread: thread as string }); // already on it: still reopens
    assert.equal(openFor("b3").length, 1);
    assert.ok(
      (context(db, chat("codex", "b4"), { thread: thread as string }).timeline as string[]).some((l) =>
        /reopened/.test(l),
      ),
    );
  });

  test("an unknown thread is refused", () => {
    assert.throws(() => context(db, chat("claude", "a"), { thread: "t_nope" }), /unknown thread/);
  });
});

describe("context only sends what is new", () => {
  test("a later call with nothing new is small; a new note shows up once", () => {
    const a = chat("claude", "a");
    for (let i = 0; i < 6; i++) noteAdd(db, a, { text: `finding ${i}: ${"detail ".repeat(30)}` });
    noteAdd(db, a, { text: "use pnpm, not npm", tier: "long" });
    const b = chat("codex", "b");
    const first = context(db, b);
    assert.equal((first.notes as unknown[]).length, 6); // the long note plus 5 of the other thread's, one line each
    assert.equal(first.notes_not_shown, 1);
    const later = context(db, b);
    assert.deepEqual(later.notes, []);
    assert.ok(JSON.stringify(later).length < 600, JSON.stringify(later));
    noteAdd(db, a, { text: "the staging db is read-only on Fridays", tier: "long" });
    assert.deepEqual(
      (context(db, b).notes as { body: string }[]).map((n) => n.body),
      ["the staging db is read-only on Fridays"],
    );
  });

  test("this thread's notes come in full, other threads' clipped", () => {
    const a = chat("claude", "a");
    noteAdd(db, a, { text: `mine ${"x".repeat(400)}` });
    noteAdd(db, chat("codex", "b"), { text: `theirs ${"y".repeat(400)}` });
    const bodies = (context(db, a).notes as { body: string }[]).map((n) => n.body);
    assert.equal(bodies.find((b) => b.startsWith("mine"))?.length, 405);
    assert.ok((bodies.find((b) => b.startsWith("theirs"))?.length ?? 999) <= 200);
  });
});

describe("notes stay true", () => {
  test("a replacement is checked against the other notes too", () => {
    const a = chat("claude", "a");
    const never = noteAdd(db, a, { text: "never commit the playground folder", tier: "long" });
    const may = noteAdd(db, a, { text: "the playground folder may be committed now", tier: "long" });
    const again = noteAdd(db, a, {
      text: "never commit the playground folder",
      tier: "long",
      supersedes: never.id as string,
    });
    assert.deepEqual(
      (again.check as { id: string }[]).map((n) => n.id),
      [may.id],
    );
  });

  test("one shared word is not a topic: the check needs two", () => {
    const a = chat("claude", "a");
    noteAdd(db, a, { text: "e2e5: the playground is a scratch folder", tier: "long" });
    assert.equal(
      noteAdd(db, chat("codex", "b"), { text: "e2e5: codex checks threads and delegation" }).check,
      undefined,
    );
    assert.ok(noteAdd(db, chat("codex", "b"), { text: "the playground scratch folder is shared" }).check);
  });

  test("a later context leaves out what this chat wrote itself", () => {
    const a = chat("claude", "a");
    context(db, a);
    noteAdd(db, a, { text: "mine, written after my first context" });
    const later = context(db, a);
    assert.deepEqual(later.notes, []);
    assert.equal(later.timeline, undefined);
    noteAdd(db, chat("codex", "b"), { text: "from codex", tier: "long" });
    assert.deepEqual(
      (context(db, a).notes as { body: string }[]).map((n) => n.body),
      ["from codex"],
    );
  });

  test("writing a note shows notes on the same topic; supersedes replaces one", () => {
    const a = chat("claude", "a");
    const vitest = noteAdd(db, a, { text: "the unit tests run with vitest", tier: "long" });
    const jest = noteAdd(db, chat("codex", "b"), {
      text: "the unit tests run with jest now, not vitest",
      tier: "long",
    });
    assert.deepEqual(
      (jest.check as { id: string }[]).map((n) => n.id),
      [vitest.id],
    );
    assert.ok(jest.next);
    const fixed = noteAdd(db, chat("codex", "b"), {
      text: "the unit tests run with jest now, not vitest",
      tier: "long",
      supersedes: vitest.id as string,
    });
    // The replacement is checked too: the identical earlier note shows up, a duplicate worth knowing about.
    assert.deepEqual(
      (fixed.check as { id: string }[]).map((n) => n.id),
      [jest.id],
    );
    const ids = noteSearch(db, a, "unit tests").notes.map((n) => n.id);
    assert.ok(!ids.includes(vitest.id));
    const timeline = context(db, a).timeline as string[];
    assert.ok(timeline.some((line) => /replaced "the unit tests run with vitest"/.test(line)));
    assert.throws(() => noteAdd(db, a, { text: "x", supersedes: vitest.id as string }), /live note/);
  });

  test("a note goes stale when a file it mentions changes, and re-checking clears it", () => {
    mkdirSync(join(repo, "src"));
    writeFileSync(join(repo, "src", "cart.ts"), "export const v = 1;\n");
    const a = chat("claude", "a");
    const note = noteAdd(db, a, { text: "src/cart.ts keeps prices in cents.", tier: "long" });
    assert.deepEqual(note.files, ["src/cart.ts"]);
    assert.equal(context(db, a).stale, undefined);
    writeFileSync(join(repo, "src", "cart.ts"), "export const v = 2;\n");
    const b = chat("codex", "b");
    assert.deepEqual(context(db, b).stale, [{ id: note.id, files: ["src/cart.ts"] }]);
    noteAdd(db, b, { text: "src/cart.ts keeps prices in cents.", tier: "long", supersedes: note.id as string });
    const after = context(db, b);
    assert.equal(after.stale, undefined);
    assert.ok((context(db, a).timeline as string[]).some((l) => /codex re-checked/.test(l)));
  });
});

describe("search, holds, sweep", () => {
  test("note_search finds notes and job results", () => {
    const a = chat("claude", "a");
    noteAdd(db, a, { text: "rain plan: the Gulbenkian cafe" });
    db.prepare(
      `INSERT INTO jobs (id, project_id, caller_session_id, folder, kind, agent_name, summary, task, prompt, state, result, started_at)
       VALUES ('j_1', ?, ?, ?, 'codex', 'codex-repo', 's', 'find a rainy-day plan', 'p', 'done', 'Booked the museum for rainy days.', '2026-10-02T00:00:00Z')`,
    ).run(a.project_id, a.id, repo);
    db.prepare("INSERT INTO search (ref, project_id, body) VALUES ('j_1', ?, 'Booked the museum for rainy days.')").run(
      a.project_id,
    );
    const found = noteSearch(db, a, "rain");
    assert.equal(found.notes.length, 1);
    assert.deepEqual(
      found.jobs.map((j) => j.id),
      ["j_1"],
    );
  });

  test("a held file is busy for another chat until released", () => {
    const a = chat("claude", "a");
    const b = chat("codex", "b");
    assert.deepEqual(claim(db, a, ["./src/app.ts"]), []);
    assert.deepEqual(context(db, b, { hold: ["src\\app.ts"] }).busy, [{ path: "src/app.ts", agent: "claude" }]);
    context(db, a, { hold: [] });
    assert.equal(context(db, b, { hold: ["src/app.ts"] }).busy, undefined);
    assert.throws(() => relPath("../x"), /relative/);
    assert.throws(() => relPath("C:/x"), /relative/);
    assert.throws(() => relPath("/etc/passwd"), /relative/);
  });

  test("sweep drops expired notes, lapsed holds, and idle sessions, keeping a caller with an open job", () => {
    const a = chat("claude", "a");
    const short = noteAdd(db, a, { text: "temporary finding" });
    db.prepare("UPDATE notes SET expires_at = ? WHERE id = ?").run(ago(1), short.id as string);
    claim(db, a, ["x.md"]);
    const caller = chat("codex", "caller");
    db.prepare(
      `INSERT INTO jobs (id, project_id, caller_session_id, folder, kind, agent_name, summary, task, prompt, state, started_at)
       VALUES ('j_open', ?, ?, ?, 'cursor', 'cursor-repo', 's', 't', 'p', 'running', ?)`,
    ).run(a.project_id, caller.id, repo, ago(40));
    db.prepare("UPDATE sessions SET last_seen_at = ?").run(ago(31));
    sweep(db, a.project_id);
    assert.equal(db.prepare("SELECT COUNT(*) AS n FROM notes").get()?.n, 0);
    assert.equal(db.prepare("SELECT COUNT(*) AS n FROM holds").get()?.n, 0);
    const left = (db.prepare("SELECT id FROM sessions").all() as { id: string }[]).map((r) => r.id);
    assert.deepEqual(left, [caller.id]);
    assert.deepEqual(db.prepare("PRAGMA foreign_key_check").all(), []);
  });

  test("holding another file keeps the ones already held; [] releases them all", () => {
    const a = chat("claude", "a");
    const b = chat("codex", "b");
    context(db, a, { hold: ["a.ts"] });
    context(db, a, { hold: ["b.ts"] });
    assert.deepEqual(
      (context(db, b, { hold: ["a.ts", "c.ts"] }).busy as { path: string }[]).map((x) => x.path),
      ["a.ts"],
    );
    context(db, a, { hold: [] });
    assert.equal(context(db, b, { hold: ["a.ts"] }).busy, undefined);
  });
});

describe("seen marks", () => {
  test("a note written while context reads is shown next time, not marked seen unshown", () => {
    const a = chat("claude", "a");
    const b = chat("codex", "b");
    context(db, a);
    const prepare = db.prepare.bind(db);
    let wrote = false;
    // Another agent writes a note in the middle of a's context call.
    db.prepare = ((sql: string) => {
      if (!wrote && sql.includes("FROM jobs WHERE project_id = ? AND seq >")) {
        wrote = true;
        noteAdd(db, b, { text: "Written mid-read by codex." });
      }
      return prepare(sql);
    }) as typeof db.prepare;
    try {
      context(db, a);
    } finally {
      db.prepare = prepare;
    }
    assert.ok(wrote);
    const next = context(db, a).notes as { body: string }[];
    assert.ok(next.some((n) => n.body === "Written mid-read by codex."));
  });

  test("every job since the last call is shown, not just the newest five", () => {
    const a = chat("claude", "a");
    context(db, a);
    for (let i = 0; i < 7; i++) {
      db.prepare(
        `INSERT INTO jobs (id, project_id, caller_session_id, folder, kind, agent_name, summary, task, prompt, state, started_at)
         VALUES (?, ?, 'other', ?, 'codex', 'codex-x', 's', ?, '', 'done', '2026-01-01T00:00:00Z')`,
      ).run(`j_${i}`, a.project_id, a.root, `task ${i}`);
    }
    assert.equal((context(db, a).jobs as string[]).length, 7);
  });
});

test("a noted file is marked stale when it changes, and not while it is the same", () => {
  // Unchanged size and modified time: the hash is reused, as make and git trust them.
  const a = chat("claude", "a");
  writeFileSync(join(repo, "plan.md"), "one\n");
  noteAdd(db, a, { text: "The plan is in plan.md.", tier: "long" });
  assert.equal(context(db, a).stale, undefined);
  assert.equal(context(db, a).stale, undefined); // from the cache
  writeFileSync(join(repo, "plan.md"), "two, and longer\n");
  assert.deepEqual((context(db, a).stale as { files: string[] }[])[0].files, ["plan.md"]);
});
