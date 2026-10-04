// Install check, run in CI on Linux, macOS, and Windows: pack the package, install the tarball into a fresh
// folder, run setup twice in a fresh HOME (the second run must change nothing), and start the installed
// `acm mcp` over stdio until it lists its seven tools.
import assert from "node:assert/strict";
import { execFileSync, spawn } from "node:child_process";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const win = process.platform === "win32";
const run = (cmd, args, opts = {}) => execFileSync(cmd, args, { encoding: "utf8", shell: win, ...opts });

const work = mkdtempSync(join(tmpdir(), "acm-install-"));
const tarball = join(process.cwd(), run("npm", ["pack", "--silent"]).trim().split("\n").at(-1));
run("npm", ["install", "--prefix", work, "--no-fund", "--no-audit", tarball]);
const acm = join(work, "node_modules", ".bin", win ? "acm.cmd" : "acm");

const home = join(work, "home");
const env = { ...process.env, HOME: home, USERPROFILE: home };
assert.equal(run(acm, ["--version"], { env }).trim(), JSON.parse(readFileSync("package.json", "utf8")).version);
const first = JSON.parse(run(acm, ["setup"], { env }));
assert.equal(first.cursor, "configured");
const second = JSON.parse(run(acm, ["setup"], { env }));
assert.equal(second.cursor, "already configured");
const cursor = JSON.parse(readFileSync(join(home, ".cursor", "mcp.json"), "utf8")).mcpServers.acm;
assert.ok([cursor.command, ...cursor.args].join(" ").includes("agent-cowork-memory mcp --harness cursor"));

const server = spawn(acm, ["mcp", "--harness", "claude"], { env: { ...env, ACM_HOME: join(work, "state") }, shell: win });
const tools = await new Promise((resolve, reject) => {
  let out = "";
  const timer = setTimeout(() => reject(new Error(`no tools list from acm mcp; got: ${out}`)), 30_000);
  server.stdout.on("data", (chunk) => {
    out += chunk;
    for (const line of out.split("\n")) {
      try {
        const msg = JSON.parse(line);
        if (msg.id === 2) {
          clearTimeout(timer);
          resolve(msg.result.tools.map((t) => t.name).sort());
        }
      } catch {
        // partial line
      }
    }
  });
  const send = (m) => server.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", ...m })}\n`);
  send({ id: 1, method: "initialize", params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "ci", version: "1" } } });
  send({ method: "notifications/initialized" });
  send({ id: 2, method: "tools/list" });
});
server.kill();
assert.deepEqual(tools, ["chats", "context", "delegate", "delegate_wait", "note_add", "note_search", "resume"]);
console.log("install check passed:", { setup: first, tools: tools.length });
