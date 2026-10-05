import { accessSync, constants, mkdirSync } from "node:fs";
import { join } from "node:path";
import { parseArgs } from "node:util";
import { connect, homeDir } from "./db.ts";
import { AcmError, BINARIES, isMain, now, which } from "./util.ts";

export { VERSION } from "./version.ts";

import { VERSION } from "./version.ts";

export function doctor(home: string) {
  let writable = true;
  try {
    mkdirSync(home, { recursive: true });
    accessSync(home, constants.W_OK);
  } catch {
    writable = false;
  }
  // An unwritable home is what doctor is for: report it rather than fail opening the database there.
  let fts5 = false;
  if (writable) {
    const db = connect(home);
    fts5 = Boolean(db.prepare("SELECT sqlite_compileoption_used('ENABLE_FTS5') AS on_").get()?.on_);
    db.close();
  }
  return {
    version: VERSION,
    node: process.versions.node,
    platform: process.platform,
    home,
    writable,
    fts5,
    herdr: which("herdr") !== null,
    agents: Object.fromEntries(Object.entries(BINARIES).map(([kind, bin]) => [kind, which(bin) !== null])),
  };
}

/** A consistent copy of the database, taken while other agents may be writing. */
export function backup(home: string, to?: string) {
  const dest = to ?? join(home, "backups", `${now().replaceAll(/[-:]/g, "")}.sqlite3`);
  mkdirSync(join(dest, ".."), { recursive: true });
  const db = connect(home);
  try {
    db.prepare("VACUUM INTO ?").run(dest);
  } finally {
    db.close();
  }
  return { backup: dest };
}

const USAGE = `acm ${VERSION}: shared memory and delegation for coding agents

  acm setup                     configure Codex, Cursor, OpenCode, and Claude Code to use acm
  acm mcp --harness <agent>     run the MCP server (agents start this)
  acm doctor                    check the install
  acm backup [--to <file>]      copy the database
  acm status [--repo <dir>] [--chat <id>] [--harness <agent>]
                                jobs, held files, and this chat's thread as JSON

  --home <dir>                  state folder (default ~/.agent-cowork-memory, or ACM_HOME)`;

export async function main(argv = process.argv.slice(2)): Promise<number> {
  const { values, positionals } = parseArgs({
    args: argv,
    allowPositionals: true,
    options: {
      home: { type: "string" },
      harness: { type: "string" },
      to: { type: "string" },
      repo: { type: "string" },
      chat: { type: "string" },
      help: { type: "boolean", short: "h" },
      version: { type: "boolean", short: "v" },
    },
  });
  const home = homeDir(values.home);
  process.env.ACM_HOME = home; // so debug.log, and the background jobs acm starts, use the same home
  const command = positionals[0];
  try {
    if (values.version) return print(VERSION);
    if (!command || values.help) return print(USAGE);
    if (command === "doctor") return print(doctor(home));
    if (command === "backup") return print(backup(home, values.to));
    if (command === "status") {
      const { status } = await import("./delegate.ts");
      const db = connect(home);
      try {
        return print(
          await status(db, { home, folder: values.repo ?? process.cwd(), harness: values.harness, chat: values.chat }),
        );
      } finally {
        db.close();
      }
    }
    if (command === "mcp") {
      const { serve } = await import("./mcp.ts");
      await serve(home, values.harness);
      return 0;
    }
    if (command === "setup") {
      const { setup } = await import("./setup.ts");
      return print(setup());
    }
    console.error(USAGE);
    return 2;
  } catch (err) {
    if (err instanceof AcmError) {
      console.error(JSON.stringify({ error: err.code, ...err.payload }));
      return 5;
    }
    throw err;
  }
}

function print(out: unknown): number {
  console.log(typeof out === "string" ? out : JSON.stringify(out, null, 2));
  return 0;
}

if (isMain(import.meta.url)) process.exitCode = await main();
