/**
 * Live A/B: can a new Codex chat finish work that earlier Codex chats started, when only those chats hold the details?
 * Each task's earlier chats run once, with ACM installed as a user would have it (chat.md, or chat-1.md then
 * chat-2.md; a line of --- splits a chat into turns), and do step 1. The continuation then runs in four arms: none
 * (no ACM), named (ACM, and the ask names it as the README says to), summary (the summary the last earlier chat
 * writes when asked, pasted), and the full chat history pasted: paste with one earlier chat, pasteall (every chat,
 * oldest first) with two. The report shows those two as one.
 * Hidden checks score the repo afterwards. When a chat stops to ask, a scripted user answers, the same in every arm.
 * No chat can find another arm's answer: each runs in a bwrap sandbox that shows it only its own folder and home
 * (the Codex login is copied in), one task's chats run one after another, and every trial starts from the earlier
 * chats' end state. bench/PLAN.md and bench/PLAN-context-loss.md have the designs. Logs go to a logs folder next to
 * --out. Spends Codex quota. Linux with bubblewrap only.
 *
 * usage: node bench/live.ts [--reps 3] [--jobs 6] [--tasks pager,report] [--arms none,named,summary,paste,pasteall]
 *        [--out file]  (arm:n runs that arm n times instead of --reps; --resume keeps --out's trials, runs the rest)
 *        node bench/live.ts --report bench/results/live.json
 *        node bench/live.ts --backfill bench/results/live.json   (steps and details from its logs; no Codex)
 *        node bench/live.ts --rescore bench/results/live.json   (strict scoring of every run from its logs; no Codex)
 *        node bench/live.ts --verify [--tasks ...]   (checks fail on repo/, pass on solution/, details match; no Codex)
 *        node bench/live.ts --summaries bench/results/live.json [--reps 1]   (summaries of its saved earlier chats,
 *        scored for their details, no continuations: bench/PLAN-context-loss.md's stage 1; spends Codex quota)
 *        Any mode that runs Codex takes --model and --effort (e.g. --model gpt-6-luna --effort medium); unset, Codex's defaults.
 */
import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  copyFileSync,
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  realpathSync,
  rmSync,
  utimesSync,
  writeFileSync,
} from "node:fs";
import { homedir, tmpdir } from "node:os";
import { basename, dirname, join, relative } from "node:path";
import { DatabaseSync } from "node:sqlite";
import { parseArgs } from "node:util";
import type { Json } from "../src/readers/index.ts";
import { parse, READERS } from "../src/transcript.ts";
import { VERSION } from "../src/version.ts";

const REPO = join(import.meta.dirname, "..");
// bench/PLAN-context-loss.md: in the first family lost context costs steps, in the others mistakes; in the second
// the repo still holds the old answer.
const RECOVERABLE = "recoverable from the repo";
const CONTRADICTED = "contradicted by the repo";
// "including step 2": without it, Luna (gpt-6-luna) read the old chat's "Don't start step 2" as still standing and
// stopped after step 1 in 17 of 21 pasted one-chat runs (bench/PLAN-context-loss.md).
const ASK = "Continue from my last Codex chat in this repo and finish the task, including step 2.";
const PROMPTS: Record<string, string> = {
  // At the user's request (2026-10-18), No ACM points at what the user told the agent before. Codex's and Cursor's
  // runs asked the same as the other ways ("Continue from my last … chat …"); their results files record it.
  none: "See what I told Codex to do in this repo, and finish the task, including step 2.",
  named: `Use ACM to ${ASK[0].toLowerCase()}${ASK.slice(1)}`,
  summary: `${ASK}\n\nHere is its summary:\n\n`,
  note: `${ASK}\n\nHere is its handoff note:\n\n`,
  notefile: `${ASK}\n\nHere is its handoff note:\n\n`,
  paste: `${ASK}\n\nHere is that chat:\n\n`,
  pasteall:
    "Continue from my Codex chats in this repo and finish the task, including step 2.\n\nHere they are, oldest first:\n\n",
};
const ARMS: Record<string, string> = {
  none: "No ACM",
  named: "ACM",
  summary: "Summary pasted",
  note: "Handoff note pasted",
  notefile: "Handoff note pasted, with the files it wrote",
  paste: "Last chat pasted",
  pasteall: "Full chat history pasted",
};
// What the user asks the last earlier chat before opening a new one, in the summary arm.
const SUMMARIZE = "Summarize this chat so I can continue in a new chat.";
// What a careful user asks for instead, in the handoff-note arm (bench/confirm/PLAN.md).
const NOTE =
  "Write a handoff note so a new chat can continue this work: list every requirement, value, rule, constraint and decision from this chat word for word, including anything that was changed or ruled out.";
// The scripted user: when ACM asks which chat, the one the last-chat arm pastes; anything else it asks, nothing new.
const PICK = "The newest one.";
const NOTHING = "Use what's in my earlier chats; I have nothing to add. Please finish the task.";
// A last message that asks the user something: a question, or a request to confirm or to send details.
const ASKS = /\?\s*$|\b(please confirm|confirm (whether|that|if)|please (provide|share|send|paste|tell me))\b/i;
// Checks only the earlier chats could have told the agent how to pass.
const DETAIL = /^(chat\d*|changed)_/;

const { values: opt } = parseArgs({
  options: {
    reps: { type: "string", default: "3" },
    jobs: { type: "string", default: "6" },
    // A task suite other than bench/ (the development set), like bench/confirm: its own tasks/ and families.json.
    suite: { type: "string" },
    tasks: { type: "string" },
    arms: { type: "string", default: "none,named,summary,paste,pasteall" },
    timeout: { type: "string", default: "900" },
    out: { type: "string", default: join(import.meta.dirname, "results", "live.json") },
    report: { type: "string" },
    backfill: { type: "string" },
    summaries: { type: "string" },
    rescore: { type: "string" },
    // The agent every chat runs in: codex, cursor (Cursor's CLI, cursor-agent), or opencode.
    agent: { type: "string", default: "codex" },
    // The agent's model and reasoning effort for every chat; unset, its defaults. Cursor takes its effort in the
    // model's name: --model 'name[effort=high]'; OpenCode as the model's variant.
    model: { type: "string" },
    effort: { type: "string" },
    verify: { type: "boolean", default: false },
    resume: { type: "boolean", default: false },
    // bench/confirm/PLAN.md: the run refuses to start unless what it runs on hashes to this (see freezeHash).
    frozen: { type: "string" },
    // The ACM the chats get, a folder with its src/ and package.json; unset, this repo's own. A frozen run uses a
    // copy (frozen/), so the repo's own can change while the run goes on.
    acm: { type: "string" },
    hash: { type: "boolean", default: false },
    admit: { type: "string" },
    confirm: { type: "string" },
  },
});
const ACM = opt.acm ? join(REPO, opt.acm) : REPO;
const CLI = join(ACM, "src", "cli.ts");
const AGENT = opt.agent;
if (!["codex", "cursor", "opencode"].includes(AGENT))
  throw new Error(`unknown agent ${AGENT}: use codex, cursor, or opencode`);
if (AGENT === "cursor" && opt.effort)
  throw new Error("Cursor takes its effort in the model's name: --model 'name[effort=high]'");
// What the user calls the agent: the tasks' chats and the prompts say Codex.
const NAME = ({ codex: "Codex", cursor: "Cursor", opencode: "OpenCode" } as Record<string, string>)[AGENT];
// Where the login every chat shares lives in a home, copied in from the user's. Cursor's is its file store: a sandbox
// can't reach a keyring.
const AUTH_AT = (
  {
    codex: join(".codex", "auth.json"),
    cursor: join(".config", "cursor", "auth.json"),
    opencode: join(".local", "share", "opencode", "auth.json"),
  } as Record<string, string>
)[AGENT];
const AUTH =
  AGENT === "codex" && process.env.CODEX_HOME ? join(process.env.CODEX_HOME, "auth.json") : join(homedir(), AUTH_AT);
const SUITE = opt.suite ? join(REPO, opt.suite) : import.meta.dirname;
const TASKS = join(SUITE, "tasks");
const FAMILIES: Record<string, string[]> = JSON.parse(readFileSync(join(SUITE, "families.json"), "utf8"));
const TASK_LIST = (opt.tasks ?? Object.values(FAMILIES).flat().join(",")).split(",");
const LOGS = join(dirname(opt.rescore ?? opt.backfill ?? opt.summaries ?? opt.report ?? opt.out), "logs");
// Set when Codex says the account's usage limit is reached: the run stops, keeping what it has, for --resume.
let limited: string | undefined;

type Checks = Record<string, boolean>;
type Usage = { input: number; cached: number; output: number };
type Run = { events: Json[]; stderr: string; seconds: number; code: number | null; timedOut: boolean };
type Chat = { file: string; raw: string };
// at: the folder the earlier chats ran in, where every trial runs too; saved: its end state; acm: ACM's store then.
type First = {
  task: string;
  at: string;
  saved: string;
  acm: string;
  chats: Chat[];
  tries: number;
  sources?: Record<string, string>; // where each planted detail first came up, see sources
  model: string;
  effort: string;
};
type Trial = {
  task: string;
  arm: string;
  rep: number;
  asked?: number; // characters the user typed or pasted
  turns?: number; // messages the user sent
  copied?: number; // chats the user found and copied
  checks: Checks;
  tools: string[];
  outside: string[];
  usage: Usage;
  steps: number;
  atoms?: Record<string, number>; // the steps by kind, see classify
  kept?: Record<string, string>; // each planted detail in what the chat was handed, see survival
  summary?: string; // summary arm: what the user pasted
  summaryUsage?: Usage; // and what writing it cost
  strict?: Strict; // what strict success needs besides the checks, see strictOf
  seconds: number;
  error?: string;
  reply: string;
};
type Result = Json & { checks: Record<string, string[]>; first: Json[]; trials: Trial[] };
// A task's planted details, by the check that tests each: patterns for its current value and for an old or
// look-alike one, matched case-insensitively against what a chat was handed.
type Details = Record<string, { value: string[]; stale?: string[] }>;

/** A prompt or chat turn as the user says it to this agent. */
function say(text: string): string {
  return text.replaceAll("Codex", NAME);
}

/** The flags that resume a chat by its id. */
function resumeArgs(id: string): string[] {
  return AGENT === "cursor" ? ["--resume", id] : AGENT === "opencode" ? ["--session", id] : ["resume", id];
}

function git(folder: string, ...args: string[]): void {
  spawnSync("git", ["-C", folder, "-c", "user.name=bench", "-c", "user.email=bench@example.com", ...args]);
}

/** What a sandboxed chat may read besides its own folders: the agent (Codex with its bundled rg, or Cursor's
 * version folder with its own node and rg), Node and ACM's code (for ACM's server), and the Python the tasks run
 * on. Found once, on the first chat. */
let found: { bin: string; read: string[]; path: string } | undefined;
export function tools() {
  if (found) return found;
  const which = `command -v ${AGENT === "cursor" ? "cursor-agent" : AGENT}`;
  const bin = realpathSync(spawnSync("sh", ["-c", which], { encoding: "utf8" }).stdout.trim());
  const release = AGENT === "codex" ? dirname(dirname(bin)) : dirname(bin);
  const python = spawnSync("python3", ["-c", "import sys; print(sys.base_prefix)"], { encoding: "utf8" }).stdout.trim();
  const node = dirname(dirname(process.execPath));
  // ACM's packages resolve from the repo's node_modules, a folder above any copy of it.
  const read = [release, python, node, join(ACM, "src"), join(ACM, "package.json"), join(REPO, "node_modules")];
  const own = AGENT === "codex" ? join(release, "codex-path") : release;
  const path = [join(python, "bin"), join(node, "bin"), own, "/usr/local/bin:/usr/bin:/bin"];
  found = { bin, read, path: path.join(":") };
  return found;
}

/** bwrap arguments for one sandboxed process. It sees the system read-only, and of /home and the temp folder only
 * what tools() needs (read-only) and its own folders (rw): not the user's chats or ACM's memory, other trials,
 * bench/ (answer keys, logs), or the Windows drives. The environment is only env. */
export function jail(rw: string[], env: Record<string, string>): string[] {
  const hidden = [...new Set(["/home", "/tmp", tmpdir(), "/mnt", "/root", "/run/user"])].filter((p) => existsSync(p));
  return [
    "--die-with-parent",
    "--unshare-pid",
    "--ro-bind",
    "/",
    "/",
    "--dev",
    "/dev",
    "--proc",
    "/proc",
    ...hidden.flatMap((p) => ["--tmpfs", p]),
    ...tools().read.flatMap((p) => ["--ro-bind", p, p]),
    ...rw.flatMap((p) => ["--bind", p, p]),
    "--clearenv",
    ...Object.entries(env).flatMap(([key, value]) => ["--setenv", key, value]),
  ];
}

/** Before any chat: inside the sandbox, the user's chats and memory, other trials, and bench/ must not exist, and
 * the temp folder holds only the way down to this check's own folder. Throws, so no run starts unisolated. */
export function canary(work: string): void {
  const own = mkdtempSync(join(work, "c-"));
  const secret = [
    join(homedir(), ".codex", "sessions"),
    join(homedir(), ".codex", "auth.json"),
    join(homedir(), ".agent-cowork-memory"),
    join(homedir(), ".claude"),
    join(homedir(), ".local", "share", "opencode"),
    join(homedir(), ".cursor"),
    join(homedir(), ".config", "cursor"),
    join(homedir(), ".config", "opencode"),
    join(REPO, "bench"),
    LOGS,
  ];
  const p = spawnSync(
    "bwrap",
    [
      ...jail([own], { PATH: "/usr/bin:/bin" }),
      "sh",
      "-c",
      'for p in "$@"; do [ -e "$p" ] && echo "$p"; done; ls -A /tmp',
      "sh",
      ...secret,
    ],
    { encoding: "utf8" },
  );
  rmSync(own, { recursive: true, force: true });
  const seen = p.stdout.split("\n").filter(Boolean);
  const top = own.split("/")[2]; // /tmp/<top>/...
  const leaks = seen.filter((line) => line !== top);
  if (p.status !== 0 || leaks.length || !own.startsWith("/tmp/")) {
    throw new Error(
      `the sandbox isn't isolating (needs bubblewrap, and a temp folder under /tmp): ${p.stderr || leaks.join(", ")}`,
    );
  }
}

/** One turn of the agent, sandboxed, with a home of its own. Codex: exec, with --ignore-user-config keeping the
 * user's config, plugins, and MCP servers out, and a fresh CODEX_HOME the user's chats. Cursor: cursor-agent -p, whose
 * fresh home holds no config, rules, hooks, or chats of the user's. Only the login is shared. rw: other folders it
 * may write (ACM's store). */
function turn(
  folder: string,
  home: string,
  prompt: string,
  extra: string[],
  rw: string[] = [],
  sandbox = "workspace-write",
): Promise<Run> {
  // A frozen run stops, as at the usage limit, once what it runs on changes under it (ACM edited mid-run, say).
  if (opt.frozen && freezeHash() !== opt.frozen) limited ??= "what this run uses changed since the freeze; put it back";
  // OpenCode's login goes in its home's config instead (see openCodeEnv): OpenCode 2 keeps logins in its chat
  // database, which the logs keep a copy of.
  const auth = AGENT === "opencode" ? "" : join(home, AUTH_AT);
  if (auth) mkdirSync(dirname(auth), { recursive: true });
  // A copy, not a link: agents looking for the earlier chat follow a link back to the user's own home. Cursor's is
  // copied every turn, since another chat may have refreshed it.
  if (auth && (AGENT === "cursor" || !existsSync(auth))) copyFileSync(AUTH, auth);
  const before = auth ? readFileSync(auth, "utf8") : "";
  // Everything runs without asking, in this sandbox rather than Cursor's own, as Codex runs in workspace-write. And
  // no self-update: in a fresh home, Cursor installs its newest version there, half a gigabyte every chat.
  const cursor = [
    "-p",
    "--output-format",
    "stream-json",
    "--force",
    "--trust",
    "--approve-mcps",
    "--sandbox",
    "disabled",
    "--disable-auto-update",
  ];
  // OpenCode approves every tool without asking (--auto), as the others do, on a server of its own (--standalone);
  // its effort is the model's variant, model#variant.
  const opencode = ["run", "--standalone", "--format", "json", "--auto"];
  const variant = opt.effort ? `#${opt.effort}` : "";
  const args =
    AGENT === "cursor"
      ? [...cursor, "--workspace", folder, ...(opt.model ? ["--model", opt.model] : []), ...extra, prompt]
      : AGENT === "opencode"
        ? [...opencode, ...(opt.model ? ["-m", `${opt.model}${variant}`] : []), ...extra, prompt]
        : [
            "exec",
            "--json",
            "--ignore-user-config",
            "--disable",
            "hooks",
            "--skip-git-repo-check",
            "-s",
            sandbox,
            ...(opt.model ? ["-m", opt.model] : []),
            ...(opt.effort ? ["-c", `model_reasoning_effort=${JSON.stringify(opt.effort)}`] : []),
            "-c",
            'approval_policy="never"',
            "--cd",
            folder,
            ...extra,
            prompt,
          ];
  const env = {
    HOME: home,
    ...(AGENT === "cursor"
      ? { AGENT_CLI_CREDENTIAL_STORE: "file" }
      : AGENT === "opencode"
        ? openCodeEnv(home)
        : { CODEX_HOME: join(home, ".codex") }),
    PATH: tools().path,
    LANG: process.env.LANG || "C.UTF-8",
    USER: process.env.USER || "user",
    TMPDIR: "/tmp",
  };
  const jailed = [...jail([folder, home, ...rw], env), "--chdir", folder, tools().bin, ...args];
  const started = Date.now();
  return new Promise((resolve) => {
    const child = spawn("bwrap", jailed, { cwd: folder, stdio: ["ignore", "pipe", "pipe"], detached: true });
    let out = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      out += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr = (stderr + chunk).slice(-4000);
    });
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      process.kill(-(child.pid as number), "SIGKILL");
    }, Number(opt.timeout) * 1000);
    child.on("close", (code) => {
      clearTimeout(timer);
      // A login the agent refreshed during the chat leaves the user's copy stale: carry the newer one back.
      const refreshed = (file: string) => String((JSON.parse(readFileSync(file, "utf8")) as Json).last_refresh ?? "");
      if (auth && (AGENT === "cursor" ? readFileSync(auth, "utf8") !== before : refreshed(auth) > refreshed(AUTH)))
        copyFileSync(auth, AUTH);
      const lines = out.split("\n").flatMap((line) => {
        try {
          return [JSON.parse(line) as Json];
        } catch {
          return [];
        }
      });
      const events = AGENT === "cursor" ? fromCursor(lines) : AGENT === "opencode" ? fromOpenCode(lines) : lines;
      const limit = AGENT === "cursor" ? CURSOR_LIMIT : AGENT === "opencode" ? OPENCODE_LIMIT : /usage limit/i;
      const failed = events.filter((e) => e.type === "error" || e.type === "turn.failed").map((e) => JSON.stringify(e));
      const hit = [...failed, ...(AGENT !== "codex" && code ? [stderr] : [])].find((text) => limit.test(text));
      if (hit) limited ??= `${NAME}'s usage limit, ${hit.slice(0, 300)}`;
      resolve({ events, stderr, seconds: (Date.now() - started) / 1000, code, timedOut });
    });
  });
}

// What Cursor says when the account can't run more: the run stops there, as at Codex's usage limit.
const CURSOR_LIMIT =
  /usage limit|rate.?limit|resource.?exhausted|quota|spend limit|out of (fast )?requests|upgrade your plan/i;

/** Cursor's stream-json as Codex's events, so one reading serves both: its session is the thread, a finished tool
 * call an item (reading tools as the shell commands they stand for, so steps count alike), its result the turn. */
export function fromCursor(lines: Json[]): Json[] {
  const out: Json[] = [];
  let said = "";
  const flush = () => {
    if (said) out.push({ type: "item.completed", item: { type: "agent_message", text: said } });
    said = "";
  };
  for (const e of lines) {
    if (e.type === "system" && e.subtype === "init")
      out.push({ type: "thread.started", thread_id: e.session_id, model: e.model });
    else if (e.type === "assistant") {
      // One message can come in several parts; a tool call or the result ends it.
      const content = ((e.message as Json)?.content as Json[]) ?? [];
      said += content
        .filter((c) => c.type === "text")
        .map((c) => String(c.text))
        .join("");
    } else if (e.type === "tool_call" && e.subtype === "completed") {
      flush();
      out.push({ type: "item.completed", item: cursorItem(e.tool_call as Json) });
    } else if (e.type === "tool_call") flush();
    else if (e.type === "result") {
      flush();
      const u = (e.usage as Record<string, number>) ?? {};
      const cached = u.cacheReadTokens ?? 0;
      out.push(
        e.is_error
          ? { type: "turn.failed", error: e.result }
          : {
              type: "turn.completed",
              usage: {
                input_tokens: (u.inputTokens ?? 0) + cached + (u.cacheWriteTokens ?? 0),
                cached_input_tokens: cached,
                output_tokens: u.outputTokens ?? 0,
              },
            },
      );
    } else if (e.type === "error") out.push({ type: "error", error: e.error ?? e.message ?? e });
  }
  flush();
  return out;
}

/** One finished Cursor tool call as a Codex item. */
function cursorItem(call: Json): Json {
  const [kind, body] = Object.entries(call ?? {})[0] ?? ["unknown", {}];
  const a = ((body as Json)?.args as Json) ?? {};
  const result = (body as Json)?.result;
  const shell = (command: string) => ({ type: "command_execution", command, tool: kind });
  switch (kind) {
    case "shellToolCall":
      return { type: "command_execution", command: String(a.command ?? ""), output: strings(result).slice(0, 4000) };
    case "readToolCall":
      return shell(`cat ${a.path ?? ""}`);
    case "lsToolCall":
      return shell(`ls ${a.path ?? "."}`);
    case "grepToolCall":
      return shell(`rg ${JSON.stringify(String(a.pattern ?? ""))} ${a.path ?? "."}`);
    case "globToolCall":
      return shell(`find ${a.targetDirectory ?? "."} -name ${JSON.stringify(String(a.globPattern ?? ""))}`);
    case "semSearchToolCall":
      return shell(`rg ${JSON.stringify(String(a.query ?? ""))}`);
    case "editToolCall":
    case "deleteToolCall":
      return { type: "file_change", path: a.path, tool: kind };
    case "mcpToolCall": {
      // ACM answers in JSON: the longest string in the result that parses as an object is that answer.
      const texts = strings(result).split("\n");
      const json = texts.filter((t) => t.trim().startsWith("{")).sort((x, y) => y.length - x.length)[0];
      const text = json ?? texts.join("\n");
      return {
        type: "mcp_tool_call",
        server: a.providerIdentifier,
        tool: a.toolName ?? a.name,
        arguments: a.args,
        result: { content: [{ type: "text", text }] },
      };
    }
    default:
      return { type: kind, tool: kind };
  }
}

// What an OpenCode provider says when the account can't run more.
const OPENCODE_LIMIT =
  /usage limit|rate.?limit|insufficient (credit|balance|funds|quota)|credit balance|quota|billing|payment required|out of usage/i;

/** OpenCode's JSON events as Codex's: its session is the thread, a finished tool call an item (its reading tools as
 * the shell commands they stand for, ACM's as MCP calls), its steps' tokens the turn's usage. */
export function fromOpenCode(lines: Json[]): Json[] {
  const out: Json[] = [];
  const usage = { input_tokens: 0, cached_input_tokens: 0, output_tokens: 0 };
  let said = "";
  let failed: Json | undefined;
  const flush = () => {
    if (said) out.push({ type: "item.completed", item: { type: "agent_message", text: said } });
    said = "";
  };
  for (const e of lines) {
    const part = (e.part as Json) ?? {};
    if (!out.length && e.sessionID) out.push({ type: "thread.started", thread_id: e.sessionID });
    if (e.type === "text") said += `${said ? "\n" : ""}${String(part.text ?? "")}`;
    else if (e.type === "tool_use") {
      flush();
      for (const item of openCodeItems(part)) out.push({ type: "item.completed", item });
    } else if (e.type === "step_finish") {
      const t = (part.tokens as Record<string, number & Json>) ?? {};
      const cache = (t.cache as Record<string, number>) ?? {};
      usage.input_tokens += (t.input ?? 0) + (cache.read ?? 0) + (cache.write ?? 0);
      usage.cached_input_tokens += cache.read ?? 0;
      usage.output_tokens += (t.output ?? 0) + (t.reasoning ?? 0);
    } else if (e.type === "error") failed = e;
  }
  flush();
  out.push(failed ? { type: "error", error: failed.error ?? failed } : { type: "turn.completed", usage });
  return out;
}

/** One finished OpenCode tool call as Codex items: one, or one per ACM tool an execute call ran. */
function openCodeItems(part: Json): Json[] {
  const state = (part.state as Json) ?? {};
  const a = (state.input as Json) ?? {};
  const result = { content: [{ type: "text", text: String(state.output ?? "") }] };
  // OpenCode 2 calls MCP tools from code it runs, tools.acm.resume(...) in an execute call; its output is their result.
  const acm = part.tool === "execute" ? [...String(a.code ?? "").matchAll(/tools\.acm\.(\w+)/g)].map((m) => m[1]) : [];
  if (acm.length) return acm.map((tool) => ({ type: "mcp_tool_call", server: "acm", tool, arguments: a, result }));
  return [openCodeItem(part)];
}

function openCodeItem(part: Json): Json {
  const tool = String(part.tool ?? "tool");
  const state = (part.state as Json) ?? {};
  const a = (state.input as Json) ?? {};
  const output = String(state.output ?? "");
  const shell = (command: string) => ({ type: "command_execution", command, tool });
  // MCP tools come named server_tool.
  if (tool.startsWith("acm_"))
    return {
      type: "mcp_tool_call",
      server: "acm",
      tool: tool.slice(4),
      arguments: a,
      result: { content: [{ type: "text", text: output }] },
    };
  switch (tool) {
    case "bash":
    case "shell":
      return { type: "command_execution", command: String(a.command ?? ""), output: output.slice(0, 4000) };
    case "read":
      return shell(`cat ${a.filePath ?? a.path ?? ""}`);
    case "list":
      return shell(`ls ${a.path ?? "."}`);
    case "grep":
      return shell(`rg ${JSON.stringify(String(a.pattern ?? ""))} ${a.path ?? "."}`);
    case "glob":
      return shell(`find ${a.path ?? "."} -name ${JSON.stringify(String(a.pattern ?? ""))}`);
    case "edit":
    case "write":
    case "patch":
    case "multiedit":
    case "apply_patch":
      return { type: "file_change", path: a.filePath ?? a.path, tool };
    default:
      return { type: tool, tool };
  }
}

/** The access token of the user's OpenCode login (their Zen or Go subscription), or "" without one. Only that one:
 * not the refresh token, and no other provider's login. It lasts weeks, so no chat here needs to refresh it. */
let openCodeToken: string | undefined;
function openCodeLogin(): string {
  if (openCodeToken !== undefined) return openCodeToken;
  openCodeToken = "";
  try {
    const db = new DatabaseSync(join(homedir(), ".local", "share", "opencode", "opencode.db"), { readOnly: true });
    try {
      const row = db.prepare("SELECT value FROM credential WHERE integration_id = 'opencode' AND active = 1").get() as
        | { value: string }
        | undefined;
      openCodeToken = row ? String((JSON.parse(row.value) as Json).access ?? "") : "";
    } finally {
      db.close();
    }
  } catch {
    // no OpenCode login: free models only
  }
  return openCodeToken;
}

/** An OpenCode chat's settings: no updates, no sharing, nothing from Claude Code's setup, and ACM when the chat's home
 * holds its config (see withAcm). */
function openCodeEnv(home: string): Record<string, string> {
  // The login, in the home's own config, which the logs never keep (they keep OpenCode's data folder only).
  const token = openCodeLogin();
  const config = join(home, ".config", "opencode", "opencode.json");
  if (token && !existsSync(config)) {
    mkdirSync(dirname(config), { recursive: true });
    const options = { options: { apiKey: token } };
    writeFileSync(config, JSON.stringify({ provider: { opencode: options, "opencode-go": options } }), { mode: 0o600 });
  }
  const acm = join(home, ".config", "acm-opencode.json");
  // A port of the home's own for OpenCode's background service: an agent running opencode in the sandbox must not
  // reach the user's own service on the default port, and their chats with it.
  const service = join(home, ".config", "opencode", "service.json");
  if (!existsSync(service)) {
    mkdirSync(dirname(service), { recursive: true });
    writeFileSync(service, JSON.stringify({ port: 50_000 + Math.floor(Math.random() * 10_000) }));
  }
  return {
    OPENCODE_DISABLE_AUTOUPDATE: "1",
    OPENCODE_DISABLE_CLAUDE_CODE: "1",
    OPENCODE_CONFIG_CONTENT: JSON.stringify({ share: "disabled" }),
    ...(existsSync(acm) ? { OPENCODE_CONFIG: acm } : {}),
  };
}

/** ACM for one chat: its own database, and the agent's chats read from chats (a Codex home, Cursor's projects
 * folder, or OpenCode's data folder); no other agent's chats. Codex takes it as flags, Cursor from the mcp.json in
 * the chat's home, OpenCode from a config file there. */
function withAcm(acmHome: string, chats: string, home: string): string[] {
  const none = `${acmHome}-none`;
  const env = {
    ACM_HOME: acmHome,
    CODEX_HOME: AGENT === "codex" ? chats : none,
    CLAUDE_CONFIG_DIR: none,
    CURSOR_TRANSCRIPTS: AGENT === "cursor" ? chats : none,
    OPENCODE_DATA: AGENT === "opencode" ? chats : none,
  };
  const args = [CLI, "mcp", "--harness", AGENT];
  if (AGENT === "opencode") {
    mkdirSync(join(home, ".config"), { recursive: true });
    const server = { type: "local", command: [process.execPath, ...args], environment: env, enabled: true };
    writeFileSync(join(home, ".config", "acm-opencode.json"), JSON.stringify({ mcp: { acm: server } }));
    return [];
  }
  if (AGENT === "cursor") {
    mkdirSync(join(home, ".cursor"), { recursive: true });
    const server = { command: process.execPath, args, env };
    writeFileSync(join(home, ".cursor", "mcp.json"), JSON.stringify({ mcpServers: { acm: server } }));
    return [];
  }
  const table = Object.entries(env)
    .map(([key, value]) => `${key} = ${JSON.stringify(value)}`)
    .join(", ");
  return [
    "-c",
    `mcp_servers.acm.command=${JSON.stringify(process.execPath)}`,
    "-c",
    `mcp_servers.acm.args=${JSON.stringify(args)}`,
    "-c",
    `mcp_servers.acm.env={ ${table} }`,
    "-c",
    'mcp_servers.acm.default_tools_approval_mode="approve"',
  ];
}

/** A task's script (check.py, stale.py) on a folder, as JSON, or {} if it fails. Its temp files, and those of the
 * code it runs, go in a folder of their own, gone afterwards: /tmp may be memory. */
function taskScript(file: string, folder: string): Json {
  const tmp = mkdtempSync(join(tmpdir(), "p-"));
  try {
    const p = spawnSync("python3", [file, folder], {
      cwd: folder,
      encoding: "utf8",
      timeout: 120_000,
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1", TMPDIR: tmp },
    });
    return JSON.parse(p.stdout);
  } catch {
    return {};
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

function check(task: string, folder: string): Checks {
  return taskScript(join(TASKS, task, "check.py"), folder) as Checks;
}

/** The task's check names, after making sure they all fail on repo/ and all pass on solution/. */
function verify(work: string, task: string): string[] {
  const dir = mkdtempSync(join(work, "v-"));
  try {
    const start = join(dir, "start");
    const solved = join(dir, "solved");
    cpSync(join(TASKS, task, "repo"), start, { recursive: true });
    cpSync(start, solved, { recursive: true });
    cpSync(join(TASKS, task, "solution"), solved, { recursive: true });
    const before = check(task, start);
    const after = check(task, solved);
    const names = Object.keys(after);
    if (!names.length || names.some((n) => before[n] !== false || after[n] !== true)) {
      throw new Error(`${task}: its checks must all fail on repo/ and all pass on solution/`);
    }
    return names;
  } finally {
    rmSync(dir, { recursive: true, force: true }); // a solved copy left on disk is an answer key any chat could find
  }
}

/** Where the agent filed a chat in a home: Codex's rollout, or Cursor's transcript (what ACM reads of it). */
function chatPath(home: string, id: string): string | undefined {
  if (AGENT === "cursor") return READERS.cursor.find(join(home, ".cursor", "projects"), id) ?? undefined;
  if (AGENT === "opencode") return READERS.opencode.find(join(home, ".local", "share", "opencode"), id) ?? undefined;
  const base = join(home, ".codex", "sessions");
  try {
    const hit = (readdirSync(base, { recursive: true }) as string[]).find((p) => p.endsWith(`${id}.jsonl`));
    return hit ? join(base, hit) : undefined;
  } catch {
    return undefined;
  }
}

function modelOf(raw: string): { model: string; effort: string } {
  for (const line of raw.split("\n")) {
    if (!line.includes('"turn_context"')) continue;
    const payload = (JSON.parse(line) as Json).payload as Json;
    const settings = ((payload.collaboration_mode as Json)?.settings ?? {}) as Json;
    return { model: String(payload.model), effort: String(payload.effort ?? settings.reasoning_effort ?? "default") };
  }
  return { model: "?", effort: "?" };
}

function threadOf(run: Run): string {
  return String(run.events.find((e) => e.type === "thread.started")?.thread_id);
}

function items(run: Run): Json[] {
  return run.events.filter((e) => e.type === "item.completed").map((e) => e.item as Json);
}

function usageOf(runs: Run[]): Usage {
  const usage = { input: 0, cached: 0, output: 0 };
  for (const e of runs.flatMap((r) => r.events)) {
    if (e.type !== "turn.completed") continue;
    const u = e.usage as Record<string, number>;
    usage.input += u.input_tokens ?? 0;
    usage.cached += u.cached_input_tokens ?? 0;
    usage.output += u.output_tokens ?? 0;
  }
  return usage;
}

/** Why a run ended badly, if it did: a timeout counts against the agent, anything else is the harness's.
 * A turn that completed is fine, even after Codex reconnected on the way. */
function errorOf(run: Run): string | undefined {
  if (run.timedOut) return "timeout";
  if (run.events.some((e) => e.type === "turn.completed")) return undefined;
  const failed = run.events.find((e) => e.type === "turn.failed" || e.type === "error");
  if (failed) return JSON.stringify(failed).slice(0, 300);
  if (run.code) return `exit ${run.code}: ${run.stderr.slice(-300)}`;
  return undefined;
}

/** Commands that reached past the chat's own folder, where a chat without ACM might go looking for the first one. */
function outside(run: Run, folder: string): string[] {
  return items(run).flatMap((item) => {
    if (item?.type !== "command_execution") return [];
    const command = String(item.command).replaceAll(folder, ".");
    return /\/tmp\b|\/home\b|~\/|\$HOME|\.(codex|cursor)\/|share\/opencode|(^|[\s"'])\.\.([/\s"';]|$)/.test(command)
      ? [command.slice(0, 300)]
      : [];
  });
}

/** The JSON an ACM tool call returned, or {} if it failed. */
function acmResult(item: Json): Json {
  try {
    return JSON.parse(String((((item.result as Json)?.content as Json[]) ?? [])[0]?.text));
  } catch {
    return {};
  }
}

/** What the scripted user says next, if the chat stopped to ask. */
function followUp(run: Run): string | undefined {
  const resumed = items(run)
    .filter((i) => i?.type === "mcp_tool_call" && i.server === "acm" && i.tool === "resume")
    .map(acmResult);
  if (resumed.some((r) => r.choose) && !resumed.some((r) => r.messages)) return PICK;
  const last = items(run)
    .filter((i) => i?.type === "agent_message")
    .at(-1);
  return ASKS.test(String(last?.text ?? "").trim()) ? NOTHING : undefined;
}

/** The chat as a user would paste it: what each side said, without tool calls. */
function chatText(raw: string): string {
  return parse(AGENT, Buffer.from(raw))
    .records.map((r) => `${r.role === "user" ? "Me" : NAME}: ${r.text}`)
    .join("\n\n");
}

/** The family a task belongs to (bench/families.json). */
function familyOf(task: string): string {
  return Object.keys(FAMILIES).find((f) => FAMILIES[f].includes(task)) ?? "other";
}

/** A task's planted details (bench/tasks/<task>/details.json), or none. */
function details(task: string): Details {
  const file = join(TASKS, task, "details.json");
  return existsSync(file) ? JSON.parse(readFileSync(file, "utf8")) : {};
}

/** Each planted detail in text: kept (its value is there), stale (only an old or look-alike value is), both, or
 * dropped. Diagnostic, by pattern: the hidden checks decide whether the chat got it right. */
export function survival(text: string, planted: Details): Record<string, string> {
  const has = (patterns: string[] = []) => patterns.some((p) => new RegExp(p, "i").test(text));
  return Object.fromEntries(
    Object.entries(planted).map(([check, d]) => {
      const [now, old] = [has(d.value), has(d.stale)];
      return [check, now && old ? "both" : now ? "kept" : old ? "stale" : "dropped"];
    }),
  );
}

/** Every string in a JSON value, one per line: an ACM tool result as the agent read it. */
function strings(value: unknown): string {
  if (typeof value === "string") return value;
  if (value && typeof value === "object") return Object.values(value).map(strings).filter(Boolean).join("\n");
  return "";
}

/** Where each planted detail first came up in the earlier chats: user (the user said it), agent (the agent said
 * it), tool (only in a command's output), or none. ACM's reader and the pasted chat carry the first two only. */
function sources(chats: Chat[], planted: Details): Record<string, string> {
  // A Cursor transcript, or OpenCode's chat as ACM reads it, holds what each side said, not the tools' output.
  const transcript = (c: Chat): [string, string][] =>
    parse(AGENT, Buffer.from(c.raw)).records.map((r) => [r.role === "user" ? "user" : "agent", r.text]);
  const said = chats.flatMap((c) =>
    AGENT !== "codex"
      ? transcript(c)
      : c.raw.split("\n").flatMap((line): [string, string][] => {
          try {
            const e = JSON.parse(line) as Json;
            const p = e.payload as Json;
            if (e.type !== "response_item" || !p) return [];
            if (p.type === "message" && (p.role === "user" || p.role === "assistant"))
              return [[p.role === "user" ? "user" : "agent", strings(p.content)]];
            return String(p.type).endsWith("_output") ? [["tool", strings(p.output)]] : [];
          } catch {
            return [];
          }
        }),
  );
  return Object.fromEntries(
    Object.entries(planted).map(([check, d]) => {
      const hit = said.find(([, text]) => d.value.some((p) => new RegExp(p, "i").test(text)));
      return [check, hit?.[0] ?? "none"];
    }),
  );
}

// The step rules (bench/PLAN-context-loss.md), applied to each atom: one command of a shell script, split at
// unquoted &&, ||, ; and newlines; a pipeline is one atom, named by its first command.
const ORIENTATION =
  /\bacm\b(?!-bench)|agent-cowork-memory|AGENTS\.md|CODEX_HOME|\.codex\b|\.cursor\b|agent-transcripts|share\/opencode|opencode\.db|\.agents\b|state_5|thread_history|rollout-|\/sessions\b|\.sqlite3?\b/i;
const WRITES = /^(cat|echo|printf)\b[^|]*?>>?\s*(?!\/dev\/null)[^\s&]/;
const NOISE = /^(cd|export|set|unset|echo|printf|true|false|:|done|fi|esac|for|case|\{|\}|\)|\()(\s|$)/;
const VERIFY = /^(python3?|pytest|py\.test|node|make|tox|uv)\b/;
const EXPLORE =
  /^(ls|cat|sed -n|head|tail|rg|grep|egrep|find|git (log|diff|show|status|ls-files|blame|grep)|wc|nl|tree|pwd|stat|file|awk|less|more|du|realpath|readlink|which|type|sort|diff|cmp|test|\[)(\s|$)/;
const EDIT = /^(sed -i|tee|mv|cp|rm|touch|mkdir|chmod|apply_patch|patch|truncate|ln)(\s|$)/;

/** The script a Codex command ran: bash -lc's argument, unquoted, with heredoc bodies (data, not commands) out. */
function script(command: string): string {
  const quoted = /^\S*\bbash -lc (['"])([\s\S]*)\1$/.exec(command);
  let s = command;
  if (quoted?.[1] === "'") s = quoted[2].replaceAll(`'"'"'`, "'");
  if (quoted?.[1] === '"') s = quoted[2].replace(/\\(["$`\\])/g, "$1");
  const kept: string[] = [];
  let body: string | undefined;
  for (const line of s.split("\n")) {
    if (body !== undefined) {
      if (line.trim() === body) body = undefined;
      continue;
    }
    body = /<<-?\s*['"]?(\w+)['"]?/.exec(line)?.[1];
    kept.push(line);
  }
  return kept.join("\n");
}

/** A script's atoms, split outside quotes, keywords that only start a line (if, then, do, ...) taken off. */
export function atomsOf(command: string): string[] {
  const s = script(command);
  const out: string[] = [];
  let quote = "";
  let start = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (quote) {
      if (c === quote) quote = "";
      else if (c === "\\" && quote === '"') i++;
      continue;
    }
    if (c === "'" || c === '"') quote = c;
    else if (c === "\\") i++;
    else if (c === ";" || c === "\n" || ((c === "&" || c === "|") && s[i + 1] === c)) {
      out.push(s.slice(start, i));
      if (c !== ";" && c !== "\n") i++;
      start = i + 1;
    }
  }
  out.push(s.slice(start));
  return out
    .map((a) =>
      a
        .trim()
        .replace(/^((then|do|else|elif|if|while|until|!|\{|\()\s+)+/, "")
        .replace(/^(\w+=\S*\s+)+/, ""),
    )
    .filter((a) => a && !NOISE.test(a));
}

/** The chat's steps by kind: explore (reading, searching), verify (running code), edit, orientation (looking for
 * ACM or for chats on disk, in any arm), other, and memory (ACM's own tool calls). From a trial's log. */
export function classify(log: Json[]): Record<string, number> {
  const counts: Record<string, number> = { explore: 0, verify: 0, edit: 0, orientation: 0, other: 0, memory: 0 };
  for (const e of log) {
    const item = e.item as Json;
    if (e.type !== "item.completed" || !item) continue;
    if (item.type === "mcp_tool_call") counts[item.server === "acm" ? "memory" : "other"]++;
    else if (item.type === "file_change") counts.edit++;
    else if (item.type === "command_execution")
      for (const atom of atomsOf(String(item.command))) {
        if (ORIENTATION.test(atom)) counts.orientation++;
        else if (WRITES.test(atom) || EDIT.test(atom)) counts.edit++;
        else if (VERIFY.test(atom)) counts.verify++;
        else if (EXPLORE.test(atom)) counts.explore++;
        else counts.other++;
      }
  }
  return counts;
}

/** What a trial's log says beyond its checks: its steps by kind, and its planted details in what it was handed
 * (the summary, ACM's resume results, or the pasted chats). */
function measure(task: string, arm: string, log: Json[], summary?: string): Pick<Trial, "atoms" | "kept"> {
  const planted = details(task);
  const resumed = log
    .filter((e) => e.type === "item.completed" && (e.item as Json)?.type === "mcp_tool_call")
    .map((e) => e.item as Json)
    .filter((i) => i.server === "acm" && i.tool === "resume")
    .map((i) => strings(acmResult(i)))
    .join("\n");
  // Only what was pasted: the ask in front of it is the harness's, the same in every run ("oldest first"), in any
  // version of the prompts.
  const pasted =
    arm === "paste" || arm === "pasteall"
      ? String(log[0]?.text ?? "").replace(/^[\s\S]*?(Here is that chat|Here they are, oldest first):\n\n/, "")
      : "";
  const handed = ["summary", "note", "notefile"].includes(arm) ? (summary ?? "") : arm === "named" ? resumed : pasted;
  const kept = arm !== "none" && Object.keys(planted).length ? survival(handed, planted) : undefined;
  return { atoms: classify(log), ...(kept ? { kept } : {}) };
}

/** The summary the user asks the last earlier chat for: one more turn, in a throwaway home holding only that chat,
 * so the chat ACM reads never holds it. In the chat's own sandbox, as the user's request would be: a read-only one
 * makes the summary say so ("this session is read-only"), and that would be pasted too. */
async function summarize(work: string, first: First, request = SUMMARIZE): Promise<Run> {
  const home = mkdtempSync(join(work, "h-"));
  const last = first.chats[first.chats.length - 1];
  let id: string;
  if (AGENT === "cursor") {
    // Cursor resumes a chat from its own store (kept from the earlier chats), and files its transcript by folder.
    id = READERS.cursor.nativeId(last.file);
    const kept = join(LOGS, `${first.task}-cursor`);
    const hash = readdirSync(kept).find((h) => existsSync(join(kept, h, id)));
    cpSync(join(kept, String(hash), id), join(home, ".cursor", "chats", String(hash), id), { recursive: true });
    mkdirSync(dirname(join(home, ".cursor", "projects", last.file)), { recursive: true });
    writeFileSync(join(home, ".cursor", "projects", last.file), last.raw);
  } else if (AGENT === "opencode") {
    // OpenCode resumes a chat from its database, kept from the earlier chats (without the login).
    id = basename(last.file, ".json");
    cpSync(join(LOGS, `${first.task}-opencode`), join(home, ".local", "share", "opencode"), { recursive: true });
  } else {
    const [, y, m, d] = /rollout-(\d{4})-(\d{2})-(\d{2})/.exec(last.file) ?? [];
    id = String(/([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})\.jsonl$/.exec(last.file)?.[1]);
    // Codex finds a chat to resume in its sessions folder, by date, as it filed it.
    const dir = join(home, ".codex", "sessions", y, m, d);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, last.file), last.raw);
  }
  try {
    return await turn(first.at, home, request, resumeArgs(id));
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
}

/** The Markdown files a handoff turn wrote or changed in the folder, each under its name: where an agent asked for a
 * note may have put it. */
function notesWritten(folder: string, before: string): string {
  const changed = (f: string) =>
    !existsSync(join(before, f)) || readFileSync(join(before, f), "utf8") !== readFileSync(join(folder, f), "utf8");
  return fileList(folder)
    .filter((f) => f.endsWith(".md") && changed(f))
    .map((f) => `\n\n${f}:\n\n${readFileSync(join(folder, f), "utf8")}`)
    .join("");
}

async function pool<T, R>(items: T[], fn: (item: T) => Promise<R>): Promise<R[]> {
  const out: R[] = [];
  let next = 0;
  const worker = async () => {
    while (next < items.length && !limited) {
      const i = next++;
      out[i] = await fn(items[i]);
    }
  };
  await Promise.all(Array.from({ length: Number(opt.jobs) }, worker));
  return out;
}

/** The chats a continuation picks up from, run one after another in one home with ACM installed, as a user would
 * have it: so chat-2 can continue chat-1 through ACM, and ACM's notes and threads form as they would. */
async function earlierChats(work: string, task: string, names: string[]): Promise<First | null> {
  const dir = join(TASKS, task);
  const files = existsSync(join(dir, "chat.md")) ? ["chat.md"] : ["chat-1.md", "chat-2.md"];
  for (let tries = 1; tries <= 3; tries++) {
    const at = join(mkdtempSync(join(work, "a-")), task);
    cpSync(join(dir, "repo"), at, { recursive: true });
    git(at, "init", "-q");
    git(at, "add", "-A");
    git(at, "commit", "-qm", "start");
    const home = mkdtempSync(join(work, "h-"));
    const store = mkdtempSync(join(work, "s-"));
    // ACM reads the chats from the agent's own home, as it does for a real user.
    const projects = join(home, ".cursor", "projects");
    const data = join(home, ".local", "share", "opencode");
    const chatsAt = AGENT === "cursor" ? projects : AGENT === "opencode" ? data : join(home, ".codex");
    const extra = withAcm(join(store, "acm"), chatsAt, home);
    const ids: string[] = [];
    let failed: string | undefined;
    let model = "?";
    for (const file of files) {
      if (limited) break;
      const turns = readFileSync(join(dir, file), "utf8").split(/\n---\n/);
      let run = await turn(at, home, say(turns[0].trim()), extra, [store]);
      const id = threadOf(run);
      model = String(run.events.find((e) => e.type === "thread.started")?.model ?? model);
      for (const next of turns.slice(1)) {
        if (errorOf(run)) break;
        run = await turn(at, home, say(next.trim()), [...extra, ...resumeArgs(id)], [store]);
      }
      failed = errorOf(run);
      if (failed) break;
      ids.push(id);
    }
    const found = ids.flatMap((id) => chatPath(home, id) ?? []);
    // Cursor's are kept by their place under its projects folder, where ACM and a resume look for them.
    const chats = found.map((path) => ({
      file: AGENT === "cursor" ? relative(projects, path) : basename(path),
      // OpenCode's chats are in its database: the chat as ACM reads it.
      raw: AGENT === "opencode" ? String(READERS.opencode.read?.(path) ?? "") : readFileSync(path, "utf8"),
    }));
    const checks = check(task, at);
    // Step 1 done and nothing more: otherwise the code would give away what only the chats should hold. Where the
    // repo contradicts the chats, it must still: chats that "fixed" the old README or docstring took the trap away.
    // And no planted value may be written into the repo (a TASK.md that now lists the rules is an answer key).
    const trap = familyOf(task) !== CONTRADICTED || misleads(task, at);
    const leak = leaked(task, at);
    if (
      !failed &&
      trap &&
      !leak.length &&
      chats.length === files.length &&
      names.every((n) => checks[n] === n.startsWith("step1_"))
    ) {
      chats.forEach((c, i) => {
        writeFileSync(join(LOGS, `${task}-chat-${i + 1}.jsonl`), c.raw);
      });
      // Kept next to the logs, so --resume works after /tmp is gone.
      const saved = join(LOGS, `${task}-first`);
      const acm = join(LOGS, `${task}-acm`);
      cpSync(at, saved, { recursive: true });
      cpSync(join(store, "acm"), acm, { recursive: true });
      // Cursor resumes a chat (for its summary) from its own store, not the transcript.
      if (AGENT === "cursor") cpSync(join(home, ".cursor", "chats"), join(LOGS, `${task}-cursor`), { recursive: true });
      // OpenCode resumes one from its database; never the login with it.
      const withoutLogin = (src: string) => !/[/\\](auth\.json|log)$/.test(src);
      if (AGENT === "opencode") cpSync(data, join(LOGS, `${task}-opencode`), { recursive: true, filter: withoutLogin });
      // The home holds the chats twice (their files and the agent's own index): only the copies kept here remain.
      for (const gone of [store, home]) rmSync(gone, { recursive: true, force: true });
      const settings =
        AGENT === "cursor"
          ? {
              model: opt.model ?? model,
              effort: /(?:effort=|-)(low|medium|high|xhigh)(?![a-z])/.exec(opt.model ?? "")?.[1] ?? "default",
            }
          : AGENT === "opencode"
            ? { model: opt.model ?? "default", effort: opt.effort ?? "default" }
            : modelOf(chats[0].raw);
      return { task, at, saved, acm, chats, tries, sources: sources(chats, details(task)), ...settings };
    }
    const why = !trap
      ? "the repo's old value is gone"
      : leak.length
        ? `the earlier chats wrote planted values into the repo: ${leak.join(", ")}`
        : JSON.stringify(checks);
    console.error(`${task}: earlier chats try ${tries} failed: ${failed ?? why}`);
    // The folder may hold step 2, an answer key for the others.
    for (const gone of [dirname(at), store, home]) rmSync(gone, { recursive: true, force: true });
    if (limited) break;
  }
  return null;
}

async function trial(work: string, first: First, arm: string, rep: number): Promise<Trial> {
  const name = `${first.task}-${arm}-${rep}`;
  // Every trial runs in the folder the earlier chats ran in, so their paths and ACM's project match, reset to
  // the state they left it in.
  rmSync(first.at, { recursive: true, force: true });
  mkdirSync(dirname(first.at), { recursive: true });
  cpSync(first.saved, first.at, { recursive: true });
  const home = mkdtempSync(join(work, "h-"));
  const store = mkdtempSync(join(work, "s-"));
  const extra: string[] = [];
  let prompt = say(PROMPTS[arm]);
  let copied = 0;
  // A fresh summary every rep: how much one keeps varies, and that is part of what is measured.
  // The handoff-note arm is the same turn with a careful user's request. Asked for a note, an agent often writes it
  // to HANDOFF.md and answers with a pointer to it, and the folder is reset below: notefile also pastes the Markdown
  // files the turn wrote, as a user copying the note would (exploratory; bench/confirm/PLAN.md, "Deviations").
  const noted = arm === "note" || arm === "notefile";
  const summary = arm === "summary" || noted ? await summarize(work, first, noted ? NOTE : SUMMARIZE) : undefined;
  const written = arm === "notefile" && summary ? notesWritten(first.at, first.saved) : "";
  // Whatever the summary turn touched, the new chat starts where the earlier chats left the folder.
  if (summary) {
    rmSync(first.at, { recursive: true, force: true });
    cpSync(first.saved, first.at, { recursive: true });
  }
  const summarized = summary
    ? String(
        items(summary)
          .filter((i) => i?.type === "agent_message")
          .at(-1)?.text ?? "",
      ) + written
    : "";
  if (summary) {
    prompt += summarized;
    copied = 1;
  }
  if (arm === "named" && AGENT === "opencode") {
    cpSync(first.acm, join(store, "acm"), { recursive: true });
    // OpenCode's chats are in its database, which goes in this chat's own data folder: ACM takes the newest chat
    // there for the one it serves, and the earlier ones are older.
    const data = join(home, ".local", "share", "opencode");
    cpSync(join(LOGS, `${first.task}-opencode`), data, { recursive: true });
    extra.push(...withAcm(join(store, "acm"), data, home));
  } else if (arm === "named" && AGENT === "cursor") {
    cpSync(first.acm, join(store, "acm"), { recursive: true });
    // Cursor's chats go where Cursor files them, in this chat's own home: ACM takes the newest chat there for the
    // one it serves, so the earlier ones are older, in order, as on the user's disk.
    const projects = join(home, ".cursor", "projects");
    first.chats.forEach((c, i) => {
      const file = join(projects, c.file);
      mkdirSync(dirname(file), { recursive: true });
      writeFileSync(file, c.raw);
      const when = new Date(Date.now() - (first.chats.length - i) * 60_000);
      utimesSync(file, when, when);
    });
    extra.push(...withAcm(join(store, "acm"), projects, home));
  } else if (arm === "named") {
    cpSync(first.acm, join(store, "acm"), { recursive: true });
    mkdirSync(join(store, "codex", "sessions"), { recursive: true });
    for (const c of first.chats) {
      const file = join(store, "codex", "sessions", c.file);
      writeFileSync(file, c.raw);
      // Dated as the chat's last line, as on the user's disk: ACM tells the newest chat by it.
      const last = new Date(String((JSON.parse(c.raw.trimEnd().split("\n").at(-1) ?? "{}") as Json).timestamp));
      if (!Number.isNaN(last.getTime())) utimesSync(file, last, last);
    }
    extra.push(...withAcm(join(store, "acm"), join(store, "codex"), home));
  }
  if (arm === "paste") {
    prompt += chatText(first.chats[first.chats.length - 1].raw);
    copied = 1;
  }
  if (arm === "pasteall") {
    prompt += first.chats.map((c, i) => `Chat ${i + 1}:\n\n${chatText(c.raw)}`).join("\n\n");
    copied = first.chats.length;
  }
  const said = [prompt];
  const rw = arm === "named" ? [store] : [];
  // A summary that broke (service, timeout) leaves nothing to paste: the trial carries its error.
  const broke = summary && (errorOf(summary) ?? (summarized ? undefined : "no summary"));
  const runs = broke ? [] : [await turn(first.at, home, prompt, extra, rw)];
  for (let more = 0; more < 2 && runs.length && !errorOf(runs[runs.length - 1]); more++) {
    const reply = followUp(runs[runs.length - 1]);
    if (!reply) break;
    said.push(reply);
    runs.push(await turn(first.at, home, reply, [...extra, ...resumeArgs(threadOf(runs[0]))], rw));
  }
  const all = runs.flatMap((r) => items(r));
  const replies = all.filter((item) => item?.type === "agent_message");
  const log = runs.flatMap((r, i) => [{ type: "user.message", text: said[i] }, ...r.events]);
  const done: Trial = {
    task: first.task,
    arm,
    rep,
    asked: said.reduce((sum, s) => sum + s.length, 0),
    turns: said.length,
    copied,
    checks: check(first.task, first.at),
    strict: strictOf(first.task, first.saved, first.at),
    tools: all.flatMap((item) => (item?.type === "mcp_tool_call" && item.server === "acm" ? [String(item.tool)] : [])),
    outside: runs.flatMap((r) => outside(r, first.at)),
    usage: usageOf(runs),
    // Commands, edits, and tool calls: everything the chat did besides talking and thinking.
    steps: all.filter((item) => item?.type !== "agent_message" && item?.type !== "reasoning").length,
    ...measure(first.task, arm, log, summarized),
    ...(summary ? { summary: summarized, summaryUsage: usageOf([summary]) } : {}),
    seconds: Math.round(runs.reduce((sum, r) => sum + r.seconds, 0)),
    error: broke || runs.map(errorOf).find(Boolean),
    reply: String(replies.at(-1)?.text ?? "").slice(0, 2000),
  };
  writeFileSync(join(LOGS, `${name}.jsonl`), log.map((e) => JSON.stringify(e)).join("\n"));
  if (summary) {
    const asked = [{ type: "user.message", text: noted ? NOTE : SUMMARIZE }, ...summary.events];
    writeFileSync(join(LOGS, `${name}.summary.jsonl`), asked.map((e) => JSON.stringify(e)).join("\n"));
  }
  git(first.at, "add", "-A");
  writeFileSync(
    join(LOGS, `${name}.diff`),
    spawnSync("git", ["-C", first.at, "diff", "--cached"], { encoding: "utf8" }).stdout,
  );
  for (const dir of [home, store]) rmSync(dir, { recursive: true, force: true });
  console.error(
    `${name}: ${Object.values(done.checks).filter(Boolean).length}/${Object.keys(done.checks).length} checks${done.error ? `, ${done.error}` : ""}`,
  );
  return done;
}

// ---- report ----

/** Exact two-sided sign-flip test on per-task differences. The task is the unit: two runs of one task aren't
 * independent. With no real effect, each task's difference is as likely to point either way. Counts the sign
 * patterns by their sum on a grid of 1/scale, so 40 tasks take milliseconds, not 2^40 sums: exact for
 * finish-rate differences (whole multiples of 1/60 with up to 6 runs per arm); token ratios use a finer grid. */
export function signFlip(diffs: number[], scale = 60): number {
  const d = diffs.filter((x) => x !== 0).map((x) => Math.round(Math.abs(x) * scale));
  const total = d.reduce((s, x) => s + x, 0);
  const observed = Math.abs(Math.round(diffs.reduce((s, x) => s + x, 0) * scale));
  // ways[k]: sign patterns whose positive part sums to k; such a pattern sums to 2k - total.
  let ways = new Array(total + 1).fill(0);
  ways[0] = 1;
  for (const x of d) {
    const next = [...ways];
    for (let k = 0; k + x <= total; k++) next[k + x] += ways[k];
    ways = next;
  }
  const hits = ways.reduce((sum, n, k) => (Math.abs(2 * k - total) >= observed ? sum + n : sum), 0);
  return hits / 2 ** d.length;
}

/** The q quantile of the mean per-task difference, resampling tasks (seeded, so reruns agree). */
export function bootstrap(diffs: number[], q: number, draws = 10_000): number {
  let seed = 1;
  const random = () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const means = Array.from({ length: draws }, () => {
    let sum = 0;
    for (let i = 0; i < diffs.length; i++) sum += diffs[Math.floor(random() * diffs.length)];
    return sum / diffs.length;
  }).sort((a, b) => a - b);
  return means[Math.floor(draws * q)];
}

/** One-sided 95% lower bound of the mean per-task difference. */
export function lowerBound(diffs: number[]): number {
  return bootstrap(diffs, 0.05);
}

/** Holm's step-down adjustment, so testing two contrasts doesn't buy a lucky p. */
export function holm(ps: number[]): number[] {
  const out: number[] = [];
  let max = 0;
  ps.map((_, i) => i)
    .sort((i, j) => ps[i] - ps[j])
    .forEach((i, rank) => {
      max = Math.max(max, Math.min(1, (ps.length - rank) * ps[i]));
      out[i] = max;
    });
  return out;
}

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function mean(values: number[]): number {
  return values.reduce((s, x) => s + x, 0) / values.length;
}

/** A difference of two means, without float dust: 2/3 - 2/3 can come out -1e-16, a "loss" in the tally. */
function difference(a: number, b: number): number {
  return Math.round((a - b) * 1e9) / 1e9;
}

function table(result: Result): string {
  // Only the full chat history pasted is compared: the paste and pasteall runs show as one arm.
  const arms = ["none", "named", "summary", "note", "notefile", "pasteall"].filter((a) =>
    result.trials.some((t) => t.arm === a || (a === "pasteall" && t.arm === "paste")),
  );
  const tasks = Object.keys(result.checks);
  const chatsOf = new Map(result.first.map((f) => [String(f.task), ((f.files as string[]) ?? [""]).length]));
  const family = familyOf;
  // Trials the harness broke (quota, network) say nothing about the arm; a timeout is the agent's own failure.
  const scored = result.trials.filter((t) => !t.error || t.error === "timeout");
  const actual = (arm: string, task?: string) => scored.filter((t) => t.arm === arm && (!task || t.task === task));
  // With one earlier chat, pasting all of them is pasting the last one.
  const runs = (arm: string, task: string) =>
    arm === "pasteall" && chatsOf.get(task) === 1 ? actual("paste", task) : actual(arm, task);
  const every = (arm: string) => tasks.flatMap((task) => runs(arm, task));
  // A killed chat never reports its tokens.
  const counted = (ts: Trial[]) => ts.filter((t) => t.usage.input > 0);
  const finished = (t: Trial) => result.checks[t.task].every((n) => t.checks[n]);
  const rate = (ts: Trial[]) => mean(ts.map((t) => +finished(t)));
  const count = (ts: Trial[], pick: (name: string) => boolean) => {
    let k = 0;
    let n = 0;
    for (const t of ts) {
      for (const name of result.checks[t.task].filter(pick)) {
        n += 1;
        if (t.checks[name]) k += 1;
      }
    }
    return `${k}/${n}`;
  };
  const row = (label: string, cell: (arm: string, ts: Trial[]) => string) =>
    `| ${label} | ${arms.map((a) => cell(a, every(a))).join(" | ")} |`;
  const med = (ts: Trial[], value: (t: Trial) => number | undefined) => {
    const xs = ts.flatMap((t) => (value(t) === undefined ? [] : [value(t) as number]));
    return xs.length ? median(xs) : Number.NaN;
  };
  const shown = (x: number, unit = "") => (Number.isNaN(x) ? "–" : `${x.toLocaleString("en")}${unit}`);
  // Steps by kind and planted details exist for runs since bench/PLAN-context-loss.md (or backfilled from logs).
  const atoms = (ts: Trial[], key: string) => ts.flatMap((t) => (t.atoms ? [t.atoms[key]] : []));
  const perRun = (ts: Trial[], key: string) =>
    atoms(ts, key).length ? (Math.round(mean(atoms(ts, key)) * 10) / 10).toFixed(1) : "–";
  const handed = (ts: Trial[]) => {
    const states = ts.flatMap((t) => Object.values(t.kept ?? {}));
    if (!states.length) return "–";
    const share = (s: string) => `${Math.round((100 * states.filter((x) => x === s).length) / states.length)}%`;
    return `kept ${share("kept")}, both ${share("both")}, stale ${share("stale")}, dropped ${share("dropped")}`;
  };
  const models = [...new Set(result.first.map((f) => `${f.model}, ${f.effort} effort`))].join("; ");
  const lines = [
    `${result.cli ?? result.codex} (${models}), ACM ${result.acm}, ${String(result.date).slice(0, 10)}`,
    "",
    `| | ${arms.map((a) => ARMS[a]).join(" | ")} |`,
    `|---|${arms.map(() => "---").join("|")}|`,
    row("Finished the task (every check passes)", (_, ts) => `${ts.filter(finished).length}/${ts.length} runs`),
    row("Did what only the earlier chats said", (_, ts) => count(ts, (n) => DETAIL.test(n))),
    row("Kept the earlier chats' work", (_, ts) => count(ts, (n) => n.startsWith("step1_"))),
    row("What the user typed or pasted, median", (_, ts) =>
      shown(
        med(ts, (t) => t.asked),
        " chars",
      ),
    ),
    row("Messages the user sent, median", (_, ts) => shown(med(ts, (t) => t.turns))),
    row("Chats the user found and copied", (_, ts) => shown(med(ts, (t) => t.copied))),
    row("Called ACM's resume", (a, ts) =>
      a === "named" ? `${ts.filter((t) => t.tools.includes("resume")).length}/${ts.length}` : "–",
    ),
    row(
      "Input tokens, median (uncached)",
      (_, ts) =>
        `${Math.round(med(counted(ts), (t) => t.usage.input) / 1000)}k (${Math.round(med(counted(ts), (t) => t.usage.input - t.usage.cached) / 1000)}k)`,
    ),
    row("Output tokens, median", (_, ts) => `${Math.round(med(counted(ts), (t) => t.usage.output) / 100) / 10}k`),
    row("Steps (commands, edits, tool calls), median", (_, ts) => `${med(ts, (t) => t.steps)}`),
    row("Explore steps, mean per run", (_, ts) => perRun(ts, "explore")),
    row("Looking for ACM or chat stores, mean per run", (_, ts) => perRun(ts, "orientation")),
    row("Planted details in what the chat was handed", (_, ts) => handed(ts)),
    row("Input tokens per handoff, counting writing the summary, median", (_, ts) =>
      shown(Math.round(med(counted(ts), (t) => t.usage.input + (t.summaryUsage?.input ?? 0)) / 1000), "k"),
    ),
    row("Tokens to write the summary, median", (a, ts) =>
      a === "summary" ? shown(Math.round(med(ts, (t) => t.summaryUsage?.input) / 1000), "k") : "–",
    ),
    row("Minutes per continuation, median", (_, ts) => `${Math.round(med(ts, (t) => t.seconds) / 6) / 10}`),
  ];

  // Per family: how often each arm finished.
  const families = Object.keys(FAMILIES).filter((f) => tasks.some((t) => family(t) === f));
  lines.push("", `| Earlier chats | Tasks | ${arms.map((a) => ARMS[a]).join(" | ")} |`);
  lines.push(`|---|---|${arms.map(() => "---").join("|")}|`);
  for (const f of families) {
    const ts = tasks.filter((t) => family(t) === f);
    const cells = arms.map((a) => {
      const all = ts.flatMap((t) => runs(a, t));
      return all.length ? `${all.filter(finished).length}/${all.length}` : "–";
    });
    lines.push(`| ${f} | ${ts.length} | ${cells.join(" | ")} |`);
  }

  // The planned tests (bench/PLAN.md): per-task differences in finish rate, exact sign-flip; H2 was dropped.
  const diffs = (a: string, b: string, pick: (task: string) => boolean) =>
    tasks.filter(pick).flatMap((task) => {
      const [x, y] = [runs(a, task), runs(b, task)];
      return x.length && y.length ? [difference(rate(x), rate(y))] : [];
    });
  const pct = (x: number) => `${Math.round(x * 100)} points`;
  const tally = (d: number[]) =>
    `better on ${d.filter((x) => x > 0).length} tasks, worse on ${d.filter((x) => x < 0).length}, tied on ${d.filter((x) => x === 0).length}`;
  const summary = (d: number[], test: string) =>
    d.length ? `${tally(d)}; mean ${pct(mean(d))}; ${test}` : "no tasks yet";
  const h1 = diffs("named", "none", () => true);
  const h3 = diffs("named", "pasteall", (t) => family(t) !== "corrected mid-chat");
  const fmt = (p: number) => (p < 0.001 ? "<0.001" : p.toPrecision(2));
  lines.push(
    "",
    `- H1, ACM vs no ACM, ${h1.length} tasks: ${summary(h1, `exact p = ${fmt(signFlip(h1))}`)}`,
    `- H3, ACM vs the full chat history pasted, ${h3.length} tasks: ${summary(h3, `95% lower bound ${pct(lowerBound(h3))} (non-inferior if above -10 points)`)}`,
  );
  // Secondary, reported whichever way they go: tokens, and the mid-chat change.
  const tokens = (a: string, b: string, pick: (task: string) => boolean) => {
    const d = tasks.filter(pick).flatMap((task) => {
      const [x, y] = [counted(runs(a, task)), counted(runs(b, task))];
      return x.length && y.length
        ? [Math.log(mean(x.map((t) => t.usage.input)) / mean(y.map((t) => t.usage.input)))]
        : [];
    });
    if (!d.length) return "no tasks yet";
    return `${Math.round(Math.exp(mean(d)) * 100) / 100}× the input tokens (geometric mean over ${d.length} tasks), more on ${d.filter((x) => x > 0).length}, fewer on ${d.filter((x) => x < 0).length}; sign-flip p = ${fmt(signFlip(d, 1000))}`;
  };
  const mid = diffs("named", "pasteall", (t) => family(t) === "corrected mid-chat");
  lines.push(
    `- Secondary: ACM vs the full chat history pasted, ${tokens("named", "pasteall", () => true)}`,
    `- Secondary: ACM vs the full chat history pasted, corrected mid-chat, ${mid.length} tasks: ${summary(mid, `exact p = ${fmt(signFlip(mid))}`)}`,
  );

  // The admission rule (bench/PLAN.md, bench/PLAN-context-loss.md), for the pilot: the full history pasted always
  // finished, and no ACM never did; where the repo can tell, no ACM explored at least 2 steps more instead.
  const admitted = tasks.filter((t) => {
    const [none, all] = [runs("none", t), runs("pasteall", t)];
    if (!none.length || !all.length || !all.every(finished)) return false;
    return family(t) === RECOVERABLE
      ? mean(atoms(none, "explore")) - mean(atoms(all, "explore")) >= 2
      : !none.some(finished);
  });

  // bench/PLAN-context-loss.md: ACM against the summary pasted, two-sided, Holm over H1 and H2. Each difference
  // points ACM's way when positive.
  if (arms.includes("summary")) {
    // B and C were admitted at stage 2. The A tasks were admitted with another model, so each enters H1 only when
    // this run's own No ACM and full-history runs pass the rule; the rule never looks at ACM or the summary.
    const inPlay = (t: string) => [RECOVERABLE, CONTRADICTED].includes(family(t)) || admitted.includes(t);
    const out = tasks.filter((t) => !inPlay(t));
    const right = (ts: Trial[]) =>
      mean(
        ts.map((t) => {
          const names = result.checks[t.task].filter((n) => DETAIL.test(n));
          return names.filter((n) => t.checks[n]).length / names.length;
        }),
      );
    const explore = (ts: Trial[]) => mean(atoms(ts, "explore"));
    const paired = (pick: (task: string) => boolean, value: (ts: Trial[]) => number, a: string, b: string) =>
      tasks.filter(pick).flatMap((task) => {
        const d = difference(value(runs(a, task)), value(runs(b, task)));
        return Number.isNaN(d) ? [] : [d];
      });
    const c1 = paired((t) => family(t) !== RECOVERABLE && inPlay(t), right, "named", "summary");
    const c2 = paired((t) => family(t) === RECOVERABLE, explore, "summary", "named");
    // Grids fine enough to be exact: shares of up to 10 checks over up to 6 runs, and means of whole steps.
    const raw = [c1.length ? signFlip(c1, 2520) : 1, c2.length ? signFlip(c2, 60) : 1];
    const adjusted = holm(raw);
    const steps = (x: number) => `${x.toFixed(1)} steps`;
    const verdict = (d: number[], i: number, margin: number, unit: (x: number) => string) => {
      if (!d.length) return "no tasks yet";
      const [lo, hi] = [bootstrap(d, 0.025), bootstrap(d, 0.975)];
      const read =
        adjusted[i] < 0.05
          ? mean(d) > 0
            ? "ACM loses less context"
            : "the summary loses less context"
          : hi < margin
            ? `no meaningful difference (rules out an ACM advantage of ${unit(margin)})`
            : "not settled";
      return `${tally(d)}; mean ${unit(mean(d))}, 95% interval ${unit(lo)} to ${unit(hi)}; exact p = ${fmt(raw[i])}, Holm ${fmt(adjusted[i])}: ${read}`;
    };
    // A missed detail was either not in what the chat was handed, or handed and not used.
    const missed = (a: string) => {
      let [gone, unused] = [0, 0];
      for (const t of every(a))
        for (const n of result.checks[t.task].filter((n) => DETAIL.test(n) && !t.checks[n] && t.kept?.[n])) {
          if (t.kept?.[n] === "kept" || t.kept?.[n] === "both") unused++;
          else gone++;
        }
      return `${gone} not handed, ${unused} handed but not used`;
    };
    const sourceOf = new Map(result.first.map((f) => [String(f.task), (f.sources ?? {}) as Record<string, string>]));
    const bySource = (a: string) =>
      ["user", "agent", "tool"]
        .flatMap((s) => {
          const hits = every(a).flatMap((t) =>
            Object.entries(sourceOf.get(t.task) ?? {}).flatMap(([n, src]) =>
              src === s && n in t.checks ? [t.checks[n]] : [],
            ),
          );
          return hits.length ? [`${s} ${hits.filter(Boolean).length}/${hits.length}`] : [];
        })
        .join(", ") || "–";
    lines.push(
      "",
      "Context loss, ACM against the summary pasted (bench/PLAN-context-loss.md):",
      "",
      `- H1, planted details right, ${c1.length} tasks: ${verdict(c1, 0, 0.05, pct)}`,
      `  (left out of H1 by the admission rule on this run's No ACM and full-history runs: ${out.join(", ") || "none"})`,
      `- H2, explore steps per run (summary minus ACM), ${c2.length} tasks recoverable from the repo: ${verdict(c2, 1, 0.5, steps)}`,
      `- Missed planted details: summary ${missed("summary")}; ACM ${missed("named")}`,
      `- Planted details right, by where they first came up: summary ${bySource("summary")}; ACM ${bySource("named")}; full history ${bySource("pasteall")}`,
      `- Secondary: ACM vs the summary pasted, ${tokens("named", "summary", () => true)}`,
    );
  }

  // Strict scoring (bench/PLAN-context-loss.md), for runs that have it (from the run, or --rescore).
  if (result.trials.some((t) => t.strict)) {
    const strict = (t: Trial) => strictPass(t.checks, result.checks[t.task], t.strict);
    const cell = (ts: Trial[], hit: (t: Trial) => boolean) => `${ts.filter(hit).length}/${ts.length}`;
    lines.push(
      "",
      "Strict scoring (bench/PLAN-context-loss.md):",
      "",
      `| | ${arms.map((a) => ARMS[a]).join(" | ")} |`,
      `|---|${arms.map(() => "---").join("|")}|`,
      row(
        "Passed strictly: every check, no test broken, no file deleted, kept what the user said to leave, no old value",
        (_, ts) => cell(ts, strict),
      ),
      row("Didn't use the repo's default where no chat gave a value (fabrication controls)", (_, ts) =>
        cell(ts, (t) => Object.entries(t.strict?.stale ?? {}).some(([n, v]) => v && n.startsWith("fab_"))),
      ),
      row("Implemented an old or look-alike value", (_, ts) =>
        cell(ts, (t) => Object.entries(t.strict?.stale ?? {}).some(([n, v]) => v && !n.startsWith("fab_"))),
      ),
      row("Broke a test that passed when the earlier chats ended", (_, ts) =>
        cell(ts, (t) => !!t.strict?.regressed.length),
      ),
      row("Deleted a file the earlier chats left", (_, ts) => cell(ts, (t) => !!t.strict?.deleted.length)),
      row("Changed text the user said to leave as it is", (_, ts) => cell(ts, (t) => t.strict?.kept === false)),
      row("Tasks passed strictly in all 3 runs (pass^3)", (a) => {
        const all = tasks.filter((k) => runs(a, k).length >= 3 && runs(a, k).every(strict));
        return `${all.length}/${tasks.filter((k) => runs(a, k).length >= 3).length}`;
      }),
    );
    lines.push("", `| Passed strictly, by earlier chats | Tasks | ${arms.map((a) => ARMS[a]).join(" | ")} |`);
    lines.push(`|---|---|${arms.map(() => "---").join("|")}|`);
    for (const f of families) {
      const ts = tasks.filter((k) => family(k) === f);
      lines.push(
        `| ${f} | ${ts.length} | ${arms
          .map((a) =>
            cell(
              ts.flatMap((k) => runs(a, k)),
              strict,
            ),
          )
          .join(" | ")} |`,
      );
    }
    // Strict comparisons, per task, the share of runs that pass strictly, ACM minus the other arm; no admission rule,
    // and tasks whose earlier chats wrote a planted value into the repo left out. Against the summary, on the tasks
    // whose details live in chats (A and C): the strict H1. The others are exploratory.
    const leakedTasks = tasks.filter(
      (k) => existsSync(join(LOGS, `${k}-first`)) && leaked(k, join(LOGS, `${k}-first`)).length,
    );
    const strictRate = (ts: Trial[]) => mean(ts.map((t) => +strict(t)));
    const versus = (other: string, pick: (k: string) => boolean) =>
      tasks
        .filter((k) => pick(k) && !leakedTasks.includes(k))
        .flatMap((k) => {
          const x = difference(strictRate(runs("named", k)), strictRate(runs(other, k)));
          return Number.isNaN(x) ? [] : [x];
        });
    const line = (label: string, d: number[]) =>
      `- ${label}, ${d.length} tasks: ${d.length ? `${tally(d)}; mean ${pct(mean(d))}, 95% interval ${pct(bootstrap(d, 0.025))} to ${pct(bootstrap(d, 0.975))}; exact p = ${fmt(signFlip(d, 2520))}` : "no tasks yet"}`;
    const inChats = (k: string) => family(k) !== RECOVERABLE;
    lines.push(
      "",
      `Strict comparisons, runs passed strictly per task (no admission rule; left out, their earlier chats leaked a planted value into the repo: ${leakedTasks.join(", ") || "none"}):`,
      "",
      ...(arms.includes("summary")
        ? [line("Strict H1, ACM vs the summary pasted (A and C)", versus("summary", inChats))]
        : []),
      line(
        "Exploratory, ACM vs no ACM (all tasks)",
        versus("none", () => true),
      ),
      line("Exploratory, ACM vs the full chat history pasted (A and C)", versus("pasteall", inChats)),
    );
  }

  lines.push(
    "",
    `Pass the admission rule (the full history pasted always finished; no ACM never did, or where the repo can tell, explored at least 2 steps more): ${admitted.length}/${tasks.length}: ${admitted.join(",")}`,
  );
  const dropped = result.trials.length - scored.length;
  if (dropped)
    lines.push(
      "",
      `${dropped} trial(s) left out: the run broke for reasons outside the agent (see error in the results file).`,
    );

  lines.push("", `| Task | Earlier chats | ${arms.map((a) => ARMS[a]).join(" | ")} |`);
  lines.push(`|---|---|${arms.map(() => "---").join("|")}|`);
  for (const task of tasks) {
    const cells = arms.map((a) => {
      const ts = runs(a, task);
      return `${ts.filter(finished).length}/${ts.length}`;
    });
    lines.push(`| ${task} | ${family(task)} | ${cells.join(" | ")} |`);
  }
  const recoverable = tasks.filter((t) => family(t) === RECOVERABLE);
  if (recoverable.length) {
    lines.push("", `| Explore steps, mean per run | ${arms.map((a) => ARMS[a]).join(" | ")} |`);
    lines.push(`|---|${arms.map(() => "---").join("|")}|`);
    for (const task of recoverable)
      lines.push(`| ${task} | ${arms.map((a) => perRun(runs(a, task), "explore")).join(" | ")} |`);
  }
  return lines.join("\n");
}

/** Steps by kind and planted details for a finished run's trials and earlier chats, from its logs: for runs from
 * before they were recorded. Rewrites the file; a trial whose log is gone keeps what it has. */
function backfill(file: string): void {
  const result: Result = JSON.parse(readFileSync(file, "utf8"));
  const lines = (path: string) =>
    existsSync(path)
      ? readFileSync(path, "utf8")
          .split("\n")
          .flatMap((l) => {
            try {
              return [JSON.parse(l) as Json];
            } catch {
              return [];
            }
          })
      : undefined;
  for (const t of result.trials) {
    const log = lines(join(LOGS, `${t.task}-${t.arm}-${t.rep}.jsonl`));
    if (log) Object.assign(t, measure(t.task, t.arm, log, t.summary));
  }
  for (const f of result.first) {
    const files = ((f.files as string[]) ?? []).map((file, i) => [file, join(LOGS, `${f.task}-chat-${i + 1}.jsonl`)]);
    if (!files.length || !files.every(([, path]) => existsSync(path))) continue;
    const chats = files.map(([file, path]) => ({ file, raw: readFileSync(path, "utf8") }));
    f.sources = sources(chats, details(String(f.task)));
  }
  writeFileSync(file, `${JSON.stringify(result, null, 1)}\n`);
}

/** Every file in a folder, one after another: what an agent could read there. */
function filesIn(dir: string): string {
  return readdirSync(dir, { recursive: true, withFileTypes: true })
    .filter((e) => e.isFile() && !/[/\\](\.git|__pycache__)([/\\]|$)/.test(e.parentPath))
    .map((e) => readFileSync(join(e.parentPath, e.name), "utf8"))
    .join("\n");
}

type Made = { task: string; rep: number; text: string; kept: Record<string, string>; usage: Usage; error?: string };

/** Stage 1 of bench/PLAN-context-loss.md: --reps summaries of each task's saved earlier chats in a finished run,
 * scored for its planted details; no continuations. Kept in summaries.json next to the run, so it resumes. */
async function summaries(file: string): Promise<void> {
  const result: Result = JSON.parse(readFileSync(file, "utf8"));
  const out = join(dirname(file), "summaries.json");
  const made: Made[] = existsSync(out) ? JSON.parse(readFileSync(out, "utf8")).summaries : [];
  const codexVersion = spawnSync("codex", ["--version"], { encoding: "utf8" }).stdout.trim();
  const save = () =>
    writeFileSync(
      out,
      `${JSON.stringify({ codex: codexVersion, model: opt.model ?? "default", effort: opt.effort ?? "default", prompt: SUMMARIZE, summaries: made }, null, 1)}\n`,
    );
  const work = mkdtempSync(join(tmpdir(), "w-"));
  const wanted = TASK_LIST;
  try {
    canary(work);
    const firsts = result.first.flatMap((entry) => {
      const first = saved(entry);
      return first && wanted.includes(first.task) ? [first] : [];
    });
    await pool(firsts, async (first) => {
      for (let rep = 1; rep <= Number(opt.reps); rep++) {
        if (limited || made.some((m) => m.task === first.task && m.rep === rep)) continue;
        let made1: Made | undefined;
        // A summary the service broke says nothing: try it again, a minute later.
        for (let again = 0; again < 3 && !limited && (!made1 || (made1.error && made1.error !== "timeout")); again++) {
          if (again) await new Promise((resolve) => setTimeout(resolve, 60_000));
          // The folder the earlier chats left, at their path, as the summary turn would find it.
          rmSync(first.at, { recursive: true, force: true });
          mkdirSync(dirname(first.at), { recursive: true });
          cpSync(first.saved, first.at, { recursive: true });
          const run = await summarize(work, first);
          const text = String(
            items(run)
              .filter((i) => i?.type === "agent_message")
              .at(-1)?.text ?? "",
          );
          const error = errorOf(run) ?? (text ? undefined : "no summary");
          made1 = {
            task: first.task,
            rep,
            text,
            kept: survival(text, details(first.task)),
            usage: usageOf([run]),
            error,
          };
        }
        if (limited || !made1) return;
        made.push(made1);
        save();
      }
      rmSync(dirname(first.at), { recursive: true, force: true });
    });
    save();
    console.log(gate(made));
    if (limited) {
      console.error(`Stopped: ${limited}\nRun it again once the limit resets; it resumes.`);
      process.exitCode = 3;
    }
  } finally {
    rmSync(work, { recursive: true, force: true });
  }
}

/** How much of each family's planted details the summaries kept, and the gate's reading (bench/PLAN-context-loss.md). */
function gate(made: Made[]): string {
  const family = familyOf;
  const states = ["kept", "both", "stale", "dropped"];
  const count = (ms: Made[]) =>
    states.map((s) => ms.flatMap((m) => Object.values(m.kept)).filter((x) => x === s).length);
  const ok = made.filter((m) => !m.error);
  const lines = [
    `| Earlier chats | Summaries | Details | ${states.join(" | ")} |`,
    `|---|---|---|${states.map(() => "---").join("|")}|`,
  ];
  for (const f of Object.keys(FAMILIES)) {
    const ms = ok.filter((m) => family(m.task) === f);
    if (!ms.length) continue;
    const c = count(ms);
    lines.push(`| ${f} | ${ms.length} | ${c.reduce((s, x) => s + x, 0)} | ${c.join(" | ")} |`);
  }
  // The gate counts the A families only: B and C have their own chats, made at stage 2.
  const a = ok.filter((m) => ![RECOVERABLE, CONTRADICTED].includes(family(m.task)));
  const c = count(a);
  const total = c.reduce((s, x) => s + x, 0);
  const kept = total ? c[0] / total : Number.NaN;
  lines.push(
    "",
    `Summaries: ${ok.length} made, ${made.length - ok.length} broke; median ${median(ok.map((m) => m.text.length))} characters, ${Math.round(median(ok.map((m) => m.usage.input)) / 1000)}k input tokens to write.`,
    `Gate: the summaries kept ${Math.round(kept * 100)}% of the A tasks' ${total} planted details right (${c[1]} with an old value beside, ${c[2]} only old, ${c[3]} dropped). ${kept >= 0.95 ? "At least 95%: the A part of H1 is expected to tie; ask the user before stage 2." : "Under 95%: summaries lose details; stage 2 can go ahead."}`,
    "",
    "Not kept, to check by hand:",
    ...ok.flatMap((m) =>
      Object.entries(m.kept)
        .filter(([, s]) => s !== "kept")
        .map(([check, s]) => `- ${m.task} #${m.rep} ${check}: ${s}`),
    ),
  );
  return lines.join("\n");
}

/** Whether a folder still holds one of a task's old values: what a task the repo contradicts is built on. */
function misleads(task: string, folder: string): boolean {
  const text = filesIn(folder);
  return Object.values(details(task)).some((d) => (d.stale ?? []).some((p) => new RegExp(p, "i").test(text)));
}

/** Planted details whose value a folder holds and the task's start repo doesn't: the earlier chats wrote an answer
 * into the repo, so even a chat without them could read it. Tasks recoverable from the repo hold theirs by design. */
export function leaked(task: string, folder: string): string[] {
  if (familyOf(task) === RECOVERABLE) return [];
  const [start, now] = [filesIn(join(TASKS, task, "repo")), filesIn(folder)];
  return Object.entries(details(task)).flatMap(([check, d]) =>
    d.value.some((p) => !new RegExp(p, "i").test(start) && new RegExp(p, "i").test(now)) ? [check] : [],
  );
}

// ---- strict scoring (bench/PLAN-context-loss.md, "Strict scoring") ----

// A task's strict.json: text the user said to leave as it is (keep), and plausible wrong solutions (mutants/<name>/,
// overlaid on repo/ like solution/), each with the checks it must fail (breaks) and the stale verdicts it must raise.
type StrictSpec = {
  keep?: { file: string; text: string }[];
  mutants?: Record<string, { breaks: string[]; stale?: string[]; why?: string }>;
};
// What strict success needs besides every check passing: the repo's tests that passed when the earlier chats ended
// still pass (regressed lists the rest), no file of theirs was deleted, the text the user said to leave is still
// there (kept; null where nothing was), and no old or look-alike value was implemented (stale, from stale.py).
type Strict = { regressed: string[]; deleted: string[]; kept: boolean | null; stale: Record<string, boolean> };

function strictSpec(task: string): StrictSpec {
  const file = join(TASKS, task, "strict.json");
  return existsSync(file) ? JSON.parse(readFileSync(file, "utf8")) : {};
}

/** A folder's files as relative paths, git's store and caches aside. */
function fileList(dir: string): string[] {
  return readdirSync(dir, { recursive: true, withFileTypes: true })
    .filter((e) => e.isFile() && !/(^|[/\\])(\.git|__pycache__)([/\\]|$)/.test(relative(dir, e.parentPath)))
    .map((e) => relative(dir, join(e.parentPath, e.name)));
}

// Runs every test*.py and *_test.py in a folder with unittest and writes each test's outcome, by id, to a file:
// tests print to stdout, so it can't carry the result.
const TESTS_PY = `
import json, os, pathlib, sys, unittest
root = pathlib.Path(sys.argv[1]).resolve(); sys.path.insert(0, str(root)); os.chdir(root)
out = {}
class Result(unittest.TestResult):
    def addSuccess(self, t): out[t.id()] = "ok"
    def addFailure(self, t, e): out[t.id()] = "fail"
    def addError(self, t, e): out[t.id()] = "error"
    def addSkip(self, t, r): out[t.id()] = "skip"
    def addExpectedFailure(self, t, e): out[t.id()] = "ok"
    def addUnexpectedSuccess(self, t): out[t.id()] = "fail"
for p in sorted(root.rglob("*.py")):
    if ".git" in p.parts or "__pycache__" in p.parts or not (p.name.startswith("test") or p.name.endswith("_test.py")):
        continue
    name = ".".join(p.relative_to(root).with_suffix("").parts)
    try:
        unittest.defaultTestLoader.loadTestsFromName(name).run(Result())
    except Exception:
        out[name] = "error"
pathlib.Path(sys.argv[2]).write_text(json.dumps(out))
`;

/** The repo's own tests in a copy of a folder (so they can't change it), by id: ok, fail, error, or skip. */
function repoTests(folder: string): Record<string, string> {
  const dir = mkdtempSync(join(tmpdir(), "t-"));
  try {
    cpSync(folder, join(dir, "repo"), { recursive: true });
    const out = join(dir, "tests.json");
    spawnSync("python3", ["-c", TESTS_PY, join(dir, "repo"), out], {
      cwd: join(dir, "repo"),
      timeout: 120_000,
      // The tests' own temp files go in this folder, gone below.
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1", TMPDIR: dir },
      stdio: "ignore",
    });
    return existsSync(out) ? JSON.parse(readFileSync(out, "utf8")) : {};
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

/** stale.py's verdicts on a folder: true where it does what an old or look-alike value says. */
function staleOf(task: string, folder: string): Record<string, boolean> {
  const file = join(TASKS, task, "stale.py");
  return existsSync(file) ? (taskScript(file, folder) as Record<string, boolean>) : {};
}

/** Strict scoring of a run's final folder against the folder the earlier chats left (before). */
function strictOf(task: string, before: string, after: string, testsBefore = repoTests(before)): Strict {
  const now = repoTests(after);
  const have = new Set(fileList(after));
  const keep = strictSpec(task).keep ?? [];
  const holds = (k: { file: string; text: string }) =>
    existsSync(join(after, k.file)) && readFileSync(join(after, k.file), "utf8").includes(k.text);
  return {
    regressed: Object.keys(testsBefore).filter((id) => testsBefore[id] === "ok" && now[id] !== "ok"),
    deleted: fileList(before).filter((p) => !have.has(p)),
    kept: keep.length ? keep.every(holds) : null,
    stale: staleOf(task, after),
  };
}

/** Whether a run passes strictly: every check, and nothing in Strict against it. */
export function strictPass(checks: Checks, names: string[], s: Strict | undefined): boolean {
  if (!s) return false;
  return (
    names.every((n) => checks[n]) &&
    !s.regressed.length &&
    !s.deleted.length &&
    s.kept !== false &&
    !Object.values(s.stale).some(Boolean)
  );
}

/** A diff's file sections without bytecode or other binary files, which git apply can't take from a text diff. */
function textOnly(diff: string): string {
  return diff
    .split(/(?=^diff --git )/m)
    .filter(
      (s) => s.startsWith("diff --git ") && !/__pycache__|\.pyc\b/.test(s.split("\n")[0]) && !/^Binary files /m.test(s),
    )
    .join("");
}

/** Strict scoring for a finished run, from its logs: each run's final folder is its task's start repo with the run's
 * diff applied, scored against the earlier chats' saved end state. Rewrites the file. */
function rescore(file: string): void {
  const result: Result = JSON.parse(readFileSync(file, "utf8"));
  const work = mkdtempSync(join(tmpdir(), "r-"));
  const before = new Map<string, Record<string, string>>();
  let [scored, differ, broken] = [0, 0, 0];
  try {
    const wanted = new Set(TASK_LIST);
    for (const t of result.trials) {
      if (!wanted.has(t.task)) continue;
      const diff = join(LOGS, `${t.task}-${t.arm}-${t.rep}.diff`);
      const saved = join(LOGS, `${t.task}-first`);
      if (!existsSync(diff) || !existsSync(saved)) continue;
      const after = join(work, `${t.task}-${t.arm}-${t.rep}`);
      cpSync(join(TASKS, t.task, "repo"), after, { recursive: true });
      const patch = textOnly(readFileSync(diff, "utf8"));
      const applied = !patch.trim()
        ? 0
        : spawnSync("git", ["apply", "--whitespace=nowarn", "-"], { cwd: after, input: patch }).status;
      if (applied !== 0) {
        broken++;
        rmSync(after, { recursive: true, force: true });
        continue;
      }
      // The rebuilt folder must score as the run did; if not, the rebuild (or a flaky check) is off.
      const checks = check(t.task, after);
      if (Object.keys(t.checks).some((n) => checks[n] !== t.checks[n])) differ++;
      if (!before.has(t.task)) before.set(t.task, repoTests(saved));
      t.strict = strictOf(t.task, saved, after, before.get(t.task));
      scored++;
      rmSync(after, { recursive: true, force: true });
    }
  } finally {
    rmSync(work, { recursive: true, force: true });
  }
  writeFileSync(file, `${JSON.stringify(result, null, 1)}\n`);
  console.error(
    `rescored ${scored} runs; ${differ} rebuilt folders scored differently from the run; ${broken} diffs didn't apply`,
  );
}

/** The SHA-256 of what a run of this suite runs on: the harness, ACM's code, the suite's plan (up to its Freeze
 * section, which records this hash), families, and tasks. --frozen makes a run refuse anything else. */
function freezeHash(): string {
  const plan = join(SUITE, "PLAN.md");
  const files = [
    join(import.meta.dirname, "live.ts"),
    ...fileList(join(ACM, "src")).map((p) => join(ACM, "src", p)),
    join(SUITE, "families.json"),
    ...fileList(TASKS).map((p) => join(TASKS, p)),
  ].sort();
  const h = createHash("sha256");
  for (const f of files)
    h.update(`${relative(REPO, f)}\0`)
      .update(readFileSync(f))
      .update("\0");
  if (existsSync(plan)) h.update(readFileSync(plan, "utf8").split("\n## Freeze")[0]);
  return h.digest("hex");
}

/** A run's full-history trials of a task: paste with one earlier chat, pasteall with two. */
function fullOf(result: Result, task: string): string {
  const files = (result.first.find((f) => f.task === task)?.files as string[]) ?? [""];
  return files.length > 1 ? "pasteall" : "paste";
}

/** bench/confirm/PLAN.md's pilot admission: the full history pasted finished strictly in every run, and No ACM in
 * none. Prints the admitted tasks, ready for --tasks. Never looks at ACM or the pasted handoffs. */
function admit(file: string): void {
  const result: Result = JSON.parse(readFileSync(file, "utf8"));
  const strict = (t: Trial) => strictPass(t.checks, result.checks[t.task], t.strict);
  const of = (task: string, arm: string) => result.trials.filter((t) => t.task === task && t.arm === arm);
  const tasks = Object.keys(result.checks);
  const admitted = tasks.filter((k) => {
    const [none, full] = [of(k, "none"), of(k, fullOf(result, k))];
    return none.length && full.length && full.every(strict) && !none.some(strict);
  });
  console.error(
    `admitted ${admitted.length}/${tasks.length}; out: ${tasks.filter((k) => !admitted.includes(k)).join(", ") || "none"}`,
  );
  console.log(admitted.join(","));
}

/** bench/confirm/PLAN.md's analysis, fixed before the run, over its two histories (one results file each). */
function confirmatory(files: string[]): string {
  const histories: Result[] = files.map((f) => JSON.parse(readFileSync(f, "utf8")));
  const tasks = Object.keys(histories[0].checks).filter((k) => histories.every((h) => k in h.checks));
  const family = (task: string) => Object.keys(FAMILIES).find((f) => FAMILIES[f].includes(task)) ?? "other";
  const ok = (t: Trial) => !t.error || t.error === "timeout";
  const trialsOf = (hs: Result[], task: string, arm: string) =>
    hs.flatMap((h) =>
      h.trials
        .filter((t) => ok(t) && t.task === task && t.arm === (arm === "full" ? fullOf(h, task) : arm))
        .map((t) => ({ t, h })),
    );
  const strictRate = (xs: { t: Trial; h: Result }[]) =>
    mean(xs.map(({ t, h }) => +strictPass(t.checks, h.checks[t.task], t.strict)));
  const detailRate = (xs: { t: Trial; h: Result }[], keep?: (n: string) => boolean) =>
    mean(
      xs.map(({ t, h }) => {
        const names = h.checks[t.task].filter((n) => DETAIL.test(n) && (!keep || keep(n)));
        return names.length ? names.filter((n) => t.checks[n]).length / names.length : Number.NaN;
      }),
    );
  const diffs = (hs: Result[], other: string, value = strictRate, pick: (k: string) => boolean = () => true) =>
    tasks.filter(pick).flatMap((k) => {
      const d = difference(value(trialsOf(hs, k, "named")), value(trialsOf(hs, k, other)));
      return Number.isNaN(d) ? [] : [d];
    });
  const pct = (x: number) => `${Math.round(x * 100)} points`;
  const fmt = (p: number) => (p < 0.001 ? "<0.001" : p.toPrecision(2));
  const describe = (d: number[]) =>
    d.length
      ? `${d.length} tasks, ACM ahead on ${d.filter((x) => x > 0).length}, behind on ${d.filter((x) => x < 0).length}; mean ${pct(mean(d))}, 95% interval ${pct(bootstrap(d, 0.025))} to ${pct(bootstrap(d, 0.975))}; exact p = ${fmt(signFlip(d, 2520))}`
      : "no tasks";
  // H1b's note: the note pasted, or for a run that has only the corrected way, the note with the files it wrote
  // (bench/confirm/PLAN.md, "Deviations").
  const has = (arm: string) => histories.some((h) => h.trials.some((t) => t.arm === arm));
  const note = has("notefile") && !has("note") ? "notefile" : "note";
  const [a, b] = [diffs(histories, "summary"), diffs(histories, note)];
  const raw = [signFlip(a, 2520), signFlip(b, 2520)];
  const [pa, pb] = holm(raw);
  const full = diffs(histories, "full");
  const each = histories.map((h) => [diffs([h], "summary"), diffs([h], note)]);
  const count = (arm: string, prefix: string) => {
    const xs = tasks.flatMap((k) => trialsOf(histories, k, arm));
    return xs.filter(({ t }) =>
      Object.entries(t.strict?.stale ?? {}).some(([n, v]) => v && (prefix === "fab_") === n.startsWith("fab_")),
    ).length;
  };
  const wrong = (arm: string) => count(arm, "fab_") + count(arm, "stale_");
  const passes =
    pa < 0.05 &&
    pb < 0.05 &&
    mean(a) >= 0.15 &&
    mean(b) >= 0.15 &&
    each.every(([x, y]) => mean(x) > 0 && mean(y) > 0) &&
    wrong("named") <= wrong("summary") &&
    wrong("named") <= wrong(note) &&
    lowerBound(full) > -0.05;
  const lines = [
    `Confirmatory analysis (bench/confirm/PLAN.md), ${tasks.length} tasks, ${histories.length} histories; frozen at ${histories.map((h) => String(h.frozen ?? "?").slice(0, 12)).join(", ")}`,
    "",
    `- H1a, ACM vs the summary pasted, runs finished strictly: ${describe(a)}; Holm ${fmt(pa)}`,
    `- H1b, ACM vs the ${ARMS[note].toLowerCase()}, runs finished strictly: ${describe(b)}; Holm ${fmt(pb)}`,
    `- H2, ACM vs the full history pasted: ${describe(full)}; one-sided 95% lower bound ${pct(lowerBound(full))} (non-inferior if above -5 points)`,
    ...each.map(([x, y], i) => `- History ${i + 1} alone: vs summary ${describe(x)}; vs note ${describe(y)}`),
    `- Old or look-alike values implemented / repo default not used where no chat gave a value, runs: ${["none", "named", "summary", note, "full"].map((arm) => `${ARMS[arm === "full" ? "pasteall" : arm]} ${count(arm, "stale_")}/${count(arm, "fab_")}`).join("; ")}`,
    "",
    `Decision rule: ${passes ? "met. ACM loses less context than a pasted summary or handoff note." : "not met; the README says which parts held."}`,
    "",
    "Sensitivity (reported whichever way it goes, not used for the decision):",
    ...Object.keys(FAMILIES).map(
      (f) => `- Without ${f}: vs summary ${describe(diffs(histories, "summary", strictRate, (k) => family(k) !== f))}`,
    ),
    `- Details done right instead of strict finishing: vs summary ${describe(diffs(histories, "summary", detailRate))}; vs note ${describe(diffs(histories, note, detailRate))}`,
  ];
  // Only the details no-context runs never got right: what a chat can't guess.
  const guessed = new Set(
    tasks.flatMap((k) =>
      trialsOf(histories, k, "none").flatMap(({ t }) =>
        Object.keys(t.checks)
          .filter((n) => DETAIL.test(n) && t.checks[n])
          .map((n) => `${k}.${n}`),
      ),
    ),
  );
  const unguessed = (xs: { t: Trial; h: Result }[]) => detailRate(xs, (n) => !guessed.has(`${xs[0]?.t.task}.${n}`));
  lines.push(
    `- Only details No ACM never got right: vs summary ${describe(diffs(histories, "summary", unguessed))}; vs note ${describe(diffs(histories, note, unguessed))}`,
  );
  return lines.join("\n");
}

/** The checks strict.json holds a task to, without Codex: solution-2/ (a second, independent solution) passes every
 * check; each mutant fails exactly the checks it names and raises exactly its stale verdicts; stale.py says nothing
 * against either solution; the text to keep is in the start repo and survives the solutions. Throws on the first
 * that doesn't. Returns the detail checks no mutant fails: nothing shows they would catch a wrong value. */
function strictChecks(work: string, task: string, names: string[]): string[] {
  const spec = strictSpec(task);
  const dir = join(TASKS, task);
  const solved = (overlay: string, run: (folder: string) => void) => {
    const folder = mkdtempSync(join(work, "s-"));
    try {
      cpSync(join(dir, "repo"), folder, { recursive: true });
      cpSync(join(dir, overlay), folder, { recursive: true });
      run(folder);
    } finally {
      rmSync(folder, { recursive: true, force: true }); // a solved copy is an answer key
    }
  };
  const quiet = (folder: string, which: string, expect: string[] = []) => {
    const verdicts = staleOf(task, folder);
    const raised = Object.keys(verdicts).filter((n) => verdicts[n]);
    if (raised.sort().join() !== [...expect].sort().join())
      throw new Error(`${task}: stale.py on ${which} raised [${raised}], expected [${expect}]`);
  };
  for (const overlay of ["solution", "solution-2"].filter((o) => existsSync(join(dir, o)))) {
    solved(overlay, (folder) => {
      const failing = names.filter((n) => !check(task, folder)[n]);
      if (failing.length) throw new Error(`${task}: ${overlay} fails ${failing.join(", ")}`);
      quiet(folder, overlay);
      for (const k of spec.keep ?? [])
        if (!readFileSync(join(folder, k.file), "utf8").includes(k.text))
          throw new Error(`${task}: ${overlay} changes ${k.file}'s "${k.text}", which the user said to leave`);
    });
  }
  for (const k of spec.keep ?? [])
    if (!readFileSync(join(dir, "repo", k.file), "utf8").includes(k.text))
      throw new Error(`${task}: strict.json keeps "${k.text}" in ${k.file}, which the start repo doesn't have`);
  for (const [name, m] of Object.entries(spec.mutants ?? {})) {
    solved(join("mutants", name), (folder) => {
      const checks = check(task, folder);
      const failing = names.filter((n) => !checks[n]);
      if (failing.sort().join() !== [...m.breaks].sort().join())
        throw new Error(`${task}: mutant ${name} fails [${failing}], strict.json says [${m.breaks}]`);
      quiet(folder, `mutant ${name}`, m.stale);
    });
  }
  const caught = new Set(Object.values(spec.mutants ?? {}).flatMap((m) => m.breaks));
  return Object.keys(spec.mutants ?? {}).length
    ? names.filter((n) => (DETAIL.test(n) || n.startsWith("found_")) && !caught.has(n))
    : [];
}

/** Without Codex: every task's checks fail on repo/ and pass on solution/, and its planted details are checks it
 * has. Each value is stated in its chats, or for a task recoverable from the repo, in its repo; a task the repo
 * contradicts has the old value there. Throws on the first task that isn't so. */
function verifyTasks(tasks: string[]): void {
  const work = mkdtempSync(join(tmpdir(), "v-"));
  const family = familyOf;
  try {
    for (const task of tasks) {
      const names = verify(work, task);
      const files = existsSync(join(TASKS, task, "chat.md")) ? ["chat.md"] : ["chat-1.md", "chat-2.md"];
      const said = files.map((f) => readFileSync(join(TASKS, task, f), "utf8")).join("\n");
      const repo = filesIn(join(TASKS, task, "repo"));
      const planted = details(task);
      // One wording of each is enough there: the others are for a summary that puts it differently.
      const where = (text: string, patterns: string[], place: string, check: string) => {
        if (patterns.length && !patterns.some((p) => new RegExp(p, "i").test(text)))
          throw new Error(`${task}: none of ${check}'s patterns is in its ${place}`);
      };
      for (const [check, d] of Object.entries(planted)) {
        if (!names.includes(check)) throw new Error(`${task}: details.json names ${check}, which check.py doesn't run`);
        where(
          family(task) === RECOVERABLE ? repo : said,
          d.value,
          family(task) === RECOVERABLE ? "repo" : "chats",
          check,
        );
        // An old value the repo contradicts the chats with may also be one the chats themselves replaced.
        where(
          family(task) === CONTRADICTED ? `${repo}\n${said}` : said,
          d.stale ?? [],
          family(task) === CONTRADICTED ? "repo or chats" : "chats",
          check,
        );
      }
      if (family(task) === CONTRADICTED && !misleads(task, join(TASKS, task, "repo")))
        throw new Error(`${task}: no planted detail's old value is in its repo`);
      const unplanted = names.filter((n) => DETAIL.test(n) && !(n in planted));
      const weak = strictChecks(work, task, names);
      const notes = [
        ...(unplanted.length ? [`no details.json entry for ${unplanted.join(", ")}`] : []),
        ...(weak.length ? [`no mutant fails ${weak.join(", ")}`] : []),
      ];
      console.log(`${task}: ok${notes.length ? ` (${notes.join("; ")})` : ""}`);
    }
  } finally {
    rmSync(work, { recursive: true, force: true });
  }
}

/** The earlier chats a resumed run saved, or null if their folder is gone. */
function saved(entry: Json): First | null {
  const task = String(entry.task);
  const files = (entry.files as string[]) ?? [];
  const chats = files.map((file, i) => ({
    file,
    raw: readFileSync(join(LOGS, `${task}-chat-${i + 1}.jsonl`), "utf8"),
  }));
  const [folder, acm] = [join(LOGS, `${task}-first`), join(LOGS, `${task}-acm`)];
  if (!existsSync(folder) || !existsSync(acm) || !files.length) return null;
  return { ...(entry as Omit<First, "saved" | "acm" | "chats">), saved: folder, acm, chats };
}

// ---- main ----

if (import.meta.main && opt.report) {
  console.log(table(JSON.parse(readFileSync(opt.report, "utf8"))));
} else if (import.meta.main && opt.backfill) {
  backfill(opt.backfill);
} else if (import.meta.main && opt.rescore) {
  rescore(opt.rescore);
} else if (import.meta.main && opt.summaries) {
  await summaries(opt.summaries);
} else if (import.meta.main && opt.hash) {
  console.log(freezeHash());
} else if (import.meta.main && opt.admit) {
  admit(opt.admit);
} else if (import.meta.main && opt.confirm) {
  console.log(confirmatory(opt.confirm.split(",")));
} else if (import.meta.main && opt.verify) {
  verifyTasks(TASK_LIST);
} else if (import.meta.main) {
  const tasks = TASK_LIST;
  const arms = opt.arms.split(",").map((spec) => {
    const [arm, reps = opt.reps] = spec.split(":");
    if (!(arm in ARMS)) throw new Error(`unknown arm ${arm}: use ${Object.keys(ARMS).join(", ")}`);
    return { arm, reps: Number(reps) };
  });
  const old: Result | undefined = opt.resume ? JSON.parse(readFileSync(opt.out, "utf8")) : undefined;
  // A frozen plan runs only on what it froze: harness, ACM, plan, and tasks hash to what it recorded.
  const frozen = freezeHash();
  if (opt.frozen && opt.frozen !== frozen)
    throw new Error(`what this run would use hashes to ${frozen}, not the frozen ${opt.frozen}`);
  // A fresh run clears its logs folder: never under a finished run's results.
  if (!old && existsSync(opt.out)) throw new Error(`${opt.out} holds a finished run: pass --resume, or another --out`);
  // Every run in one results file uses one agent, model and effort: a resume can't mix in another.
  if (old && (old.agent ?? "codex") !== AGENT)
    throw new Error(`${opt.out} was run with ${old.agent ?? "codex"}, not ${AGENT}`);
  const setting = `${opt.model ?? "default"}, ${opt.effort ?? "default"}`;
  if (old && `${old.model ?? "default"}, ${old.effort ?? "default"}` !== setting)
    throw new Error(
      `${opt.out} was run with ${old.model ?? "default"}, ${old.effort ?? "default"}; resume it with the same --model and --effort, not ${setting}`,
    );
  // A plain name: agents read every path they are given, and one that says "acm" sends them looking for it.
  const work = mkdtempSync(join(tmpdir(), "w-"));
  if (!old) rmSync(LOGS, { recursive: true, force: true });
  mkdirSync(LOGS, { recursive: true });
  console.error(`work folder: ${work}\nlogs: ${LOGS}`);
  try {
    canary(work);
    const checks = Object.fromEntries(tasks.map((t) => [t, verify(work, t)]));
    const bin = AGENT === "cursor" ? "cursor-agent" : AGENT;
    const version = `${AGENT === "codex" ? "" : `${bin} `}${spawnSync(bin, ["--version"], { encoding: "utf8" }).stdout.trim()}`;
    const result: Result = {
      date: old?.date ?? new Date().toISOString(),
      acm: VERSION,
      agent: AGENT,
      cli: [old?.cli ?? old?.codex, version].filter((v, i, all) => v && all.indexOf(v) === i).join(", then "),
      node: process.version,
      model: opt.model ?? "default",
      effort: opt.effort ?? "default",
      frozen,
      prompts: Object.fromEntries(
        Object.entries({ ...PROMPTS, summarize: SUMMARIZE, note: NOTE, pick: PICK, nothing: NOTHING }).map(([k, v]) => [
          k,
          say(v),
        ]),
      ),
      arms: Object.fromEntries(arms.map((a) => [a.arm, a.reps])),
      checks,
      first: old?.first ?? [],
      trials: old?.trials ?? [],
    };
    if (old) result.resumed = [...((old.resumed as string[]) ?? []), new Date().toISOString()];
    const save = () => writeFileSync(opt.out, `${JSON.stringify(result, null, 1)}\n`);
    const most = Math.max(...arms.map((a) => a.reps));
    // Tasks run side by side; one task's chats run one after another, so none can find another arm's work.
    await pool(tasks, async (task) => {
      const ran = (arm: string, rep: number) =>
        result.trials.some((t) => t.task === task && t.arm === arm && t.rep === rep);
      const before = result.first.find((f) => f.task === task);
      let first = before ? saved(before) : null;
      if (!first && before && result.trials.some((t) => t.task === task)) {
        // Its trials need the earlier chats' end state, and that is gone: the rest can't be paired.
        console.error(`${task}: the earlier chats' folder is gone, skipping its remaining trials`);
        return;
      }
      if (!first) {
        result.first = result.first.filter((f) => f.task !== task);
        first = await earlierChats(work, task, checks[task]);
        if (!first && limited) return;
        if (!first) {
          delete checks[task];
          save();
          return;
        }
        const { saved: _, acm: __, chats, ...entry } = first;
        result.first.push({ ...entry, files: chats.map((c) => c.file) });
        save();
      }
      for (let rep = 1; rep <= most; rep++) {
        // The arms swap order each rep, so none always goes first.
        for (const { arm, reps } of rep % 2 ? arms : [...arms].reverse()) {
          // The full history is paste with one earlier chat, pasteall with two: each runs only where it is that.
          if (limited) return;
          const one = first.chats.length === 1;
          if (rep > reps || ran(arm, rep) || (arm === "pasteall" && one) || (arm === "paste" && !one)) continue;
          // A run the service broke (capacity, 503) says nothing about the arm: try it again, a minute later.
          let tried = await trial(work, first, arm, rep);
          for (let again = 1; again < 3 && tried.error && tried.error !== "timeout" && !limited; again++) {
            await new Promise((resolve) => setTimeout(resolve, 60_000));
            tried = await trial(work, first, arm, rep);
          }
          // Cut short by the usage limit: not the agent's doing, so it runs again on --resume.
          if (limited) return;
          result.trials.push(tried);
          save();
        }
      }
      rmSync(dirname(first.at), { recursive: true, force: true });
    });
    save();
    console.log(table(result));
    if (limited) {
      console.error(`Stopped: ${limited}\nRun it again with --resume once that's fixed.`);
      process.exitCode = 3;
    }
  } finally {
    rmSync(work, { recursive: true, force: true });
  }
}
