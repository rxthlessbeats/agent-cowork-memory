import { randomBytes } from "node:crypto";
import { appendFileSync, existsSync, realpathSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

/** The program each agent kind runs as. */
export const BINARIES: Record<string, string> = {
  codex: "codex",
  claude: "claude",
  cursor: "cursor-agent",
  opencode: "opencode",
};

/** The full path of a program on PATH, or null. */
export function which(name: string): string | null {
  const win = process.platform === "win32";
  const exts = win ? (process.env.PATHEXT ?? ".EXE;.CMD").split(";") : [""];
  for (const dir of (process.env.PATH ?? "").split(win ? ";" : ":")) {
    for (const ext of exts) {
      const path = join(dir, name + ext);
      try {
        if (dir && existsSync(path) && statSync(path).isFile()) return path;
      } catch {
        // unreadable entry on PATH: skip it
      }
    }
  }
  return null;
}

/** True when this module is the script Node was started with. `import.meta.main` only exists from Node 24.2. */
export function isMain(url: string): boolean {
  try {
    return Boolean(process.argv[1]) && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(url));
  } catch {
    return false;
  }
}

/** A program and its arguments as one cmd.exe command line, each part quoted, so paths with spaces work.
 * On Windows npm-installed CLIs are .cmd shims, which only cmd.exe can start. */
export function winCommand(program: string, args: string[]): string {
  return [program, ...args].map((a) => `"${a.replaceAll('"', '\\"')}"`).join(" ");
}

/** An error an agent can act on: `code` plus fields, sent back as `{"error": code, ...}`. */
export class AcmError extends Error {
  readonly code: string;
  readonly payload: Record<string, unknown>;
  constructor(code: string, message: string, payload: Record<string, unknown> = {}) {
    super(message);
    this.code = code;
    this.payload = { message, ...payload };
  }
}

/** UTC to the second, the format every stored time uses. */
export function now(date = new Date()): string {
  return `${date.toISOString().slice(0, 19)}Z`;
}

export function daysAgo(days: number): string {
  return now(new Date(Date.now() - days * 86_400_000));
}

export function inDays(days: number): string {
  return daysAgo(-days);
}

export function newId(prefix: string): string {
  return prefix + randomBytes(6).toString("hex");
}

/** With ACM_DEBUG set, how long something took, appended to debug.log in acm's home. For diagnosing timeouts. */
export function debug(what: string, since: number): void {
  if (!process.env.ACM_DEBUG) return;
  const home = process.env.ACM_HOME || join(homedir(), ".agent-cowork-memory");
  const took = ((performance.now() - since) / 1000).toFixed(2);
  appendFileSync(join(home, "debug.log"), `${now()} ${process.pid} ${what} ${took}s\n`);
}

/** Whitespace collapsed, cut to `width` with an ellipsis. */
export function oneLine(text: string | null | undefined, width = 200): string {
  const flat = (text ?? "").split(/\s+/).filter(Boolean).join(" ");
  return flat.length <= width ? flat : `${flat.slice(0, width - 1)}…`;
}
