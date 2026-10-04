import { spawnSync } from "node:child_process";
import {
  chmodSync,
  existsSync,
  mkdirSync,
  readFileSync,
  realpathSync,
  renameSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";
import { obj, text } from "./readers/index.ts";
import { AcmError, which, winCommand } from "./util.ts";

export type SetupEnv = {
  home: string;
  env: NodeJS.ProcessEnv;
  platform: NodeJS.Platform;
  which: (name: string) => string | null;
  run: (cmd: string, args: string[]) => Ran;
};
type Ran = { status: number | null; stdout: string; stderr?: string };

export function realEnv(): SetupEnv {
  return {
    home: homedir(),
    env: process.env,
    platform: process.platform,
    which,
    run: (cmd, args) => {
      // Windows: the agents' CLIs are .cmd shims, so they go through cmd.exe, quoted so paths with spaces work.
      const out =
        process.platform === "win32"
          ? spawnSync(winCommand(cmd, args), { encoding: "utf8", timeout: 30_000, shell: true })
          : spawnSync(cmd, args, { encoding: "utf8", timeout: 30_000 });
      return { status: out.status, stdout: out.stdout ?? "", stderr: out.stderr ?? "" };
    },
  };
}

/** How an agent starts acm: through npx, so a new release is picked up on the next start. The two fetch flags
 * make an offline start use the cached copy in half a second instead of retrying for a minute. */
export function startCommand(npx: string, harness: string, platform: NodeJS.Platform): string[] {
  const rest = ["-y", "--fetch-retries=0", "--fetch-timeout=3000", "agent-cowork-memory", "mcp", "--harness", harness];
  // On Windows npx is a .cmd shim, which agents can only start through cmd.
  return platform === "win32" ? ["cmd", "/c", "npx", ...rest] : [npx, ...rest];
}

/** An acm entry that runs agent-cowork-memory in any form (npx, uvx, a pip install's acm): ours to replace. */
export function isOurs(cmd: string[]): boolean {
  return (
    cmd.join(" ").includes("agent-cowork-memory") ||
    (/^acm(\.exe|\.cmd)?$/.test(basename(cmd[0] ?? "")) && cmd.includes("mcp"))
  );
}

const same = (a: string[], b: string[]) => a.length === b.length && a.every((x, i) => x === b[i]);

/** Replace the file in one step, so an interrupted setup never leaves half a config.
 * A symlinked config is written at its target, with the target's permissions. */
export function writeAtomic(path: string, content: string): void {
  const target = existsSync(path) ? realpathSync(path) : path;
  mkdirSync(dirname(target), { recursive: true });
  // Beside the target, not the link: a rename can't cross file systems.
  const temporary = `${target}.acm-${process.pid}.tmp`;
  writeFileSync(temporary, content);
  if (existsSync(target)) chmodSync(temporary, statSync(target).mode & 0o777);
  renameSync(temporary, target);
}

export function writeJson(path: string, data: unknown): void {
  writeAtomic(path, `${JSON.stringify(data, null, 2)}\n`);
}

/** What to tell the user when an agent's own command didn't work, with the command to run by hand. */
function failure(command: string[], ran: Ran, after = ""): Outcome {
  const why = ran.status === null ? "timed out" : `exited with ${ran.status}`;
  const said = (ran.stderr ?? "").trim().split("\n")[0];
  return `failed: \`${command.slice(0, 3).join(" ")}\` ${why}${said ? ` (${said})` : ""}${after}. Run it yourself: ${command.join(" ")}`;
}

type Outcome = string;

function decide(existing: string[] | null, wanted: string[], what: string): "add" | "replace" | Outcome {
  if (!existing) return "add";
  if (same(existing, wanted)) return "already configured";
  if (isOurs(existing)) return "replace";
  return `not changed: its acm entry runs ${existing.join(" ")}, not agent-cowork-memory; remove it from ${what} to use this one`;
}

function jsonConfig(
  file: string,
  key: string,
  wanted: string[],
  entry: (cmd: string[]) => unknown,
  read: (e: unknown) => string[],
): Outcome {
  let config: Record<string, unknown> = {};
  if (existsSync(file)) {
    try {
      config = obj(JSON.parse(readFileSync(file, "utf8")));
    } catch {
      if (!file.endsWith(".jsonc")) throw new AcmError("invalid", `Invalid MCP config: ${file}`);
      return `not changed: ${file} has comments, which setup would lose. Add this under "${key}" yourself: "acm": ${JSON.stringify(entry(wanted))}`;
    }
  }
  const servers = obj(config[key]);
  const current = servers.acm === undefined ? null : read(servers.acm);
  const step = decide(current, wanted, file);
  if (step !== "add" && step !== "replace") return step;
  writeJson(file, { ...config, [key]: { ...servers, acm: entry(wanted) } });
  return step === "add" ? "configured" : `updated (was: ${current?.join(" ")})`;
}

/** Point Codex's acm entry at a new command by rewriting only its command and args lines, so the tables under
 * it (per-tool approvals) stay. False when the entry isn't in that simple form. TOML takes JSON strings and arrays. */
export function editCodexEntry(file: string, cmd: string[]): boolean {
  let text: string;
  try {
    text = readFileSync(file, "utf8");
  } catch {
    return false;
  }
  const lines = text.split("\n");
  const start = lines.findIndex((l) => l.trim() === "[mcp_servers.acm]");
  if (start < 0) return false;
  const next = lines.findIndex((l, i) => i > start && /^\s*\[/.test(l));
  const end = next < 0 ? lines.length : next;
  const at = (re: RegExp) => lines.findIndex((l, i) => i > start && i < end && re.test(l));
  const command = at(/^\s*command\s*=/);
  const args = at(/^\s*args\s*=\s*\[.*\]\s*$/);
  if (command < 0 || args < 0) return false;
  lines[command] = `command = ${JSON.stringify(cmd[0])}`;
  lines[args] = `args = ${JSON.stringify(cmd.slice(1))}`;
  writeAtomic(file, lines.join("\n"));
  return true;
}

/** Let Codex run every acm tool without asking: one setting on acm's entry, which also covers tools acm adds
 * later. An approval setting already there, whatever its value, is the user's and stays. True if it was added. */
export function approveCodexTools(file: string): boolean {
  let text: string;
  try {
    text = readFileSync(file, "utf8");
  } catch {
    return false;
  }
  const lines = text.split("\n");
  const start = lines.findIndex((l) => l.trim() === "[mcp_servers.acm]");
  if (start < 0) return false;
  const next = lines.findIndex((l, i) => i > start && /^\s*\[/.test(l));
  const end = next < 0 ? lines.length : next;
  if (lines.slice(start + 1, end).some((l) => /^\s*default_tools_approval_mode\s*=/.test(l))) return false;
  lines.splice(start + 1, 0, 'default_tools_approval_mode = "approve"');
  writeAtomic(file, lines.join("\n"));
  return true;
}

export function setup(env: SetupEnv = realEnv()): Record<string, Outcome> {
  const npx = env.which("npx");
  if (!npx) throw new AcmError("unavailable", "npx was not found; install Node 24 or newer, then run setup again");
  const want = (h: string) => startCommand(npx, h, env.platform);
  const result: Record<string, Outcome> = {};

  // Codex: read and add through its own CLI. A replacement edits config.toml in place instead, because
  // `codex mcp remove` would also drop the per-tool approvals the user gave acm.
  const codex = env.which("codex");
  if (!codex) result.codex = "not installed";
  else {
    const got = env.run(codex, ["mcp", "get", "acm", "--json"]);
    let transport: Record<string, unknown> | null = null;
    try {
      transport = got.status === 0 ? obj(obj(JSON.parse(got.stdout || "{}")).transport) : null;
    } catch {
      // not JSON (an older Codex, or a warning on stdout): treated as no entry; `mcp add` below reports a clash
    }
    const current = transport ? [text(transport.command), ...((transport.args as string[]) ?? [])] : null;
    const step = decide(current, want("codex"), "Codex (codex mcp remove acm)");
    const file = join(env.env.CODEX_HOME || join(env.home, ".codex"), "config.toml");
    const add = ["codex", "mcp", "add", "acm", "--", ...want("codex")];
    let note = "";
    let failed = "";
    if (step === "replace" && !editCodexEntry(file, want("codex"))) {
      const removed = env.run(codex, ["mcp", "remove", "acm"]);
      if (removed.status !== 0) failed = failure(["codex", "mcp", "remove", "acm"], removed);
      note = "; its per-tool approvals were reset";
    }
    if (!failed && (step === "add" || (step === "replace" && note))) {
      const added = env.run(codex, add.slice(1));
      if (added.status !== 0) failed = failure(add, added, note ? "; the old acm entry is already removed" : "");
    }
    result.codex =
      failed ||
      (step === "add" ? "configured" : step === "replace" ? `updated (was: ${current?.join(" ")})${note}` : step);
    // Without this, headless Codex fails every acm call and interactive Codex asks before each one.
    if (!failed && !step.startsWith("not changed") && approveCodexTools(file)) {
      result.codex =
        result.codex === "already configured" ? "acm's tools approved" : `${result.codex}; acm's tools approved`;
    }
  }

  // Cursor: always, since the IDE reads this file even without cursor-agent on PATH.
  result.cursor = jsonConfig(
    join(env.home, ".cursor", "mcp.json"),
    "mcpServers",
    want("cursor"),
    (cmd) => ({ command: cmd[0], args: cmd.slice(1) }),
    (e) => [text(obj(e).command), ...((obj(e).args as string[]) ?? [])],
  );

  // OpenCode: its own JSON config, or the .jsonc one if that is what exists.
  if (!env.which("opencode")) result.opencode = "not installed";
  else {
    const folder = join(env.home, ".config", "opencode");
    const file =
      env.env.OPENCODE_CONFIG ||
      [join(folder, "opencode.json"), join(folder, "opencode.jsonc")].find((p) => existsSync(p)) ||
      join(folder, "opencode.json");
    result.opencode = jsonConfig(
      file,
      "mcp",
      want("opencode"),
      (cmd) => ({ type: "local", command: cmd, enabled: true }),
      (e) => (obj(e).command as string[]) ?? [],
    );
  }

  // Claude Code: read its user config to see what is there; change it only through its CLI, which owns the file.
  const claude = env.which("claude");
  if (!claude) result.claude = "not installed";
  else {
    const file = join(env.env.CLAUDE_CONFIG_DIR || env.home, ".claude.json");
    let entry: Record<string, unknown> | undefined;
    try {
      entry = obj(obj(JSON.parse(readFileSync(file, "utf8"))).mcpServers).acm as Record<string, unknown> | undefined;
    } catch {
      entry = undefined;
    }
    const current = entry ? [text(entry.command), ...((entry.args as string[]) ?? [])] : null;
    const step = decide(current, want("claude"), "Claude Code (claude mcp remove acm -s user)");
    const add = ["claude", "mcp", "add", "-s", "user", "acm", "--", ...want("claude")];
    let failed = "";
    if (step === "replace") {
      const removed = env.run(claude, ["mcp", "remove", "acm", "-s", "user"]);
      if (removed.status !== 0) failed = failure(["claude", "mcp", "remove", "acm", "-s", "user"], removed);
    }
    if (!failed && (step === "add" || step === "replace")) {
      const added = env.run(claude, add.slice(1));
      if (added.status !== 0) {
        failed = failure(add, added, step === "replace" ? "; the old acm entry is already removed" : "");
      }
    }
    result.claude =
      failed || (step === "add" ? "configured" : step === "replace" ? `updated (was: ${current?.join(" ")})` : step);
  }
  return result;
}
