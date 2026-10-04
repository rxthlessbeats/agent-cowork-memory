import assert from "node:assert/strict";
import { type ChildProcessWithoutNullStreams, execFileSync, spawn } from "node:child_process";
import { mkdtempSync, realpathSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createInterface } from "node:readline";
import { afterEach, beforeEach, test } from "node:test";

const CLI = join(import.meta.dirname, "..", "src", "cli.ts");
type Msg = { id?: number; result?: Record<string, unknown>; error?: unknown };

/** A minimal MCP client over stdio: JSON-RPC lines in, responses matched by id. */
class Client {
  proc: ChildProcessWithoutNullStreams;
  waiting = new Map<number, (m: Msg) => void>();
  next = 1;
  constructor(args: string[], cwd: string, home: string) {
    this.proc = spawn(process.execPath, [CLI, "mcp", ...args], { cwd, env: { ...process.env, ACM_HOME: home } });
    createInterface({ input: this.proc.stdout }).on("line", (line) => {
      const msg = JSON.parse(line) as Msg;
      if (msg.id !== undefined) this.waiting.get(msg.id)?.(msg);
    });
  }
  request(method: string, params: Record<string, unknown> = {}): Promise<Msg> {
    const id = this.next++;
    return new Promise((resolve) => {
      this.waiting.set(id, resolve);
      this.proc.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", id, method, params })}\n`);
    });
  }
  async init(clientName: string) {
    await this.request("initialize", {
      protocolVersion: "2025-06-18",
      capabilities: {},
      clientInfo: { name: clientName, version: "1" },
    });
    this.proc.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" })}\n`);
  }
  async call(name: string, args: Record<string, unknown> = {}) {
    const res = (await this.request("tools/call", { name, arguments: args })).result as {
      content: { text: string }[];
      isError?: boolean;
    };
    // biome-ignore lint/suspicious/noExplicitAny: test reads arbitrary result fields
    let json: Record<string, any> = {};
    try {
      json = JSON.parse(res.content.at(-1)?.text ?? "{}");
    } catch {
      // the SDK's own input validation errors are plain text
    }
    return { texts: res.content.map((c) => c.text), json, isError: Boolean(res.isError) };
  }
  close() {
    this.proc.kill();
  }
}

let dir: string;
let repo: string;
let client: Client;

beforeEach(() => {
  dir = mkdtempSync(join(tmpdir(), "acm-mcp-"));
  repo = join(dir, "repo");
  execFileSync("git", ["init", "-q", repo]);
  repo = realpathSync(repo);
});

afterEach(() => {
  client?.close();
  rmSync(dir, { recursive: true, force: true });
});

test("seven tools; the agent comes from the client name; repo_path defaults to the working directory", async () => {
  client = new Client([], repo, join(dir, "home"));
  await client.init("claude-code");
  const listed = (await client.request("tools/list")).result ?? {};
  const tools = (listed.tools as { name: string }[]).map((t) => t.name).sort();
  assert.deepEqual(tools, ["chats", "context", "delegate", "delegate_wait", "note_add", "note_search", "resume"]);
  // Every tool declares all four hints as booleans; only delegate reaches out and can destroy.
  for (const t of listed.tools as { name: string; annotations?: Record<string, unknown> }[]) {
    for (const key of ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"]) {
      assert.equal(typeof t.annotations?.[key], "boolean", `${t.name} ${key}`);
    }
    assert.equal(t.annotations?.destructiveHint, t.name === "delegate", t.name);
  }
  const added = await client.call("note_add", { text: "use pnpm, not npm", tier: "long" });
  assert.ok(added.json.thread);
  const seen = await client.call("context");
  assert.deepEqual(
    seen.json.notes.map((n: { body: string; by: string }) => [n.body, n.by]),
    [["use pnpm, not npm", "claude"]],
  );
  assert.equal(seen.json.thread.id, added.json.thread);
  const again = await client.call("context");
  assert.deepEqual(again.json.notes, []);
});

test("errors carry the JSON payload; an unknown client is refused", async () => {
  client = new Client([], repo, join(dir, "home"));
  await client.init("some-editor");
  const out = await client.call("context");
  assert.equal(out.isError, true);
  assert.equal(out.json.error, "harness");
  assert.match(out.json.message, /--harness codex\|cursor\|claude\|opencode/);
});

test("--harness wins; delegate_wait shows its card first, then the JSON with a reply hint", async () => {
  client = new Client(["--harness", "codex"], repo, join(dir, "home"));
  await client.init("anything");
  const bad = await client.call("note_add", { text: "x", tier: "medium" });
  assert.equal(bad.isError, true);
  assert.match(bad.texts[0], /tier/);
  const wait = await client.call("delegate_wait");
  assert.equal(wait.texts[0], "acm · delegate_wait(nothing running; every result was already reported)\n\n");
  assert.deepEqual(wait.json.jobs, []);
  assert.match(wait.json.reply, /card above this JSON/);
});

test("an acm that can't write its database (a sandbox) says so", async () => {
  const home = join(dir, "home");
  client = new Client(["--harness", "codex"], repo, home);
  await client.init("anything");
  await client.call("context");
  client.close();
  const { chmodSync, readdirSync } = await import("node:fs");
  for (const name of readdirSync(home)) if (name.startsWith("acm.sqlite3")) chmodSync(join(home, name), 0o444);
  chmodSync(home, 0o555);
  try {
    client = new Client(["--harness", "codex"], repo, home);
    await client.init("anything");
    const out = await client.call("note_add", { text: "x" });
    assert.equal(out.isError, true);
    assert.match(out.json.message, /inside a sandbox/);
  } finally {
    chmodSync(home, 0o755);
    for (const name of readdirSync(home)) if (name.startsWith("acm.sqlite3")) chmodSync(join(home, name), 0o644);
  }
});
