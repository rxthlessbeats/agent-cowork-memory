import assert from "node:assert/strict";
import {
  chmodSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  statSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { approveCodexTools, isOurs, type SetupEnv, setup, startCommand, writeJson } from "../src/setup.ts";
import { winCommand } from "../src/util.ts";

let home: string;
let calls: string[][];
let codexEntry: string[] | null;

/** Fake agents: Codex and Claude Code keep their entry where their real CLIs would. */
function fakeEnv(installed = ["npx", "codex", "opencode", "claude"]): SetupEnv {
  return {
    home,
    env: {},
    platform: "linux",
    which: (name) => (installed.includes(name) ? `/bin/${name}` : null),
    run: (cmd, args) => {
      calls.push([cmd, ...args]);
      const sub = args.slice(0, 2).join(" ");
      const toml = join(home, ".codex", "config.toml");
      if (cmd.endsWith("codex") && sub === "mcp get") {
        // Like the real Codex: what config.toml says, when there is one.
        const text = readJson(toml);
        const m = text && /\[mcp_servers\.acm\]\n(?:[^[]*\n)?command = (".*")\nargs = (\[.*\])/.exec(text);
        if (m) codexEntry = [JSON.parse(m[1]), ...JSON.parse(m[2])];
        return codexEntry
          ? { status: 0, stdout: JSON.stringify({ transport: { command: codexEntry[0], args: codexEntry.slice(1) } }) }
          : { status: 1, stdout: "" };
      }
      if (cmd.endsWith("codex") && sub === "mcp add") {
        codexEntry = args.slice(args.indexOf("--") + 1);
        mkdirSync(join(home, ".codex"), { recursive: true });
        const kept = (readJson(toml) ?? "").replace(/\[mcp_servers\.acm\][^[]*/, "");
        writeFileSync(
          toml,
          `${kept}[mcp_servers.acm]\ncommand = ${JSON.stringify(codexEntry[0])}\nargs = ${JSON.stringify(codexEntry.slice(1))}\n`,
        );
      }
      if (cmd.endsWith("codex") && sub === "mcp remove") {
        codexEntry = null;
        const text = readJson(toml);
        if (text !== null) writeFileSync(toml, text.replace(/\[mcp_servers\.acm(\.[^\]]*)?\][^[]*/g, ""));
      }
      if (cmd.endsWith("claude")) {
        const file = join(home, ".claude.json");
        const config = JSON.parse(readJson(file) ?? "{}");
        config.mcpServers ??= {};
        if (sub === "mcp add") {
          const cmdline = args.slice(args.indexOf("--") + 1);
          config.mcpServers.acm = { type: "stdio", command: cmdline[0], args: cmdline.slice(1) };
        }
        if (sub === "mcp remove") delete config.mcpServers.acm;
        writeFileSync(file, JSON.stringify(config));
      }
      return { status: 0, stdout: "" };
    },
  };
}

function readJson(path: string): string | null {
  try {
    return readFileSync(path, "utf8");
  } catch {
    return null;
  }
}

const npx = (h: string) => startCommand("/bin/npx", h, "linux");

beforeEach(() => {
  home = mkdtempSync(join(tmpdir(), "acm-setup-"));
  calls = [];
  codexEntry = null;
});

afterEach(() => rmSync(home, { recursive: true, force: true, maxRetries: 5, retryDelay: 50 }));

test("setup configures all four agents through npx, keeps other servers, and a second run changes nothing", () => {
  mkdirSync(join(home, ".cursor"));
  writeFileSync(join(home, ".cursor", "mcp.json"), JSON.stringify({ mcpServers: { other: { command: "other" } } }));
  assert.deepEqual(setup(fakeEnv()), {
    codex: "configured; acm's tools approved",
    cursor: "configured",
    opencode: "configured",
    claude: "configured",
  });
  assert.deepEqual(codexEntry, npx("codex"));
  const cursor = JSON.parse(readFileSync(join(home, ".cursor", "mcp.json"), "utf8")).mcpServers;
  assert.deepEqual(cursor.other, { command: "other" });
  assert.deepEqual([cursor.acm.command, ...cursor.acm.args], npx("cursor"));
  const opencode = JSON.parse(readFileSync(join(home, ".config", "opencode", "opencode.json"), "utf8")).mcp.acm;
  assert.deepEqual(opencode, { type: "local", command: npx("opencode"), enabled: true });
  assert.ok(calls.some((c) => c.join(" ") === `/bin/claude mcp add -s user acm -- ${npx("claude").join(" ")}`));
  assert.deepEqual(npx("claude").slice(1, 5), [
    "-y",
    "--fetch-retries=0",
    "--fetch-timeout=3000",
    "agent-cowork-memory",
  ]);

  calls = [];
  const again = setup(fakeEnv());
  assert.deepEqual(Object.values(again), [
    "already configured",
    "already configured",
    "already configured",
    "already configured",
  ]);
  assert.ok(!calls.some((c) => c.includes("add") || c.includes("remove")));
});

test("setup replaces 0.2.4's uvx entries in all four agents, and leaves someone else's acm alone", () => {
  const uvx = (h: string) => ["/home/u/.local/bin/uvx", "agent-cowork-memory", "mcp", "--harness", h];
  codexEntry = uvx("codex");
  mkdirSync(join(home, ".cursor"));
  writeFileSync(
    join(home, ".cursor", "mcp.json"),
    JSON.stringify({ mcpServers: { acm: { command: uvx("cursor")[0], args: uvx("cursor").slice(1) } } }),
  );
  mkdirSync(join(home, ".config", "opencode"), { recursive: true });
  writeFileSync(
    join(home, ".config", "opencode", "opencode.json"),
    JSON.stringify({ mcp: { acm: { type: "local", command: ["/usr/bin/other-acm", "serve"] } } }),
  );
  writeFileSync(
    join(home, ".claude.json"),
    JSON.stringify({
      mcpServers: { acm: { type: "stdio", command: "/venv/bin/acm", args: ["mcp", "--harness", "claude"] } },
    }),
  );
  const out = setup(fakeEnv());
  assert.match(out.codex, /^updated \(was: .*uvx agent-cowork-memory/);
  assert.match(out.cursor, /^updated/);
  assert.match(out.claude, /^updated \(was: \/venv\/bin\/acm mcp/);
  assert.match(out.opencode, /^not changed: its acm entry runs \/usr\/bin\/other-acm serve/);
  assert.deepEqual(codexEntry, npx("codex"));
  assert.ok(calls.some((c) => c.join(" ") === "/bin/codex mcp remove acm"));
  assert.ok(calls.some((c) => c.join(" ") === "/bin/claude mcp remove acm -s user"));
  assert.deepEqual(
    JSON.parse(readFileSync(join(home, ".config", "opencode", "opencode.json"), "utf8")).mcp.acm.command,
    ["/usr/bin/other-acm", "serve"],
  );
});

test("replacing Codex's entry keeps the per-tool approvals under it", () => {
  const file = join(home, ".codex", "config.toml");
  mkdirSync(join(home, ".codex"));
  writeFileSync(
    file,
    [
      'model = "x"',
      "",
      "[mcp_servers.acm]",
      'command = "/home/u/.local/bin/acm"',
      'args = ["mcp", "--harness", "codex"]',
      "",
      "[mcp_servers.acm.tools.context]",
      'approval_mode = "approve"',
      "",
      "[mcp_servers.other]",
      'command = "other"',
      "",
    ].join("\n"),
  );
  codexEntry = ["/home/u/.local/bin/acm", "mcp", "--harness", "codex"];
  const out = setup(fakeEnv());
  assert.match(out.codex, /^updated \(was: \/home\/u\/.local\/bin\/acm mcp --harness codex\); acm's tools approved$/);
  const edited = readFileSync(file, "utf8");
  assert.ok(edited.includes(`command = "${npx("codex")[0]}"`));
  assert.ok(edited.includes(`args = ${JSON.stringify(npx("codex").slice(1))}`));
  assert.ok(edited.includes('[mcp_servers.acm.tools.context]\napproval_mode = "approve"'));
  assert.ok(edited.includes('[mcp_servers.other]\ncommand = "other"'));
  assert.ok(!calls.some((c) => c.includes("remove")));
});

test("setup lets Codex run every acm tool without asking, once, and keeps a setting the user chose", () => {
  assert.equal(setup(fakeEnv()).codex, "configured; acm's tools approved");
  const toml = join(home, ".codex", "config.toml");
  assert.match(readFileSync(toml, "utf8"), /\[mcp_servers\.acm\]\ndefault_tools_approval_mode = "approve"\n/);
  assert.equal(setup(fakeEnv()).codex, "already configured");
  writeFileSync(toml, readFileSync(toml, "utf8").replace('"approve"', '"prompt"'));
  setup(fakeEnv());
  assert.match(readFileSync(toml, "utf8"), /default_tools_approval_mode = "prompt"/);
});

test("a failed agent command is reported as failed, with the command to run, never as configured", () => {
  writeFileSync(
    join(home, ".claude.json"),
    JSON.stringify({ mcpServers: { acm: { command: "/venv/bin/acm", args: ["mcp", "--harness", "claude"] } } }),
  );
  const env = fakeEnv();
  const run = env.run;
  env.run = (cmd, args) => {
    const sub = args.slice(0, 2).join(" ");
    if (sub === "mcp add") {
      calls.push([cmd, ...args]);
      return { status: cmd.endsWith("claude") ? null : 1, stdout: "", stderr: "boom: config is locked\nmore" };
    }
    if (cmd.endsWith("codex") && sub === "mcp get") return { status: 0, stdout: "warning: not json" };
    return run(cmd, args);
  };
  const out = setup(env);
  assert.match(
    out.codex,
    /^failed: `codex mcp add` exited with 1 \(boom: config is locked\)\. Run it yourself: codex mcp add acm -- /,
  );
  assert.match(
    out.claude,
    /^failed: `claude mcp add` timed out .*; the old acm entry is already removed\. Run it yourself: claude mcp add -s user acm -- /,
  );
  assert.equal(out.cursor, "configured");
});

test("on Windows a command line quotes every part, so a path with a space stays one program", () => {
  assert.equal(
    winCommand("C:\\Users\\John Smith\\npm\\codex.cmd", ["mcp", "get", "acm"]),
    '"C:\\Users\\John Smith\\npm\\codex.cmd" "mcp" "get" "acm"',
  );
});

test("a config symlinked onto another folder is rewritten at its target (Codex edits too)", () => {
  mkdirSync(join(home, "dotfiles"));
  mkdirSync(join(home, ".codex"));
  const target = join(home, "dotfiles", "config.toml");
  writeFileSync(target, '[mcp_servers.acm]\ncommand = "/old/acm"\nargs = ["mcp"]\n');
  symlinkSync(target, join(home, ".codex", "config.toml"));
  assert.ok(approveCodexTools(join(home, ".codex", "config.toml")));
  assert.match(readFileSync(target, "utf8"), /default_tools_approval_mode = "approve"/);
  assert.ok(lstatSync(join(home, ".codex", "config.toml")).isSymbolicLink());
  assert.deepEqual(readdirSync(join(home, ".codex")), ["config.toml"]); // no temp file left beside the link
});

test("agents that aren't installed are skipped; without npx setup says what to install", () => {
  assert.deepEqual(setup(fakeEnv(["npx"])), {
    codex: "not installed",
    cursor: "configured",
    opencode: "not installed",
    claude: "not installed",
  });
  assert.throws(() => setup(fakeEnv([])), /install Node 24/);
});

test("an OpenCode .jsonc with comments is never rewritten; without comments it is used", () => {
  const folder = join(home, ".config", "opencode");
  mkdirSync(folder, { recursive: true });
  const jsonc = join(folder, "opencode.jsonc");
  writeFileSync(jsonc, '{\n  // my theme\n  "theme": "dark"\n}\n');
  assert.match(setup(fakeEnv()).opencode, /^not changed: .* has comments/);
  assert.match(readFileSync(jsonc, "utf8"), /\/\/ my theme/);
  writeFileSync(jsonc, '{"theme": "dark"}\n');
  assert.equal(setup(fakeEnv()).opencode, "configured");
  assert.ok(JSON.parse(readFileSync(jsonc, "utf8")).mcp.acm);
});

test("a symlinked config is written at its target, keeping its permissions", () => {
  const target = join(home, "dotfiles.json");
  const link = join(home, "opencode.json");
  writeFileSync(target, "{}");
  chmodSync(target, 0o644);
  const mode = statSync(target).mode & 0o777;
  symlinkSync(target, link);
  writeJson(link, { mcp: {} });
  assert.deepEqual(JSON.parse(readFileSync(target, "utf8")), { mcp: {} });
  // Windows only keeps the write bit, so 0o644 may come back as 0o666. What matters is the rewrite didn't change it.
  assert.equal(statSync(target).mode & 0o777, mode);
});

test("ours is any agent-cowork-memory or acm mcp entry; Windows starts npx through cmd", () => {
  assert.ok(isOurs(["/x/uvx", "agent-cowork-memory", "mcp"]));
  assert.ok(isOurs(["/venv/bin/acm", "mcp", "--harness", "codex"]));
  assert.ok(!isOurs(["/usr/bin/other-acm", "serve"]));
  assert.deepEqual(startCommand("C:\\npx.cmd", "codex", "win32").slice(0, 3), ["cmd", "/c", "npx"]);
});
