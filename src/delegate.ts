/** Start other agents, send each a brief, and wait for them: in herdr panes if herdr is installed, else in the background. */
import { execFile, spawn, spawnSync } from "node:child_process";
import {
  closeSync,
  existsSync,
  mkdirSync,
  openSync,
  readdirSync,
  readFileSync,
  readSync,
  statSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { homedir } from "node:os";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";
import { type Db, transaction } from "./db.ts";
import { addEvent, ensureThread, held, OPEN_JOB, releaseHolds, type Session } from "./memory.ts";
import { canonical, isHomeOrRoot, projectRoot } from "./project.ts";
import { type Json, obj, text } from "./readers/index.ts";
import { chatBytes, chatExists, parse, READERS, type Roots, rootOf } from "./transcript.ts";
import { AcmError, BINARIES, debug, newId, now, oneLine, which } from "./util.ts";

export const SESSION = "acm";
export const FLAGS: Record<string, string[]> = {
  codex: ["--approve-for-me", "-c", "check_for_update_on_startup=false"],
  claude: ["--permission-mode", "auto"],
  cursor: ["--auto-review", "--trust", "--approve-mcps"],
  opencode: ["--auto"],
};
export const WAIT_SECONDS = 45;
/** How long a delegate's reservation of an agent holds if that delegate never finishes (it crashed). */
const RESERVED = 120;
const START_SECONDS = 30; // agent starts; the rest of WAIT_SECONDS is for briefs, all under a 60 s tool timeout
const POLL_SECONDS = 2;
const JOB_FILE_DAYS = 7; // ponytail: output files of finished jobs are kept this long, for debugging
export const LIMITS = {
  resendAfter: 10, // seconds before a brief an idle agent never shows is sent again
  lostAfter: 60, // seconds after which a brief sent twice and still missing counts as lost
  jobSeconds: 15 * 60, // ponytail: a background job still running after this is stopped; one can wait on a prompt forever
};
export const WATCH = `herdr session attach ${SESSION}`;
export const BACKGROUND = "background";
const FINISHED = ["done", "gone", "needs_approval"];
const OPEN_SQL = OPEN_JOB.map((s) => `'${s}'`).join(", ");
const ASKS = /^\W*BLOCKED:[ \t]*(.*)$/m;

export class HerdrError extends Error {
  readonly code: string;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export type Deps = {
  herdr: (args: string[], raw?: boolean) => Promise<Json | string>;
  startServer: () => void;
  useHerdr: () => boolean;
  spawnJob: (base: string, cmd: string[], folder: string) => void;
  installed: (binary: string) => boolean;
  sleep: (seconds: number) => Promise<void>;
  clock: () => number;
  roots: Roots;
};

export function runHerdr(args: string[], raw = false): Promise<Json | string> {
  const t0 = performance.now();
  return new Promise<Json | string>((resolve, reject) => {
    execFile("herdr", ["--session", SESSION, ...args], { maxBuffer: 16 * 1024 * 1024 }, (err, stdout, stderr) => {
      if (err && (err as NodeJS.ErrnoException).code === "ENOENT") {
        reject(new AcmError("unavailable", "herdr is not installed; see https://herdr.dev"));
        return;
      }
      if (raw && !err) {
        resolve(stdout);
        return;
      }
      const lines = (stdout.trim() || stderr.trim()).split("\n");
      let data: Json = {};
      try {
        data = lines.length && lines[0] ? obj(JSON.parse(lines[lines.length - 1])) : {};
      } catch {
        reject(new AcmError("unavailable", `herdr: ${lines[lines.length - 1].slice(0, 200)}`));
        return;
      }
      if (data.error) {
        const e = obj(data.error);
        reject(new HerdrError(text(e.code), text(e.message)));
        return;
      }
      resolve(obj(data.result));
    });
  }).finally(() => debug(`herdr ${args.slice(0, 3).join(" ")}`, t0));
}

/** Start the background wrapper, detached so the job outlives this server. */
export function spawnJob(base: string, cmd: string[], folder: string): void {
  const self = import.meta.url.endsWith(".ts") ? "job.ts" : "job.js";
  const child = spawn(process.execPath, [fileURLToPath(new URL(self, import.meta.url)), base, ...cmd], {
    cwd: folder,
    detached: true,
    stdio: "ignore",
    windowsHide: true,
    env: { ...process.env, ACM_DELEGATED: "1" },
  });
  // A wrapper that can't start (out of processes, say) ends the job with that error instead of ending this server.
  child.on("error", (err) => {
    writeFileSync(`${base}.log`, `acm could not start the job: ${err.message}\n`, { flag: "a" });
    writeFileSync(`${base}.exit`, "1\n");
  });
  writeFileSync(`${base}.pid`, String(child.pid ?? ""));
  child.unref();
}

export function defaultDeps(roots: Roots = {}): Deps {
  return {
    herdr: runHerdr,
    // A server that can't start shows up as herdr still not answering, which ensureServer reports.
    startServer: () =>
      spawn("herdr", ["--session", SESSION, "server"], { detached: true, stdio: "ignore", windowsHide: true })
        .on("error", () => {})
        .unref(),
    useHerdr: () => which("herdr") !== null,
    spawnJob,
    installed: (binary) => which(binary) !== null,
    sleep: (s) => new Promise((r) => setTimeout(r, s * 1000)),
    clock: () => performance.now() / 1000,
    roots,
  };
}

// ---- herdr ----

async function herdr(deps: Deps, ...args: string[]): Promise<Json> {
  return obj(await deps.herdr(args));
}

async function ensureServer(deps: Deps): Promise<void> {
  try {
    await herdr(deps, "workspace", "list");
    return;
  } catch (err) {
    if (!(err instanceof HerdrError) || err.code !== "server_not_running") {
      throw err instanceof HerdrError ? new AcmError("unavailable", `herdr: ${err.message}`) : err;
    }
  }
  deps.startServer();
  for (let i = 0; i < 50; i++) {
    await deps.sleep(0.1);
    try {
      await herdr(deps, "workspace", "list");
      return;
    } catch {
      // still starting
    }
  }
  throw new AcmError("unavailable", `could not start herdr; run: ${WATCH}`);
}

function panes(list: Json): Json[] {
  return (Array.isArray(list.panes) ? list.panes : []).map(obj);
}

/** [workspace id, its fresh empty root pane or null]. */
async function workspaceFor(deps: Deps, folder: string): Promise<[string, string | null]> {
  for (const pane of panes(await herdr(deps, "pane", "list"))) {
    if (pane.cwd === folder) return [text(pane.workspace_id), null];
  }
  const made = await herdr(
    deps,
    "workspace",
    "create",
    "--cwd",
    folder,
    "--label",
    basename(folder),
    "--env",
    "ACM_DELEGATED=1",
    "--no-focus",
  );
  return [text(obj(made.workspace).workspace_id), text(obj(made.root_pane).pane_id)];
}

/** A pane for a new agent. A tab holds two panes side by side, so agents stay wide enough to draw.
 * OpenCode gets a tab to itself, and its tab is never split: in a half-width pane it crashes
 * (a Bun segfault, OpenCode 1.18 on Bun 1.3). solo holds the panes this call gave OpenCode. */
async function newPane(
  deps: Deps,
  workspace: string,
  folder: string,
  kind: string,
  solo: Set<string>,
): Promise<string> {
  const mine = panes(await herdr(deps, "pane", "list")).filter((p) => p.workspace_id === workspace);
  const perTab = new Map<string, number>();
  for (const p of mine) perTab.set(text(p.tab_id), (perTab.get(text(p.tab_id)) ?? 0) + 1);
  const lone =
    kind !== "opencode" &&
    mine.find((p) => perTab.get(text(p.tab_id)) === 1 && !solo.has(text(p.pane_id)) && p.agent !== "opencode");
  const where = ["--cwd", folder, "--env", "ACM_DELEGATED=1", "--no-focus"];
  if (lone)
    return text(
      obj((await herdr(deps, "pane", "split", text(lone.pane_id), "--direction", "right", ...where)).pane).pane_id,
    );
  return text(
    obj((await herdr(deps, "tab", "create", "--workspace", workspace, "--label", basename(folder), ...where)).root_pane)
      .pane_id,
  );
}

export function agentName(kind: string, folder: string): string {
  const s =
    basename(folder)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "folder";
  return `${kind}-${s}`.slice(0, 32).replace(/-+$/, "");
}

async function agents(deps: Deps): Promise<Map<string, Json>> {
  if (!deps.useHerdr()) return new Map();
  let list: Json;
  try {
    list = await herdr(deps, "agent", "list");
  } catch (err) {
    if (!(err instanceof HerdrError)) throw err;
    // The herdr server stopped (a reboot, herdr server stop): its agents went with it. Start it again, so the
    // jobs are checked against what is left and reported, rather than every wait failing.
    if (err.code !== "server_not_running") throw new AcmError("unavailable", `herdr: ${err.message}`);
    await ensureServer(deps);
    list = await herdr(deps, "agent", "list");
  }
  const all = (Array.isArray(list.agents) ? list.agents : []).map(obj);
  return new Map(all.map((a) => [a.name ? text(a.name) : `pane:${text(a.pane_id)}`, a]));
}

/** The last lines with text. Full-screen agents leave the bottom rows blank, so read well past them. */
async function paneTail(deps: Deps, pane: string, lines = 12): Promise<string> {
  try {
    const out = await deps.herdr(
      ["pane", "read", pane, "--source", "recent-unwrapped", "--lines", String(lines * 8)],
      true,
    );
    return String(out)
      .split("\n")
      .filter((l) => l.trim())
      .slice(-lines)
      .join("\n")
      .slice(-800);
  } catch {
    return "";
  }
}

/** Hand an agent its brief: [state, result]. One agent herdr can't prompt must not stop the others. */
async function send(deps: Deps, name: string, prompt: string, pane: string): Promise<[string, string | null]> {
  try {
    await herdr(deps, "agent", "prompt", name, prompt);
  } catch (err) {
    if (err instanceof HerdrError && err.code === "agent_blocked") return ["starting", null];
    if (!(err instanceof HerdrError)) throw err;
    return [
      "gone",
      `herdr could not give ${name} its brief: ${err.message}. Last lines: ${(await paneTail(deps, pane)) || "(none)"}`,
    ];
  }
  return ["running", null];
}

// ---- background ----

function jobsDir(home: string): string {
  return join(home, "jobs");
}

function cleanJobs(db: Db, home: string): void {
  const folder = jobsDir(home);
  if (!existsSync(folder)) return;
  const open = new Set(
    (db.prepare(`SELECT id FROM jobs WHERE state IN (${OPEN_SQL})`).all() as Json[]).map((r) => text(r.id)),
  );
  const cutoff = Date.now() - JOB_FILE_DAYS * 86_400_000;
  for (const name of readdirSync(folder)) {
    const path = join(folder, name);
    try {
      if (!open.has(name.split(".")[0]) && statSync(path).mtimeMs < cutoff) unlinkSync(path);
    } catch {
      // another acm process cleaned it first
    }
  }
}

/** The command for an agent in print mode. The brief goes on stdin, which all four take. */
function headless(kind: string, folder: string, answer: string): string[] {
  return {
    codex: ["codex", "exec", ...FLAGS.codex, "--skip-git-repo-check", "--cd", folder, "-o", answer, "-"],
    claude: ["claude", "-p", ...FLAGS.claude, "--permission-prompts", "none"],
    cursor: ["cursor-agent", "-p", ...FLAGS.cursor],
    opencode: ["opencode", "run", ...FLAGS.opencode, "--dir", folder],
  }[kind] as string[];
}

function readText(path: string): string {
  try {
    return readFileSync(path, "utf8").trim();
  } catch {
    return "";
  }
}

/** End a background job's whole process tree. True once it is gone. */
function stopJob(base: string): boolean {
  const pid = Number(readText(`${base}.pid`));
  if (!pid) return false;
  try {
    if (process.platform === "win32") {
      // Waited for: a taskkill that can't start is a result here, not an error event that ends this process.
      // 128: no such process, so it is gone already.
      const killed = spawnSync("taskkill", ["/PID", String(pid), "/T", "/F"], { stdio: "ignore", windowsHide: true });
      return killed.status === 0 || killed.status === 128;
    }
    process.kill(-pid, "SIGKILL");
    return true;
  } catch (err) {
    return (err as NodeJS.ErrnoException).code === "ESRCH";
  }
}

function age(job: Json): number {
  return (Date.now() - Date.parse(text(job.started_at))) / 1000;
}

function checkBackground(home: string, job: Json): [string, string | null] {
  const base = join(jobsDir(home), text(job.id));
  const exit = readText(`${base}.exit`);
  if (!exit) {
    if (age(job) <= LIMITS.jobSeconds || !stopJob(base)) return ["running", null];
    return [
      "needs_approval",
      `Stopped after ${Math.round(LIMITS.jobSeconds / 60)} minutes with no result. It may have been waiting for an approval nobody can answer in the background. Last lines: ${readText(`${base}.log`).slice(-800) || "(none)"}`,
    ];
  }
  const reply = readText(job.kind === "codex" && existsSync(`${base}.answer`) ? `${base}.answer` : `${base}.out`);
  if (Number(exit) === 0) return [ASKS.test(reply) ? "needs_approval" : "done", reply];
  return [
    "gone",
    `The agent exited with code ${exit}. Last lines: ${readText(`${base}.log`).slice(-800) || reply.slice(-800) || "(none)"}`,
  ];
}

/** Start an agent in print mode in the background, with the brief on stdin. */
function startBackground(deps: Deps, home: string, id: string, kind: string, prompt: string, folder: string): void {
  const base = join(jobsDir(home), id);
  mkdirSync(jobsDir(home), { recursive: true });
  writeFileSync(`${base}.prompt`, prompt);
  deps.spawnJob(base, headless(kind, folder, `${base}.answer`), folder);
}

// ---- transcripts of herdr jobs ----

/** What marks a job's brief in an agent's chat. Not the bare job id: context lists recent jobs by id, so the id
 * can appear in an agent's chat during an earlier job. */
function marker(job: Json | string): string {
  return `[acm job ${typeof job === "string" ? job : text(job.id)}]`;
}

// How far each file has been searched for each job's marker, so a poll reads only what was appended since.
// ponytail: never cleared; it holds one number per job and file touched during that job.
const searched = new Map<string, number>();

/** True if the marker is in the part of the file not searched yet for this job. */
function appended(path: string, tag: Buffer, jobId: string): boolean {
  const key = `${jobId} ${path}`;
  const size = statSync(path).size;
  const done = searched.get(key) ?? 0;
  // Re-read a marker's length before the old end, in case the marker was half written last time.
  const from = size < done ? 0 : Math.max(0, done - tag.length);
  if (size <= from) return false;
  const fd = openSync(path, "r");
  try {
    const part = Buffer.alloc(size - from);
    readSync(fd, part, 0, part.length, from);
    searched.set(key, size);
    return part.includes(tag);
  } finally {
    closeSync(fd);
  }
}

function transcriptOf(deps: Deps, job: Json, agent: Json): string | null {
  const kind = text(job.kind);
  if (job.transcript && chatExists(kind, text(job.transcript))) return text(job.transcript);
  const base = rootOf(kind, deps.roots);
  if (!existsSync(base)) return null;
  const native = text(obj(agent.agent_session).value);
  if (native) {
    const found = READERS[kind].find(base, native);
    if (found) return found;
  }
  const tag = Buffer.from(marker(job));
  if (kind === "opencode") {
    const latest = READERS.opencode.chats(base, text(job.folder)).sort((a, b) => b.mtime - a.mtime)[0];
    return latest && chatBytes(kind, latest.path).includes(tag) ? latest.path : null;
  }
  const since = Date.parse(text(job.started_at)) - 5000;
  // Claude Code and Cursor keep chats per project, so only this folder's are looked at. Codex keeps every
  // project's by date: listing them all is cheaper than opening each to ask whose it is.
  const paths =
    kind === "codex"
      ? (readdirSync(base, { recursive: true }) as string[])
          .filter((p) => p.endsWith(".jsonl"))
          .map((p) => join(base, p))
      : READERS[kind].chats(base, text(job.folder)).map((c) => c.path);
  for (const path of paths) {
    try {
      if (statSync(path).mtimeMs >= since && appended(path, tag, text(job.id))) return path;
    } catch {
      // gone while we looked
    }
  }
  return null;
}

/**
 * How the turn the job's brief started ended, with its last answer; null while it is still working.
 * Only that turn: a later turn in the same chat (the user typing in the pane, the next job) is not this job's result.
 */
function finished(kind: string, raw: Buffer, jobId: string): [string, string] | null {
  const offset = raw.indexOf(marker(jobId));
  if (offset < 0) return null;
  let line = raw.indexOf(10, offset) + 1;
  if (line === 0) return null;
  let end = -1;
  let failure = "";
  while (line < raw.length && end < 0) {
    const newline = raw.indexOf(10, line);
    const stop = newline < 0 ? raw.length : newline;
    try {
      const record = stop > line ? obj(JSON.parse(raw.subarray(line, stop).toString("utf8"))) : {};
      if (READERS[kind].turnEnded(record)) {
        end = stop;
        failure = READERS[kind].turnError?.(record) ?? "";
      }
    } catch {
      // partial line
    }
    line = stop + 1;
  }
  if (end < 0) return null;
  // The whole turn, however long.
  const answers = parse(kind, raw.subarray(0, end + 1), offset, end + 1).records.filter((r) => r.role === "assistant");
  const answer = answers.length ? answers[answers.length - 1].text : "";
  // The agent's own failure (its service timed out, say) is not a finished job, whatever it said first.
  if (failure) {
    return [
      "gone",
      `${kind} stopped with an error before it finished: ${failure}. Its last message: ${oneLine(answer, 200) || "(none)"}. Delegate the task again.`,
    ];
  }
  return [ASKS.test(answer) ? "needs_approval" : "done", answer];
}

/**
 * Claim a job for one step: move it from the state this process read to `to`, only if no other process has
 * moved it meanwhile (two chats' acm servers, or `acm status`, can refresh the same folder). True when this
 * process has it; `job.state` then says the new state.
 */
function claim(db: Db, job: Json, to: string, set: Record<string, string> = {}): boolean {
  const fields = Object.keys(set)
    .map((k) => `, ${k} = ?`)
    .join("");
  const changed = db
    .prepare(`UPDATE jobs SET state = ?${fields} WHERE id = ? AND state = ?`)
    .run(to, ...Object.values(set), text(job.id), text(job.state));
  if (!changed.changes) return false;
  job.state = to;
  return true;
}

async function check(
  db: Db,
  deps: Deps,
  home: string,
  job: Json,
  live: Map<string, Json>,
): Promise<[string, string | null]> {
  const name = text(job.agent_name);
  if (job.state === "queued") {
    const ahead = db
      .prepare(`SELECT 1 FROM jobs WHERE agent_name = ? AND folder = ? AND state IN (${OPEN_SQL}) AND seq < ? LIMIT 1`)
      .get(name, text(job.folder), job.seq as number);
    if (ahead) return ["queued", null];
    const waitedFor = job.pane === BACKGROUND ? undefined : live.get(name);
    if (job.pane !== BACKGROUND) {
      if (!waitedFor) return ["gone", "The agent it was waiting for is gone: its pane was closed."];
      if (!["idle", "done", "unknown"].includes(text(waitedFor.agent_status))) return ["queued", null];
    }
    const pane = job.pane === BACKGROUND ? BACKGROUND : text(waitedFor?.pane_id);
    if (!claim(db, job, "running", { pane, started_at: now() })) return [text(job.state), null];
    const background = () => {
      startBackground(deps, home, text(job.id), text(job.kind), text(job.prompt), text(job.folder));
      db.prepare("UPDATE jobs SET pane = ? WHERE id = ?").run(BACKGROUND, text(job.id));
      return ["running", null] as [string, null];
    };
    if (pane === BACKGROUND) return background();
    const sent = await send(deps, name, text(job.prompt), pane);
    if (sent[0] === "gone" && deps.installed(BINARIES[text(job.kind)])) return background();
    return sent;
  }
  if (job.pane === BACKGROUND) return checkBackground(home, job);
  let agent = live.get(name);
  // A start that timed out leaves the agent running in its pane with no name; name it once it's ready.
  const unnamed = live.get(`pane:${text(job.pane)}`);
  if (!agent && job.state === "starting" && unnamed) {
    if (!["idle", "done"].includes(text(unnamed.agent_status)))
      return ["starting", await paneTail(deps, text(job.pane))];
    await herdr(deps, "agent", "rename", text(job.pane), name);
    agent = { ...unnamed, name };
  }
  if (!agent) {
    // The pane may have been closed after the agent finished: its chat still has the result.
    const path = transcriptOf(deps, job, {});
    const ended = path ? finished(text(job.kind), chatBytes(text(job.kind), path), text(job.id)) : null;
    if (ended) return ended;
    return [
      "gone",
      `The agent exited or its pane was closed. Last lines: ${(await paneTail(deps, text(job.pane))) || "(none)"}`,
    ];
  }
  const status = text(agent.agent_status);
  if (job.state === "starting") {
    if (status !== "idle" && status !== "done") return ["starting", await paneTail(deps, text(job.pane))];
    if (!claim(db, job, "running")) return [text(job.state), null];
    return send(deps, name, text(job.prompt), text(job.pane));
  }
  // No chat folder for this agent where acm looks (another config dir, an unconfirmed platform): a missing
  // marker says nothing. Resending would make it do the work twice. Once it is idle, report its screen.
  if (!existsSync(rootOf(text(job.kind), deps.roots))) {
    if (status === "blocked") return ["blocked", await paneTail(deps, text(job.pane))];
    if ((status === "idle" || status === "done") && age(job) > LIMITS.resendAfter) {
      return [
        "done",
        `${name} finished, but acm can't read its chat (no ${rootOf(text(job.kind), deps.roots)}). Its pane shows: ${(await paneTail(deps, text(job.pane))) || "(nothing)"}`,
      ];
    }
    return ["running", null];
  }
  const path = transcriptOf(deps, job, agent);
  if (path && !job.transcript) db.prepare("UPDATE jobs SET transcript = ? WHERE id = ?").run(path, text(job.id));
  const raw = path ? chatBytes(text(job.kind), path) : Buffer.alloc(0);
  const ended = raw.length ? finished(text(job.kind), raw, text(job.id)) : null;
  if (ended) return ended;
  if (status === "blocked") return ["blocked", await paneTail(deps, text(job.pane))];
  const idleWithout = (status === "idle" || status === "done") && !raw.includes(marker(job));
  // A freshly started agent can drop its first brief; send it once more.
  if (idleWithout && !job.resent && age(job) > LIMITS.resendAfter) {
    // Only the process that flips the flag sends: another refreshing at the same moment does not.
    // And only while the job is as this process read it: another may have just recorded it done.
    const flipped = db
      .prepare("UPDATE jobs SET resent = 1 WHERE id = ? AND resent = 0 AND state = ?")
      .run(text(job.id), text(job.state));
    if (!flipped.changes) {
      return ["running", null];
    }
    return send(deps, name, text(job.prompt), text(job.pane));
  }
  // Sent twice, the agent idle, and still not in its chat: something on its screen took the brief (a dialog the
  // agent opened between turns, which herdr doesn't report). Free the agent and say what its pane shows.
  if (idleWithout && job.resent && age(job) > LIMITS.lostAfter) {
    return [
      "gone",
      `${name} never got its brief: something on its screen took it instead. Its pane shows: ${(await paneTail(deps, text(job.pane))) || "(nothing)"}. Answer that in its pane (${WATCH}), then delegate the task again.`,
    ];
  }
  return ["running", null];
}

/** Bring every given open job up to date: finished ones get their result, a timeline event, and free their files. */
async function refresh(db: Db, deps: Deps, home: string, jobs: Json[], live: Map<string, Json>): Promise<void> {
  for (const job of jobs) {
    let state: string;
    let result: string | null;
    try {
      [state, result] = await check(db, deps, home, job, live);
    } catch (err) {
      // One job's failing herdr call (a rename, a prompt) leaves that job for the next refresh, not the others.
      if (!(err instanceof HerdrError)) throw err;
      debug(`check ${text(job.id)} failed: ${err.message}`, performance.now());
      continue;
    }
    if (state === job.state && result === null) continue;
    const done = FINISHED.includes(state);
    transaction(db, () => {
      // Only from the state this process saw: if another process already moved the job, its record stands.
      const moved = db
        .prepare(
          "UPDATE jobs SET state = ?, result = COALESCE(?, result), finished_at = COALESCE(?, finished_at) WHERE id = ? AND state = ?",
        )
        .run(state, result, done ? now() : null, text(job.id), text(job.state));
      if (moved.changes && state !== job.state && done) {
        const body = `${job.agent_name} did: ${oneLine(text(job.task), 300)}\nResult: ${result?.trim() || "(no summary)"}`;
        if (state === "done")
          db.prepare("INSERT INTO search (ref, project_id, body) VALUES (?, ?, ?)").run(
            text(job.id),
            text(job.project_id),
            body,
          );
        if (job.thread_id)
          addEvent(
            db,
            text(job.thread_id),
            null,
            `job_${state}`,
            `${job.agent_name} ${state}: ${oneLine(result, 120)}`,
          );
        // The worker as recorded now: it may have joined while this process was reading its chat.
        const worker = db.prepare("SELECT worker_session_id AS id FROM jobs WHERE id = ?").get(text(job.id)) as Json;
        releaseHolds(db, (worker.id as string) ?? null);
      }
    });
  }
}

// ---- the brief ----

export function buildPrompt(o: {
  job: string;
  harness: string;
  thread: string;
  folder: string;
  summary: string;
  task: string;
  doneWhen?: string;
  context?: string;
  others?: [string, string][];
  problem?: boolean;
}): string {
  const parts = [
    `[acm job ${o.job}] A ${o.harness} chat asked for this in ${o.folder}. Your acm thread is ${o.thread}: pass thread=${o.thread} on your first acm context call.`,
  ];
  if (o.problem !== false) parts.push(`## Problem\n${o.summary.trim()}`);
  parts.push(`## Your task\n${o.task.trim()}`);
  parts.push(`## Done when\n${(o.doneWhen || "You decide; say what you checked.").trim()}`);
  if (o.context) parts.push(`## Context\n${o.context.trim()}`);
  if (o.others?.length) {
    const lines = o.others.map(([name, t]) => `- ${name}: ${oneLine(t.split("\n")[0], 120)}`).join("\n");
    parts.push(`## Others working in this folder right now\n${lines}\nDon't edit files another agent is working on.`);
  }
  parts.push(
    "## Before you edit\nUse the acm MCP tools you already have; never start acm yourself from a shell. Call acm context with hold set to every file you will create or edit, relative to this folder. Files outside this folder can't be held; don't try. If a path comes back busy, leave it alone. Call context again before you edit a file you have not held.",
  );
  parts.push(
    '## If an action is denied\nIf something you need is denied, don\'t work around it. Stop, and start your reply with one line `BLOCKED: <the action>`, worded to follow "wants to", e.g. `BLOCKED: run npm run db:migrate on the dev database`. Say why on the next lines. acm passes it to the chat that sent you.',
  );
  parts.push(
    "## When you finish\nacm takes the end of your turn as the end of this job, so wait for every command you start; don't leave work running in the background. Then reply with a one-paragraph summary of what you did and what you checked; acm saves it for the other agents. Don't delegate this job to other agents.",
  );
  return parts.join("\n\n");
}

// ---- delegate and wait ----

export type Task = { to: string; task: string; done_when?: string; context?: string; wait?: boolean };

export async function delegate(
  db: Db,
  s: Session,
  opts: { summary: string; tasks: Task[]; home: string; deps?: Deps },
): Promise<Json> {
  const deps = opts.deps ?? defaultDeps();
  const started = deps.clock();
  const summary = (opts.summary ?? "").trim();
  if (!summary)
    throw new AcmError("invalid", "summary is required: the problem, for someone who has not seen this chat");
  if (!opts.tasks?.length) throw new AcmError("invalid", "tasks must list at least one {to, task}");
  for (const item of opts.tasks) {
    if (!(item.to in FLAGS)) throw new AcmError("invalid", `to must be one of ${Object.keys(FLAGS).join(", ")}`);
    if (!(item.task ?? "").trim()) throw new AcmError("invalid", "every task needs task text");
  }
  const root = s.root;
  if (isHomeOrRoot(root, homedir())) {
    throw new AcmError("invalid", "refusing to delegate in the home folder or a drive root; pass a project folder");
  }
  cleanJobs(db, opts.home);
  const thread = ensureThread(db, s, summary);

  const useHerdr = deps.useHerdr();
  let workspace = "";
  let fresh: string | null = null;
  if (!useHerdr) {
    // Checked before anything starts: a missing agent must not leave the others running with no job recorded.
    const missing = opts.tasks.map((t) => BINARIES[t.to]).find((binary) => !deps.installed(binary));
    if (missing) throw new AcmError("unavailable", `${missing} is not installed or not on PATH`);
  }
  if (useHerdr) {
    await ensureServer(deps);
    [workspace, fresh] = await workspaceFor(deps, root);
  }
  const live = await agents(deps);
  const openHere = () =>
    db.prepare(`SELECT * FROM jobs WHERE folder = ? AND state IN (${OPEN_SQL}) ORDER BY seq`).all(root) as Json[];
  await refresh(db, deps, opts.home, openHere(), live);
  const running = new Map(openHere().map((j) => [text(j.agent_name), text(j.task)]));
  const queue: { item: Task; name: string }[] = [];
  const others: [string, string][] = [...running];
  const plan: { item: Task; name: string; reuse: boolean; problem: boolean; id: string }[] = [];
  const busy: Json[] = [];
  const refuse = (item: Task, name: string, doing?: string) =>
    busy.push({
      to: item.to,
      agent: name,
      state: "busy",
      result: `${name} is still working${doing ? ` on: ${oneLine(doing, 120).replace(/[.…]+$/, "")}` : ""}. Try again when it finishes.`,
    });
  for (const item of opts.tasks) {
    const name = agentName(item.to, root);
    const agent = live.get(name);
    if (agent && agent.workspace_id !== workspace) {
      throw new AcmError("invalid", `herdr agent ${name} belongs to another folder; close it or rename this folder`);
    }
    // "unknown" means herdr can't read that agent's screen, not that it is busy: the job records say that.
    const working = agent !== undefined && !["idle", "done", "unknown"].includes(text(agent.agent_status));
    const planned = plan.find((p) => p.name === name);
    if (running.has(name) || working || planned) {
      if (item.wait) {
        // The user chose to wait: it starts as soon as this agent is free.
        queue.push({ item, name });
        continue;
      }
      refuse(item, name, running.get(name) ?? planned?.item.task);
      continue;
    }
    const last = db
      .prepare("SELECT summary FROM jobs WHERE agent_name = ? AND folder = ? ORDER BY seq DESC LIMIT 1")
      .get(name, root) as Json | undefined;
    const reuse = agent !== undefined;
    plan.push({ item, name, reuse, problem: !(reuse && last?.summary === summary), id: newId("j_") });
  }
  // Reserve each agent in one write before touching herdr: another delegate in the same moment (another chat's
  // acm) must find it taken, not brief it too. A reservation left by a crashed delegate lapses after RESERVED.
  transaction(db, () => {
    for (const p of [...plan]) {
      const taken = db
        .prepare(
          `SELECT task FROM jobs WHERE agent_name = ? AND folder = ? AND (state IN (${OPEN_SQL}) OR (state = 'sending' AND started_at > ?)) LIMIT 1`,
        )
        .get(p.name, root, now(new Date(Date.now() - RESERVED * 1000))) as Json | undefined;
      if (taken) {
        plan.splice(plan.indexOf(p), 1);
        if (p.item.wait) queue.push({ item: p.item, name: p.name });
        else refuse(p.item, p.name, text(taken.task));
        continue;
      }
      db.prepare(
        `INSERT INTO jobs (id, project_id, thread_id, caller_session_id, folder, kind, agent_name, pane, summary, task, prompt, state, started_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, '', ?, ?, '', 'sending', ?)`,
      ).run(p.id, s.project_id, thread, s.id, root, p.item.to, p.name, summary, p.item.task, now());
    }
  });
  for (const p of plan) others.push([p.name, p.item.task]);
  // Who could take a busy agent's task instead: installed, with no job here, not working, not asked for in this call.
  const free = busy.length
    ? Object.keys(FLAGS).filter((k) => {
        const n = agentName(k, root);
        const a = live.get(n);
        return (
          deps.installed(BINARIES[k]) &&
          !running.has(n) &&
          !plan.some((p) => p.name === n) &&
          !(a && !["idle", "done", "unknown"].includes(text(a.agent_status)))
        );
      })
    : [];
  try {
    // Panes first, in order: the layout depends on it.
    const solo = new Set<string>();
    const jobs: { item: Task; name: string; reuse: boolean; id: string; prompt: string; pane: string }[] = [];
    for (const { item, name, reuse, problem, id } of plan) {
      const prompt = buildPrompt({
        job: id,
        harness: s.harness,
        thread,
        folder: root,
        summary,
        task: item.task,
        doneWhen: item.done_when,
        context: item.context,
        others: others.filter(([n]) => n !== name),
        problem,
      });
      let pane = text(live.get(name)?.pane_id);
      if (useHerdr && !reuse) {
        pane = fresh ?? (await newPane(deps, workspace, root, item.to, solo));
        fresh = null;
        if (item.to === "opencode") solo.add(pane);
        live.set(name, { name, pane_id: pane });
      }
      jobs.push({ item, name, reuse, id, prompt, pane });
    }

    // Then start every new agent at once, each with the same budget, so one that stalls (an update prompt, a
    // login screen) doesn't eat the others' time. The budget leaves room for the briefs under the agents' own
    // 60-second tool timeout, which OpenCode, Codex, and Cursor all enforce. herdr takes 3 to 300 seconds.
    const budget = String(Math.max(5000, Math.floor((started + START_SECONDS - deps.clock()) * 1000)));
    const errors = new Map<string, HerdrError>();
    await Promise.all(
      jobs
        .filter((j) => useHerdr && !j.reuse)
        .map(async (j) => {
          try {
            await herdr(
              deps,
              "agent",
              "start",
              j.name,
              "--kind",
              j.item.to,
              "--pane",
              j.pane,
              "--timeout",
              budget,
              "--",
              ...FLAGS[j.item.to],
            );
          } catch (err) {
            if (err instanceof HerdrError) errors.set(j.name, err);
            else throw err;
          }
        }),
    );

    // Decide each job's state, then hand out every brief at once.
    const ready = jobs.map((j) => ({
      j,
      kind: j.item.to,
      state: "running",
      result: null as string | null,
      pane: j.pane,
    }));
    const background = (o: (typeof ready)[number]) => {
      startBackground(deps, opts.home, o.j.id, o.kind, o.j.prompt, root);
      o.pane = BACKGROUND;
    };
    for (const o of ready) {
      const err = errors.get(o.j.name);
      if (!useHerdr) {
        background(o);
      } else if (err && (err.code === "agent_not_ready" || err.code === "timeout" || /timed out/.test(err.message))) {
        // Still coming up, often at a prompt (an update, a login): delegate_wait sends the brief once it's ready.
        o.state = "starting";
        o.result = (await paneTail(deps, o.pane)) || null;
      } else if (err) {
        // One agent that won't start must not stop the others.
        live.delete(o.j.name);
        o.state = "gone";
        o.result = `herdr could not start ${o.kind}: ${err.message}. Last lines: ${(await paneTail(deps, o.pane)) || "(none)"}`;
      }
    }
    await Promise.all(
      ready
        .filter((o) => useHerdr && o.state === "running")
        .map(async (o) => {
          [o.state, o.result] = await send(deps, o.j.name, o.j.prompt, o.pane);
          // herdr can't drive this agent (say, a new version it doesn't recognize yet): run the job in the background.
          if (o.state === "gone" && deps.installed(BINARIES[o.kind])) {
            background(o);
            [o.state, o.result] = ["running", null];
          }
        }),
    );

    for (const { j, state, result: failed, pane } of ready) {
      transaction(db, () => {
        // started_at again: the job's clock (resend, lost brief, time limit) runs from the brief, not the reservation.
        db.prepare(
          "UPDATE jobs SET pane = ?, prompt = ?, state = ?, result = ?, started_at = ?, finished_at = ? WHERE id = ?",
        ).run(pane, j.prompt, state, failed, now(), FINISHED.includes(state) ? now() : null, j.id);
        addEvent(db, thread, s.id, "job_started", `${j.name} started: ${j.item.task}`);
      });
    }
  } catch (err) {
    // This delegate failed partway: its reservations must not hold the agents.
    const ids = plan.map((p) => p.id);
    db.prepare(
      `UPDATE jobs SET state = 'gone', result = ?, finished_at = ? WHERE state = 'sending' AND id IN (${ids.map(() => "?").join(", ") || "''"})`,
    ).run(`delegate failed before the brief was sent: ${err instanceof Error ? err.message : err}`, now(), ...ids);
    throw err;
  }
  // Queued jobs go in last, so each has a higher seq than the job it waits for, even one started in this call.
  for (const q of queue) {
    const id = newId("j_");
    const prompt = buildPrompt({
      job: id,
      harness: s.harness,
      thread,
      folder: root,
      summary,
      task: q.item.task,
      doneWhen: q.item.done_when,
      context: q.item.context,
      others: others.filter(([n]) => n !== q.name),
    });
    // Where that agent runs: its herdr pane, or wherever its last job ran (the background, without herdr).
    const last = db
      .prepare("SELECT pane FROM jobs WHERE agent_name = ? AND folder = ? ORDER BY seq DESC LIMIT 1")
      .get(q.name, root) as Json | undefined;
    const pane = text(live.get(q.name)?.pane_id) || text(last?.pane);
    transaction(db, () => {
      db.prepare(
        `INSERT INTO jobs (id, project_id, thread_id, caller_session_id, folder, kind, agent_name, pane, summary, task, prompt, state, started_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued', ?)`,
      ).run(id, s.project_id, thread, s.id, root, q.item.to, q.name, pane, summary, q.item.task, prompt, now());
      addEvent(db, thread, s.id, "job_queued", `${q.name} queued: ${q.item.task}`);
    });
  }
  const out = await wait(db, deps, opts.home, s, started);
  out.jobs = [...busy, ...(out.jobs as Json[])];
  if (busy.length) {
    out.free = free;
    out.busy_next =
      "An agent is busy. Ask the user whether to wait for it (call delegate again with the same task and wait: true; it starts when the agent is free) or to give the task to one of free (call delegate with to set to their pick). Never choose for them.";
  }
  return out;
}

export async function delegateWait(db: Db, s: Session, opts: { home: string; deps?: Deps }): Promise<Json> {
  const deps = opts.deps ?? defaultDeps();
  return wait(db, deps, opts.home, s, deps.clock());
}

/**
 * The project at a glance, for a status line or pane: open and recent jobs (open ones refreshed first),
 * held files, and, given a chat, its thread with the latest timeline. Creates nothing.
 */
export async function status(
  db: Db,
  opts: { home: string; folder: string; harness?: string; chat?: string; deps?: Deps },
): Promise<Json> {
  const root = projectRoot(canonical(opts.folder));
  const project = db.prepare("SELECT id FROM projects WHERE root = ?").get(root) as Json | undefined;
  if (!project) return { project: root, jobs: [], held: [] };
  const open = db
    .prepare(`SELECT * FROM jobs WHERE folder = ? AND state IN (${OPEN_SQL}) ORDER BY seq`)
    .all(root) as Json[];
  if (open.length) {
    const deps = opts.deps ?? defaultDeps();
    try {
      await refresh(db, deps, opts.home, open, await agents(deps));
    } catch (err) {
      debug(`status refresh failed: ${err}`, performance.now()); // herdr down: show what the database knows
    }
  }
  const session = opts.chat
    ? (db
        .prepare("SELECT id, thread_id FROM sessions WHERE project_id = ? AND harness = ? AND chat = ?")
        .get(text(project.id), opts.harness ?? "claude", opts.chat) as Json | undefined)
    : undefined;
  const jobs = (
    db
      .prepare(
        `SELECT * FROM jobs WHERE project_id = ? AND (state IN (${OPEN_SQL}) OR seq IN (SELECT seq FROM jobs WHERE project_id = ? ORDER BY seq DESC LIMIT 5)) ORDER BY seq`,
      )
      .all(text(project.id), text(project.id)) as Json[]
  ).map((j) => ({
    job: j.id,
    agent: j.agent_name,
    to: j.kind,
    state: j.state,
    summary: j.summary,
    task: oneLine(text(j.task), 200),
    result: j.result ? oneLine(text(j.result), 200) : null,
    mine: session ? j.caller_session_id === session.id : false,
    finished_at: j.finished_at,
  }));
  const out: Json = { project: root, jobs, held: held(db, text(project.id)) };
  if (session?.thread_id) {
    const thread = db.prepare("SELECT id, name, status FROM threads WHERE id = ?").get(text(session.thread_id)) as Json;
    const events = db
      .prepare("SELECT at, kind, text FROM events WHERE thread_id = ? ORDER BY id DESC LIMIT 8")
      .all(text(session.thread_id))
      .reverse();
    out.thread = { ...thread, events };
  }
  return out;
}

async function wait(db: Db, deps: Deps, home: string, s: Session, started: number): Promise<Json> {
  const deadline = started + WAIT_SECONDS;
  for (;;) {
    const mine = db
      .prepare(`SELECT 1 FROM jobs WHERE caller_session_id = ? AND state IN (${OPEN_SQL}) LIMIT 1`)
      .get(s.id);
    // Every open job in the folder, oldest first: a queued job of mine may wait on another chat's job.
    // Nothing of mine open: don't ask herdr, so a stopped herdr can't fail a wait with nothing to wait for.
    if (mine) {
      const open = db
        .prepare(`SELECT * FROM jobs WHERE folder = ? AND state IN (${OPEN_SQL}) ORDER BY seq`)
        .all(s.root) as Json[];
      await refresh(db, deps, home, open, await agents(deps));
    }
    const pending = (
      db
        .prepare(
          "SELECT COUNT(*) AS n FROM jobs WHERE caller_session_id = ? AND state IN ('starting', 'running', 'queued')",
        )
        .get(s.id) as Json
    ).n as number;
    if (!pending || deps.clock() + POLL_SECONDS > deadline) break;
    await deps.sleep(POLL_SECONDS);
  }
  const rows = db
    .prepare(`SELECT * FROM jobs WHERE caller_session_id = ? AND (reported = 0 OR state IN (${OPEN_SQL})) ORDER BY seq`)
    .all(s.id) as Json[];
  const jobs: Json[] = [];
  for (const row of rows) {
    const state = text(row.state);
    const job: Json = {
      job: row.id,
      to: row.kind,
      agent: row.agent_name,
      pane: row.pane,
      state,
      result: state === "done" || state === "gone" ? oneLine(text(row.result)) : (row.result ?? null),
    };
    const ask = state === "needs_approval" ? ASKS.exec(text(row.result)) : null;
    if (ask?.[1].trim()) job.ask = ask[1].trim().replace(/\.+$/, "");
    jobs.push(job);
    if (FINISHED.includes(state)) db.prepare("UPDATE jobs SET reported = 1 WHERE id = ?").run(text(row.id));
  }
  const out: Json = {
    thread: s.thread_id,
    watch: deps.useHerdr() ? WATCH : `tail -f ${jobsDir(home)}/<job>.log`,
    jobs,
  };
  if (!jobs.length) out.message = "No job is running, and every result was already reported. Nothing to wait for.";
  if (jobs.some((j) => ["starting", "running", "blocked", "queued"].includes(text(j.state)))) {
    out.next =
      "Some agents are not finished. Call delegate_wait until none are running; for a blocked one, call it again after the user has answered in its pane.";
  }
  if (jobs.some((j) => j.state === "starting" || j.state === "blocked")) {
    out.blocked = "An agent is waiting on a question or approval. Tell the user; do not answer it for them.";
  }
  if (jobs.some((j) => j.state === "needs_approval")) {
    out.needs_approval =
      "An agent stopped at an action it was not allowed to run; its result says what it needs. Show the user. If they approve, run that step yourself or delegate again with their answer. Never approve it for them.";
  }
  return out;
}

/** What the user sees in the calling agent, laid out like the website demo: the briefs, each job's state, and any asks. */
export function card(out: Json, tasks?: Task[]): string {
  const lines: string[] = [];
  if (tasks) {
    lines.push(`acm · delegate(tasks=${tasks.length} · ${out.watch === WATCH ? "herdr panes" : "background"})`, "");
    for (const t of tasks) lines.push(t.to, oneLine(t.task));
    lines.push("");
  }
  const all = (out.jobs as Json[]) ?? [];
  const jobs = all.filter((j) => j.state !== "busy");
  if (!all.length)
    return [...lines, "acm · delegate_wait(nothing running; every result was already reported)"].join("\n");
  if (jobs.length)
    lines.push(`acm · delegate_wait(${jobs.filter((j) => j.state === "done").length}/${jobs.length} done)`);
  const width = Math.max(...all.map((j) => text(j.to).length)) + 2;
  for (const j of all) lines.push(text(j.to).padEnd(width) + text(j.state));
  for (const j of all) {
    if (j.state === "needs_approval") {
      lines.push(`needs_approval · ${j.to} ${j.ask ? `wants to ${j.ask}` : oneLine(text(j.result), 160)}`);
    } else if (j.state === "busy") {
      lines.push(
        `busy · ${j.to} is working on something else${out.free && (out.free as string[]).length ? `; free now: ${(out.free as string[]).join(", ")}` : ""}`,
      );
    } else if (j.state === "blocked") {
      lines.push(`blocked · ${j.to} is waiting for an answer in its herdr pane`);
    }
  }
  return lines.join("\n");
}
