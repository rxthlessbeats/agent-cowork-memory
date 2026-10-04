import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { connect, type Db } from "../src/db.ts";
import {
  buildPrompt,
  card,
  type Deps,
  delegate,
  delegateWait,
  HerdrError,
  LIMITS,
  spawnJob,
  status,
  type Task,
} from "../src/delegate.ts";
import { context, noteSearch, type Session, sessionFor } from "../src/memory.ts";
import type { Json } from "../src/readers/index.ts";

type Pane = { pane_id: string; workspace_id: string; tab_id: string; cwd: string };

/** Enough of herdr for acm: panes, tabs, agents that write a transcript when prompted. */
class FakeHerdr {
  agents = new Map<string, Json>();
  panes: Pane[] = [];
  prompts: [string, string][] = [];
  blockStart = new Set<string>();
  stuckStart = new Set<string>();
  timeouts: Record<string, number> = {};
  refusePrompt = new Set<string>();
  finish = true;
  drop = 0;
  started = 0;
  running = true;
  t = 0;
  readonly roots: Record<string, string>;
  constructor(roots: Record<string, string>) {
    this.roots = roots;
  }

  deps(): Deps {
    return {
      herdr: (args, raw) => this.call(args, raw),
      startServer: () => {
        this.started += 1;
        this.running = true;
      },
      useHerdr: () => true,
      spawnJob: () => assert.fail("no background jobs with herdr"),
      installed: () => true,
      sleep: async (s) => {
        this.t += s;
      },
      clock: () => this.t,
      roots: this.roots,
    };
  }

  async call(args: string[], raw?: boolean): Promise<Json | string> {
    if (!this.running) throw new HerdrError("server_not_running", "no server");
    const cmd = args.slice(0, 2).join(" ");
    const opt = (flag: string) => args[args.indexOf(flag) + 1];
    if (cmd === "workspace list") return { workspaces: [] };
    if (cmd === "pane list") return { panes: [...this.panes] };
    if (cmd === "workspace create") {
      const pane = { pane_id: "w1:p1", workspace_id: "w1", tab_id: "w1:t1", cwd: opt("--cwd") };
      this.panes.push(pane);
      return { workspace: { workspace_id: "w1" }, root_pane: pane };
    }
    if (cmd === "pane split" || cmd === "tab create") {
      assert.ok(args.includes("ACM_DELEGATED=1"));
      const tabs = new Set(this.panes.map((p) => p.tab_id));
      const tab =
        cmd === "pane split" ? (this.panes.find((p) => p.pane_id === args[2])?.tab_id ?? "") : `w1:t${tabs.size + 1}`;
      const pane = { pane_id: `w1:p${this.panes.length + 1}`, workspace_id: "w1", tab_id: tab, cwd: opt("--cwd") };
      this.panes.push(pane);
      return cmd === "pane split" ? { pane } : { tab: { tab_id: tab }, root_pane: pane };
    }
    if (cmd === "agent list") return { agents: [...this.agents.values()] };
    if (cmd === "agent rename") {
      const [pane, name] = [args[2], args[3]];
      const key = [...this.agents.keys()].find((k) => this.agents.get(k)?.pane_id === pane) as string;
      const agent = this.agents.get(key) as Json;
      this.agents.delete(key);
      this.agents.set(name, { ...agent, name });
      return { type: "agent_renamed" };
    }
    if (cmd === "agent start") {
      const [name, kind, pane] = [args[2], opt("--kind"), opt("--pane")];
      const timeout = Number(opt("--timeout"));
      assert.ok(timeout > 3000 && timeout <= 300_000);
      this.timeouts[kind] = timeout;
      if (this.stuckStart.has(kind)) {
        this.t += timeout / 1000; // it waited out its whole budget
        // Like real herdr: the agent keeps running in its pane, but without a name.
        this.agents.set(`unnamed-${pane}`, {
          agent: kind,
          pane_id: pane,
          workspace_id: "w1",
          agent_status: "unknown",
          agent_session: { value: `${name}-session` },
        });
        throw new HerdrError("timeout", "timed out waiting for agent startup");
      }
      const blocked = this.blockStart.has(kind);
      this.agents.set(name, {
        name,
        agent: kind,
        pane_id: pane,
        workspace_id: "w1",
        agent_status: blocked ? "blocked" : "idle",
        agent_session: { value: `${name}-session` },
      });
      if (blocked) throw new HerdrError("agent_not_ready", "blocked during startup");
      return { type: "agent_started" };
    }
    if (cmd === "agent prompt") {
      const [name, text] = [args[2], args[3]];
      if (this.refusePrompt.has(name))
        throw new HerdrError("agent_not_ready", `agent ${name} is not an active named agent`);
      this.prompts.push([name, text]);
      if (this.drop) {
        this.drop -= 1;
        return { type: "agent_prompted" };
      }
      const agent = this.agents.get(name);
      if (agent) agent.agent_status = "working";
      if (this.finish) this.complete(name, text);
      return { type: "agent_prompted" };
    }
    if (cmd === "pane read") return raw ? "Do you want to proceed?\n❯ Yes\n  No\n" : {};
    throw new Error(`unexpected herdr call ${args.join(" ")}`);
  }

  /** The agent finishes the brief: its transcript gets the brief, an answer, and a turn end. */
  complete(name: string, brief: string, answer?: string) {
    const agent = this.agents.get(name) as Json;
    const kind = agent.agent as string;
    const native = (agent.agent_session as Json).value as string;
    const reply = answer ?? `${name} finished the work`;
    let path: string;
    let lines: Json[];
    if (kind === "codex") {
      path = join(this.roots.codex, "2026", `rollout-x-${native}.jsonl`);
      lines = [
        {
          type: "response_item",
          payload: { type: "message", role: "user", content: [{ type: "input_text", text: brief }] },
        },
        {
          type: "response_item",
          payload: { type: "message", role: "assistant", content: [{ type: "output_text", text: reply }] },
        },
        { type: "event_msg", payload: { type: "task_complete", last_agent_message: reply } },
      ];
    } else if (kind === "cursor") {
      path = join(this.roots.cursor, "proj", "agent-transcripts", native, `${native}.jsonl`);
      lines = [
        { role: "user", message: { content: [{ type: "text", text: brief }] } },
        { role: "assistant", message: { content: [{ type: "text", text: reply }] } },
        { type: "turn_ended", status: "success" },
      ];
    } else {
      path = join(this.roots.claude, "-proj", `${native}.jsonl`);
      lines = [
        { type: "user", message: { role: "user", content: brief } },
        { type: "assistant", message: { role: "assistant", content: [{ type: "text", text: reply }] } },
        { type: "system", subtype: "turn_duration" },
      ];
    }
    mkdirSync(join(path, ".."), { recursive: true });
    writeFileSync(path, lines.map((l) => `${JSON.stringify(l)}\n`).join(""), { flag: "a" });
    agent.agent_status = "idle";
  }
}

let dir: string;
let db: Db;
let folder: string;
let home: string;
let fake: FakeHerdr;
let caller: Session;

beforeEach(() => {
  dir = mkdtempSync(join(tmpdir(), "acm-"));
  home = join(dir, "home");
  db = connect(home);
  folder = join(dir, "work");
  mkdirSync(folder);
  folder = realpathSync(folder);
  const roots: Record<string, string> = {};
  for (const k of ["codex", "cursor", "claude", "opencode"]) {
    roots[k] = join(dir, "t", k);
    mkdirSync(roots[k], { recursive: true });
  }
  fake = new FakeHerdr(roots);
  caller = sessionFor(db, { harness: "cursor", chat: "caller", folder });
  LIMITS.resendAfter = 10;
  LIMITS.lostAfter = 60;
  LIMITS.jobSeconds = 15 * 60;
});

afterEach(() => {
  db.close();
  rmSync(dir, { recursive: true, force: true });
});

function run(tasks: Task[], summary = "Plan a Lisbon trip.", s: Session = caller, deps = fake.deps()) {
  return delegate(db, s, { summary, tasks, home, deps });
}

const states = (out: Json) => (out.jobs as Json[]).map((j) => [j.agent, j.state]);

test("two agents run in parallel, each with its brief", async () => {
  const got = await run([
    { to: "codex", task: "Write plan.md", done_when: "plan.md exists" },
    { to: "claude", task: "Write packing.md", context: "Carry-on only." },
  ]);
  assert.deepEqual(states(got), [
    ["codex-work", "done"],
    ["claude-work", "done"],
  ]);
  assert.equal((got.jobs as Json[])[0].result, "codex-work finished the work");
  assert.equal(got.next, undefined);
  const prompts = Object.fromEntries(fake.prompts);
  assert.match(prompts["codex-work"], /## Problem\nPlan a Lisbon trip\./);
  assert.match(prompts["codex-work"], /## Done when\nplan\.md exists/);
  assert.match(prompts["codex-work"], /- claude-work: Write packing\.md/);
  assert.match(prompts["claude-work"], /## Context\nCarry-on only\./);
  assert.match(prompts["claude-work"], new RegExp(`pass thread=${got.thread}`));
});

test("results live on the job, are searchable, and land on the caller's thread timeline", async () => {
  const got = await run([{ to: "codex", task: "Write plan.md" }]);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM notes").get()?.n, 0);
  const found = noteSearch(db, caller, "finished");
  assert.deepEqual(
    found.jobs.map((j) => j.agent),
    ["codex-work"],
  );
  assert.equal(
    db.prepare("SELECT name FROM threads WHERE id = ?").get(got.thread as string)?.name,
    "Plan a Lisbon trip.",
  );
  const timeline = context(db, caller).timeline as string[];
  assert.ok(timeline.some((l) => /codex-work started: Write plan\.md/.test(l)));
  assert.ok(timeline.some((l) => /codex-work done: codex-work finished the work/.test(l)));
});

test("a follow-up reuses the agent and skips an unchanged problem; another caller reuses it too", async () => {
  await run([{ to: "codex", task: "Write plan.md" }]);
  const again = await run([{ to: "codex", task: "Add a budget section" }]);
  assert.equal((again.jobs as Json[])[0].agent, "codex-work");
  assert.equal(fake.agents.size, 1);
  assert.doesNotMatch(fake.prompts.at(-1)?.[1] ?? "", /## Problem/);
  const other = sessionFor(db, { harness: "claude", chat: "other", folder });
  await run([{ to: "codex", task: "Write budget.md" }], "Budget the trip.", other);
  assert.equal(fake.agents.size, 1);
  assert.match(fake.prompts.at(-1)?.[1] ?? "", /## Problem\nBudget the trip\./);
});

test("a busy agent refuses; the wait continues; nothing new starts", async () => {
  fake.finish = false;
  const first = await run([{ to: "codex", task: "Long job" }]);
  assert.equal((first.jobs as Json[])[0].state, "running");
  assert.ok(first.next);
  const panes = fake.panes.length;
  const other = sessionFor(db, { harness: "claude", chat: "other", folder });
  const busy = await run([{ to: "codex", task: "Another job" }], "Something else.", other);
  assert.equal(fake.panes.length, panes);
  assert.deepEqual(states(busy), [["codex-work", "busy"]]);
  assert.match((busy.jobs as Json[])[0].result as string, /still working on: Long job\. Try again/);
  assert.deepEqual(busy.free, ["claude", "cursor", "opencode"]);
  assert.match(busy.busy_next as string, /Ask the user whether to wait .* or to give the task to one of free/);
  assert.equal(
    card(busy),
    "codex  busy\nbusy · codex is working on something else; free now: claude, cursor, opencode",
  );
  fake.complete(...(fake.prompts[0] as [string, string]));
  const done = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.deepEqual(states(done), [["codex-work", "done"]]);
  const idle = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.deepEqual(idle.jobs, []);
  fake.running = false; // herdr down, nothing open: still answers
  assert.deepEqual((await delegateWait(db, caller, { home, deps: fake.deps() })).jobs, []);
});

test("a job id seen in an agent's chat before its brief (in a context result) doesn't end that job", async () => {
  fake.finish = false;
  await run([{ to: "codex", task: "Long job" }]);
  const other = sessionFor(db, { harness: "claude", chat: "other", folder });
  const queued = await run([{ to: "codex", task: "Next job", wait: true }], "Something else.", other);
  const id = (queued.jobs as Json[])[0].job as string;
  // During the long job, codex calls context, which lists the queued job by id; then the long job ends.
  fake.complete(...(fake.prompts[0] as [string, string]), `context showed ${id} queued; long job done`);
  const first = await delegateWait(db, other, { home, deps: fake.deps() });
  assert.deepEqual(states(first), [["codex-work", "running"]]); // briefed now, not done with the long job's answer
  fake.complete(...(fake.prompts.at(-1) as [string, string]), "next job done");
  const done = await delegateWait(db, other, { home, deps: fake.deps() });
  assert.deepEqual(states(done), [["codex-work", "done"]]);
  assert.equal((done.jobs as Json[])[0].result, "next job done");
});

test("waiting for a busy agent queues the task; it starts once the agent is free", async () => {
  fake.finish = false;
  await run([{ to: "codex", task: "Long job" }]);
  const other = sessionFor(db, { harness: "claude", chat: "other", folder });
  const queued = await run([{ to: "codex", task: "Next job", wait: true }], "Something else.", other);
  assert.deepEqual(states(queued), [["codex-work", "queued"]]);
  assert.ok(queued.next);
  assert.match(card(queued), /codex {2}queued/);
  // A third caller asking for codex now finds it busy: the queue holds its place.
  const third = sessionFor(db, { harness: "cursor", chat: "third", folder });
  assert.deepEqual(states(await run([{ to: "codex", task: "Third" }], "Third.", third)), [["codex-work", "busy"]]);
  assert.equal(fake.prompts.length, 1);
  // The first job finishes; the queued one gets its brief on the next wait, and finishes too.
  fake.complete(...(fake.prompts[0] as [string, string]));
  fake.finish = true;
  const done = await delegateWait(db, other, { home, deps: fake.deps() });
  assert.deepEqual(states(done), [["codex-work", "done"]]);
  assert.match(fake.prompts.at(-1)?.[1] ?? "", /## Your task\nNext job/);
});

test("a queued background job starts in the background once the job ahead of it ends", async () => {
  const started: string[] = [];
  const deps: Deps = {
    ...fake.deps(),
    useHerdr: () => false,
    spawnJob: (base) => {
      started.push(base);
      if (started.length === 2) {
        writeFileSync(`${base}.out`, "second done");
        writeFileSync(`${base}.exit`, "0\n");
      }
    },
  };
  await run([{ to: "cursor", task: "First" }], "One.", caller, deps);
  const other = sessionFor(db, { harness: "claude", chat: "other", folder });
  const queued = await run([{ to: "cursor", task: "Second", wait: true }], "Two.", other, deps);
  assert.deepEqual(states(queued), [["cursor-work", "queued"]]);
  assert.equal(started.length, 1);
  writeFileSync(`${started[0]}.out`, "first done");
  writeFileSync(`${started[0]}.exit`, "0\n");
  await delegateWait(db, caller, { home, deps });
  const second = await delegateWait(db, other, { home, deps });
  assert.equal(started.length, 2);
  assert.deepEqual(states(second), [["cursor-work", "done"]]);
});

test("a worker joins the caller's thread from its brief; its holds go when the job ends", async () => {
  fake.finish = false;
  const got = await run([{ to: "codex", task: "Long job" }]);
  const worker = sessionFor(db, { harness: "codex", chat: "codex-chat", folder });
  const seen = context(db, worker, { thread: got.thread as string, hold: ["plan.md"] });
  assert.equal((seen.thread as Json).id, got.thread);
  assert.deepEqual(seen.held, [{ path: "plan.md", agent: "codex-work" }]);
  assert.deepEqual(
    (context(db, caller).working as Json[]).map((w) => w.agent),
    ["codex-work"],
  );
  fake.complete(...(fake.prompts[0] as [string, string]));
  await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM holds").get()?.n, 0);
});

test("a reused worker already on the thread is linked to its new job, and its holds go when that job ends", async () => {
  const got = await run([{ to: "codex", task: "First job" }]);
  const worker = sessionFor(db, { harness: "codex", chat: "codex-chat", folder });
  context(db, worker, { thread: got.thread as string });
  fake.finish = false;
  await run([{ to: "codex", task: "Second job" }]);
  context(db, worker, { thread: got.thread as string, hold: ["second.md"] });
  const linked = db.prepare("SELECT worker_session_id FROM jobs WHERE task = 'Second job'").get();
  assert.equal(linked?.worker_session_id, worker.id);
  fake.complete(...(fake.prompts.at(-1) as [string, string]));
  await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM holds").get()?.n, 0);
});

test("one pane per agent, two panes per tab, and OpenCode gets a tab to itself", async () => {
  await run([
    { to: "codex", task: "A" },
    { to: "claude", task: "B" },
    { to: "cursor", task: "C" },
  ]);
  assert.deepEqual(
    fake.panes.map((p) => p.tab_id),
    ["w1:t1", "w1:t1", "w1:t2"],
  );
  const same = await run(
    [
      { to: "codex", task: "A" },
      { to: "codex", task: "C" },
    ],
    "Other.",
  );
  assert.deepEqual(
    (same.jobs as Json[]).map((j) => j.state),
    ["busy", "done"],
  );

  fake = new FakeHerdr(fake.roots);
  fake.finish = false;
  mkdirSync(join(dir, "other"));
  const elsewhere = realpathSync(join(dir, "other"));
  const s = sessionFor(db, { harness: "cursor", chat: "c2", folder: elsewhere });
  await run(
    ["opencode", "claude", "codex", "cursor"].map((to) => ({ to, task: "x" })),
    "Four.",
    s,
  );
  const perTab = new Map<string, number>();
  for (const p of fake.panes) perTab.set(p.tab_id, (perTab.get(p.tab_id) ?? 0) + 1);
  const oc = fake.agents.get("opencode-other")?.pane_id;
  assert.equal(perTab.get(fake.panes.find((p) => p.pane_id === oc)?.tab_id ?? ""), 1);
  assert.deepEqual([...perTab.values()].sort(), [1, 1, 2]);
});

test("a brief lost twice (a dialog on the agent's screen) ends the job as gone, saying what the pane shows", async () => {
  LIMITS.resendAfter = -1;
  LIMITS.lostAfter = -1;
  fake.drop = 2;
  const got = await run([{ to: "claude", task: "Write packing.md" }]);
  assert.equal(fake.prompts.length, 2); // sent, then resent
  const job = (got.jobs as Json[])[0];
  assert.equal(job.state, "gone");
  assert.match(job.result as string, /never got its brief: .*Its pane shows: Do you want to proceed/s);
  await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.equal(fake.prompts.length, 2); // nothing more typed into whatever is on its screen
});

test("a dropped brief is sent once more", async () => {
  LIMITS.resendAfter = -1;
  fake.drop = 1;
  const got = await run([{ to: "codex", task: "Write plan.md" }]);
  assert.equal((got.jobs as Json[])[0].state, "done");
  assert.equal(fake.prompts.length, 2);
});

test("blocked agents and blocked starts are reported, never answered", async () => {
  fake.finish = false;
  await run([{ to: "codex", task: "Risky" }]);
  (fake.agents.get("codex-work") as Json).agent_status = "blocked";
  const got = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.equal((got.jobs as Json[])[0].state, "blocked");
  assert.match((got.jobs as Json[])[0].result as string, /Do you want to proceed\?/);
  assert.ok(got.blocked);
  assert.match(card(got), /blocked · codex is waiting for an answer in its herdr pane/);

  fake.blockStart.add("claude");
  const other = sessionFor(db, { harness: "claude", chat: "o", folder });
  const starting = await run([{ to: "claude", task: "Write packing.md" }], "Pack.", other);
  assert.equal((starting.jobs as Json[])[0].state, "starting");
  (fake.agents.get("claude-work") as Json).agent_status = "idle";
  fake.finish = true;
  const done = await delegateWait(db, other, { home, deps: fake.deps() });
  assert.equal((done.jobs as Json[])[0].state, "done");
});

test("a stalled start doesn't shrink the others' budget; it stays starting and gets its brief once ready", async () => {
  fake.stuckStart.add("codex");
  const got = await run([
    { to: "codex", task: "Write plan.md" },
    { to: "claude", task: "Write packing.md" },
    { to: "cursor", task: "Write budget.md" },
  ]);
  assert.deepEqual(fake.timeouts, { codex: 30000, claude: 30000, cursor: 30000 });
  assert.deepEqual(states(got), [
    ["codex-work", "starting"],
    ["claude-work", "done"],
    ["cursor-work", "done"],
  ]);
  assert.match((got.jobs as Json[])[0].result as string, /Do you want to proceed/); // what the pane shows
  assert.ok(got.blocked);
  // It finishes starting: the next wait names it and sends its brief.
  (fake.agents.get("unnamed-w1:p1") as Json).agent_status = "idle";
  const done = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.deepEqual(states(done), [["codex-work", "done"]]);
});

test("briefs go out at once, so slow briefs don't add up", async () => {
  const deps = fake.deps();
  const herdrCall = deps.herdr;
  deps.herdr = async (args, raw) => {
    if (args[0] === "agent" && args[1] === "prompt") await new Promise((r) => setTimeout(r, 200));
    return herdrCall(args, raw);
  };
  const t0 = performance.now();
  await run(
    ["codex", "claude", "cursor", "opencode"].map((to) => ({ to, task: "x" })),
    "Four.",
    caller,
    deps,
  );
  assert.ok(performance.now() - t0 < 700, `four 200 ms briefs took ${Math.round(performance.now() - t0)} ms`);
  assert.equal(fake.prompts.length, 4);
});

test("a denied action in a pane comes back as needs_approval with what it wants", async () => {
  fake.finish = false;
  await run([{ to: "claude", task: "Delete ~/old.txt" }]);
  const [name, brief] = fake.prompts[0];
  assert.match(brief, /## If an action is denied/);
  fake.complete(name, brief, "BLOCKED: delete ~/old.txt\nAuto mode refused it.");
  const got = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.equal((got.jobs as Json[])[0].state, "needs_approval");
  assert.equal((got.jobs as Json[])[0].ask, "delete ~/old.txt");
  assert.match(card(got), /needs_approval · claude wants to delete ~\/old\.txt/);
});

test("an agent herdr can't brief runs in the background instead; the others are unaffected", async () => {
  fake.refusePrompt.add("cursor-work");
  const deps: Deps = {
    ...fake.deps(),
    spawnJob: (base) => {
      writeFileSync(`${base}.out`, "cursor did B in the background");
      writeFileSync(`${base}.exit`, "0\n");
    },
  };
  const got = await run(
    [
      { to: "codex", task: "A" },
      { to: "cursor", task: "B" },
      { to: "claude", task: "C" },
    ],
    "Three.",
    caller,
    deps,
  );
  assert.deepEqual(
    (got.jobs as Json[]).map((j) => [j.agent, j.pane === "background", j.state]),
    [
      ["codex-work", false, "done"],
      ["cursor-work", true, "done"],
      ["claude-work", false, "done"],
    ],
  );
  const without: Deps = { ...deps, installed: () => false };
  const other = sessionFor(db, { harness: "claude", chat: "o", folder });
  fake.refusePrompt.add("opencode-work");
  const gone = await run([{ to: "opencode", task: "D" }], "Four.", other, without);
  assert.match(
    (gone.jobs as Json[])[0].result as string,
    /could not give opencode-work its brief: .*not an active named agent/,
  );
});

test("a closed pane is gone; herdr is started when it isn't running", async () => {
  fake.running = false;
  fake.finish = false;
  await run([{ to: "cursor", task: "X" }]);
  assert.equal(fake.started, 1);
  fake.agents.clear();
  const got = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.equal((got.jobs as Json[])[0].state, "gone");
});

test("refusals: no summary, no task text, an unknown agent", async () => {
  await assert.rejects(run([{ to: "codex", task: "X" }], " "), /summary is required/);
  await assert.rejects(run([{ to: "codex", task: " " }]), /task text/);
  await assert.rejects(run([{ to: "gemini", task: "X" }]), /to must be one of/);
  assert.deepEqual(fake.prompts, []);
});

function background(write: (base: string, cmd: string[]) => void, installed = true): Deps {
  return {
    ...fake.deps(),
    useHerdr: () => false,
    installed: () => installed,
    spawnJob: (base, cmd) => {
      runs.push([cmd, readFileSync(`${base}.prompt`, "utf8")]);
      write(base, cmd);
    },
  };
}
let runs: [string[], string][] = [];

test("without herdr, agents run in the background with the brief on stdin", async () => {
  runs = [];
  const deps = background((base, cmd) => {
    if (cmd[0] === "codex") writeFileSync(cmd[cmd.indexOf("-o") + 1], "codex wrote plan.md");
    else writeFileSync(`${base}.log`, "boom");
    writeFileSync(`${base}.out`, "");
    writeFileSync(`${base}.exit`, cmd[0] === "codex" ? "0\n" : "1\n");
  });
  const got = await run(
    [
      { to: "codex", task: "Write plan.md" },
      { to: "claude", task: "Write packing.md" },
    ],
    "Plan a trip.",
    caller,
    deps,
  );
  assert.deepEqual(
    (got.jobs as Json[]).map((j) => [j.agent, j.pane, j.state]),
    [
      ["codex-work", "background", "done"],
      ["claude-work", "background", "gone"],
    ],
  );
  assert.equal((got.jobs as Json[])[0].result, "codex wrote plan.md");
  assert.match((got.jobs as Json[])[1].result as string, /exited with code 1\. Last lines: boom/);
  assert.match(got.watch as string, /tail -f/);
  assert.deepEqual(
    runs.map(([cmd]) => cmd.slice(0, 2)),
    [
      ["codex", "exec"],
      ["claude", "-p"],
    ],
  );
  assert.equal(runs[0][0].at(-1), "-"); // codex reads the brief from stdin
  assert.match(runs[1][1], /## Problem\nPlan a trip\./);
  assert.match(card(got, [{ to: "codex", task: "Write plan.md" }]), /^acm · delegate\(tasks=1 · background\)/);
  await assert.rejects(
    run(
      [{ to: "cursor", task: "X" }],
      "S",
      caller,
      background(() => {}, false),
    ),
    /not installed/,
  );
});

test("a background job still running at the limit is stopped, process tree and all", async () => {
  LIMITS.jobSeconds = -1;
  const pids: number[] = [];
  const deps: Deps = {
    ...fake.deps(),
    useHerdr: () => false,
    spawnJob: (base, _cmd, cwd) => {
      spawnJob(base, ["sleep", "30"], cwd);
      const pid = Number(readFileSync(`${base}.pid`, "utf8"));
      assert.ok(pid > 0);
      process.kill(-pid, 0); // the job's process group is running before acm stops it
      pids.push(pid);
    },
  };
  const stopped = await run([{ to: "cursor", task: "Run the risky command" }], "Ship it.", caller, deps);
  assert.equal((stopped.jobs as Json[])[0].state, "needs_approval");
  assert.match((stopped.jobs as Json[])[0].result as string, /no result.*approval/s);
  let gone = false;
  for (let i = 0; i < 40 && !gone; i++) {
    try {
      process.kill(-pids[0], 0);
      await new Promise((r) => setTimeout(r, 50));
    } catch {
      gone = true;
    }
  }
  assert.ok(gone, "the job's process group is still there");
});

test("the brief leaves out empty sections", () => {
  const text = buildPrompt({ job: "j_1", harness: "codex", thread: "t_1", folder: "/w", summary: "S", task: "T" });
  assert.ok(text.startsWith("[acm job j_1] A codex chat asked for this in /w. Your acm thread is t_1"));
  assert.match(text, /hold set to every file/);
  assert.match(text, /You decide; say what you checked\./);
  assert.doesNotMatch(text, /## Context|## Others/);
});

test("wait: true behind a task in the same call is queued after it, with and without herdr", async () => {
  // Without herdr: B must wait in the queue, not be marked gone, and start in the background after A.
  const started: string[] = [];
  const deps: Deps = { ...fake.deps(), useHerdr: () => false, spawnJob: (base) => void started.push(base) };
  const both = [
    { to: "codex", task: "A" },
    { to: "codex", task: "B", wait: true },
  ];
  const got = await run(both, "Two for codex.", caller, deps);
  assert.deepEqual(
    (got.jobs as Json[]).map((j) => j.state),
    ["running", "queued"],
  );
  assert.equal(started.length, 1);
  writeFileSync(`${started[0]}.out`, "A done");
  writeFileSync(`${started[0]}.exit`, "0\n");
  const next = await delegateWait(db, caller, { home, deps });
  assert.equal(started.length, 2);
  assert.deepEqual(
    (next.jobs as Json[]).map((j) => j.state),
    ["done", "running"],
  );

  // With herdr: B is not briefed until A's turn has ended.
  fake.finish = false;
  mkdirSync(join(dir, "second"));
  const second = sessionFor(db, { harness: "claude", chat: "c", folder: realpathSync(join(dir, "second")) });
  const inPanes = await run(
    [
      { to: "cursor", task: "A" },
      { to: "cursor", task: "B", wait: true },
    ],
    "Two for cursor.",
    second,
  );
  assert.deepEqual(
    (inPanes.jobs as Json[]).map((j) => j.state),
    ["running", "queued"],
  );
  assert.equal(fake.prompts.length, 1);
});

test("a missing agent is refused before any other agent is started", async () => {
  let spawned = 0;
  const deps: Deps = {
    ...fake.deps(),
    useHerdr: () => false,
    installed: (binary) => binary !== "cursor-agent",
    spawnJob: () => {
      spawned += 1;
    },
  };
  const tasks = [
    { to: "codex", task: "A" },
    { to: "cursor", task: "B" },
  ];
  await assert.rejects(run(tasks, "Two.", caller, deps), /cursor-agent is not installed/);
  assert.equal(spawned, 0);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM jobs").get()?.n, 0);
});

test("a job's chat is found by searching only what was appended, even when the marker arrives in two writes", async () => {
  fake.finish = false;
  const got = await run([{ to: "codex", task: "Long job" }]);
  const id = (got.jobs as Json[])[0].job as string;
  // herdr doesn't know this agent's chat, so acm has to search for the brief's marker.
  delete (fake.agents.get("codex-work") as Json).agent_session;
  const file = join(fake.roots.codex, "2026", "rollout-found-by-search.jsonl");
  mkdirSync(join(file, ".."), { recursive: true });
  const brief = JSON.stringify({
    type: "response_item",
    payload: { type: "message", role: "user", content: [{ type: "input_text", text: `[acm job ${id}] do it` }] },
  });
  const cut = brief.indexOf(id) + 4; // the first write ends in the middle of the marker
  writeFileSync(file, `${JSON.stringify({ type: "session_meta", payload: {} })}\n${brief.slice(0, cut)}`);
  const first = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.equal((first.jobs as Json[])[0].state, "running");
  const answer = { type: "message", role: "assistant", content: [{ type: "output_text", text: "found late" }] };
  writeFileSync(
    file,
    `${brief.slice(cut)}\n${JSON.stringify({ type: "response_item", payload: answer })}\n${JSON.stringify({ type: "event_msg", payload: { type: "task_complete" } })}\n`,
    { flag: "a" },
  );
  const done = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.deepEqual([(done.jobs as Json[])[0].state, (done.jobs as Json[])[0].result], ["done", "found late"]);
});

test("two processes refreshing the same jobs at once: one records each change, one resends a brief", async () => {
  fake.finish = false;
  await run([{ to: "codex", task: "Finish me" }]);
  const other = sessionFor(db, { harness: "claude", chat: "other", folder });
  fake.drop = 1; // claude drops its first brief, so it is due a resend
  await run([{ to: "claude", task: "Resend me" }], "Other.", other);
  LIMITS.resendAfter = -1;
  const codexBrief = fake.prompts.find(([n]) => n === "codex-work") as [string, string];
  fake.complete(...codexBrief);
  const sentBefore = fake.prompts.length;
  // Two waits refresh the folder's open jobs at the same moment.
  await Promise.all([
    delegateWait(db, caller, { home, deps: fake.deps() }),
    delegateWait(db, other, { home, deps: fake.deps() }),
  ]);
  const doneEvents = db
    .prepare("SELECT COUNT(*) AS n FROM events WHERE kind = 'job_done' AND text LIKE 'codex-work%'")
    .get();
  assert.equal(doneEvents?.n, 1);
  const codexJob = db.prepare("SELECT id FROM jobs WHERE agent_name = 'codex-work'").get()?.id as string;
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM search WHERE ref = ?").get(codexJob)?.n, 1);
  assert.equal(fake.prompts.length - sentBefore, 1); // claude's brief resent once, not twice
});

test("status shows a chat's jobs and thread, and records a job that finished since", async () => {
  fake.finish = false;
  await run([{ to: "codex", task: "Finish me" }]);
  const look = () => status(db, { home, folder, harness: "cursor", chat: "caller", deps: fake.deps() });
  let out = await look();
  assert.deepEqual(
    (out.jobs as Json[]).map((j) => [j.agent, j.state, j.mine]),
    [["codex-work", "running", true]],
  );
  assert.equal((out.thread as Json).name, "Plan a Lisbon trip.");
  fake.complete(...(fake.prompts.find(([n]) => n === "codex-work") as [string, string]));
  out = await look();
  assert.equal((out.jobs as Json[])[0].state, "done");
  assert.ok(((out.thread as Json).events as Json[]).some((e) => e.kind === "job_done"));
  // Another folder knows nothing, and asking creates nothing.
  const empty = await status(db, { home, folder: dir, deps: fake.deps() });
  assert.deepEqual(empty.jobs, []);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM projects").get()?.n, 1);
});

test("two delegates at once for the same agent: one briefs it, the other finds it busy", async () => {
  fake.finish = false;
  const other = sessionFor(db, { harness: "claude", chat: "other", folder });
  const [a, b] = await Promise.all([
    run([{ to: "codex", task: "First" }]),
    run([{ to: "codex", task: "Second" }], "Other.", other),
  ]);
  assert.equal(fake.prompts.filter(([n]) => n === "codex-work").length, 1);
  assert.deepEqual([...states(a), ...states(b)].map(([, st]) => st).sort(), ["busy", "running"]);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM jobs WHERE agent_name = 'codex-work'").get()?.n, 1);
});

test("the result is the brief's own turn, not a later one in the same chat", async () => {
  fake.finish = false;
  await run([{ to: "codex", task: "Answer once" }]);
  const brief = fake.prompts.find(([n]) => n === "codex-work") as [string, string];
  fake.complete(brief[0], brief[1], "the job's answer");
  fake.complete("codex-work", "something the user typed in the pane", "an answer to something else");
  const out = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.equal((out.jobs as Json[])[0].result, "the job's answer");
});

test("a pane closed after the agent finished keeps its result", async () => {
  fake.finish = false;
  await run([{ to: "codex", task: "Finish, then close" }]);
  fake.complete(...(fake.prompts.find(([n]) => n === "codex-work") as [string, string]));
  fake.agents.delete("codex-work");
  const out = await delegateWait(db, caller, { home, deps: fake.deps() });
  assert.deepEqual(states(out), [["codex-work", "done"]]);
  assert.equal((out.jobs as Json[])[0].result, "codex-work finished the work");
});

test("a brief is not resent for a job another process just finished", async () => {
  fake.drop = 1; // dropped, so the job is due a resend
  await run([{ to: "codex", task: "Done elsewhere" }]);
  LIMITS.resendAfter = -1;
  const sent = fake.prompts.length;
  const deps = fake.deps();
  const herdr = deps.herdr;
  // Another process records the job done between this one reading it and checking it.
  deps.herdr = async (args, raw) => {
    if (args[0] === "agent" && args[1] === "list") db.prepare("UPDATE jobs SET state = 'done'").run();
    return herdr(args, raw);
  };
  await delegateWait(db, caller, { home, deps });
  assert.equal(fake.prompts.length, sent);
  assert.equal(db.prepare("SELECT state FROM jobs").get()?.state, "done");
});

test("a worker that joins while its job is being checked still has its files freed", async () => {
  fake.finish = false;
  await run([{ to: "codex", task: "Hold a file" }]);
  fake.complete(...(fake.prompts.find(([n]) => n === "codex-work") as [string, string]));
  const worker = sessionFor(db, { harness: "codex", chat: "codex-work-session", folder });
  const deps = fake.deps();
  const herdr = deps.herdr;
  deps.herdr = async (args, raw) => {
    if (args[0] === "agent" && args[1] === "list") {
      db.prepare("UPDATE jobs SET worker_session_id = ?").run(worker.id);
      db.prepare(
        "INSERT OR IGNORE INTO holds (project_id, path, session_id, created_at) VALUES (?, 'a.md', ?, '')",
      ).run(worker.project_id, worker.id);
    }
    return herdr(args, raw);
  };
  await delegateWait(db, caller, { home, deps });
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM holds").get()?.n, 0);
});
