import { McpServer } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import * as z from "zod";
import { connect, type Db } from "./db.ts";
import { card, type Deps, defaultDeps, delegate, delegateWait, type Task } from "./delegate.ts";
import { context, noteAdd, noteSearch, type Session, sessionFor } from "./memory.ts";
import { projectRoot } from "./project.ts";
import { obj, text } from "./readers/index.ts";
import { chats, currentChat, HARNESSES, type Pin, resume } from "./transcript.ts";
import { AcmError, debug } from "./util.ts";
import { VERSION } from "./version.ts";

const CONTEXT =
  "Call before working and before you edit a file. Returns your thread (related work across chats and agents) with its timeline, the project's notes (after the first call, only what's new), open threads, recent jobs, who is working, and held files. hold: repo-relative paths to claim before writing; a path in busy is someone else's, leave it; [] releases yours. thread: join that thread (from open_threads or your brief). done: true closes your thread. stale lists notes whose files changed: re-check each with note_add.";
const NOTE_ADD =
  "Save a note every agent in this project sees. tier long: stays true (decisions, conventions, gotchas, the user's preferences); short (default): progress and findings, kept 7 days. If the result has check, those notes are on the same topic: if yours makes one false, call again with supersedes set to its id. supersedes also confirms (same text) or corrects a stale note. Job results are saved already.";
const NOTE_SEARCH = "Search this project's notes and delegated job results.";
const CHATS =
  "List recent chats in this project from every agent, newest first: agent, chat id, updated, folder, thread, first message, and job (when acm started the chat). Pass the chat the user picks to resume.";
const RESUME =
  "Call when the user says continue, or wants a chat from another agent. source: one agent (codex, cursor, claude, opencode); chat: one chat id (from chats). Without chat, if several match the result has choose: show it to the user, ask which, and call again with its chat; never pick for them. Otherwise it returns the recent messages and puts you on that chat's thread: carry on from the last user message.";
const DELEGATE =
  "Call when the user asks other agents (codex, claude, cursor, opencode) to do something. Each starts in this project with your brief, in a herdr pane if herdr is installed, else in the background; one agent per kind per folder. summary: the problem, for someone who hasn't seen this chat. tasks: [{to, task, done_when?, context?}]. If the result has next, call delegate_wait until no job is running. A busy agent comes back busy with the free ones: ask the user whether to wait (same task, wait: true) or reassign; never choose for them. The result starts with a card (lines beginning 'acm · delegate'): copy it into your reply as-is in a code block, then report each job. Never answer a blocked agent or approve a needs_approval for the user.";
const DELEGATE_WAIT =
  "Wait up to 45 seconds more for your delegated agents, then report their states. Copy the result's card (the lines before the JSON) into your reply as-is in a code block.";
// In the result too, not only the description: weaker models skip the description.
const REPLY =
  "Start your reply with the card above this JSON, copied as-is in a code block; most agents don't show tool output.";

// What each tool does, for hosts that warn before risky calls and directories that require all four hints.
// delegate is the one that reaches out: it starts other agents in auto mode, and they can edit files and run commands.
const hint = (readOnlyHint: boolean, destructiveHint: boolean, idempotentHint: boolean, openWorldHint: boolean) => ({
  readOnlyHint,
  destructiveHint,
  idempotentHint,
  openWorldHint,
});
const HINTS = {
  context: hint(false, false, true, false), // holds files and joins or closes threads; repeating changes nothing more
  note_add: hint(false, false, false, false), // each call adds a note; a replaced note is kept, not deleted
  note_search: hint(true, false, true, false),
  chats: hint(true, false, true, false), // reads the agents' local chat files
  resume: hint(false, false, true, false), // puts this chat on the resumed chat's thread
  delegate: hint(false, true, false, true),
  delegate_wait: hint(false, false, true, false), // refreshes jobs, and may send a waiting agent its brief
};

const repoPath = z.string().optional(); // defaults to the folder the agent started acm in

type Ctx = { mcpReq: { _meta?: Record<string, unknown>; envelope?: Record<string, unknown> } };
type Result = { content: { type: "text"; text: string }[]; isError?: boolean };

export function clientHarness(name: string | undefined): string | null {
  const lower = (name ?? "").toLowerCase();
  return HARNESSES.find((h) => lower.includes(h)) ?? null;
}

function json(data: unknown): Result {
  return { content: [{ type: "text", text: JSON.stringify(data) }] };
}

/** The card first, for the person reading; the JSON after it, for the model. A blank line keeps them apart
 * in Claude Code, which joins text blocks as they are. No structured content: Claude Code shows that instead. */
function shown(cardText: string, data: Record<string, unknown>): Result {
  return {
    content: [
      { type: "text", text: `${cardText}\n\n` },
      { type: "text", text: JSON.stringify({ ...data, reply: REPLY }) },
    ],
  };
}

export type ServerOptions = { home: string; harness?: string; deps?: Deps; roots?: Record<string, string> };

export function buildServer(opts: ServerOptions, db: Db = connect(opts.home)): McpServer {
  const server = new McpServer({ name: "acm", version: VERSION }, { capabilities: { tools: {} } });
  const roots = opts.roots ?? {};

  function harnessOf(ctx: Ctx): string {
    if (opts.harness) return opts.harness;
    const info = obj(
      ctx.mcpReq.envelope?.["io.modelcontextprotocol/clientInfo"] ??
        ctx.mcpReq._meta?.["io.modelcontextprotocol/clientInfo"],
    );
    const name = text(info.name) || server.server.getClientVersion()?.name;
    const found = clientHarness(name);
    if (!found) {
      throw new AcmError(
        "harness",
        `Unknown MCP client ${JSON.stringify(name ?? "")}. Start acm with: acm mcp --harness ${HARNESSES.join("|")}`,
      );
    }
    return found;
  }

  // The chat this process is in, per agent and project; see currentChat.
  const pins = new Map<string, Pin>();

  /** This chat's session. Codex says which chat it is; for the others this process remembers its chat. */
  function session(ctx: Ctx, repo?: string): Session {
    const harness = harnessOf(ctx);
    const folder = repo || process.cwd();
    let chat = harness === "codex" ? text(obj(ctx.mcpReq._meta?.["x-codex-turn-metadata"]).session_id) : "";
    if (!chat) {
      const root = projectRoot(folder);
      const key = `${harness} ${root}`;
      // Claude Code and OpenCode pass acm's variable on to the servers they start; Cursor and Codex strip it.
      const delegated = harness === "claude" || harness === "opencode" ? process.env.ACM_DELEGATED === "1" : null;
      const pin = currentChat(harness, root, roots, pins.get(key), delegated);
      if (pin) pins.set(key, pin);
      chat = pin?.chat ?? `proc:${process.pid}`;
    }
    return sessionFor(db, { harness, chat, folder });
  }

  async function run(tool: string, fn: () => Result | Promise<Result>): Promise<Result> {
    const t0 = performance.now();
    try {
      return await fn();
    } catch (caught) {
      let err = caught;
      if (err instanceof Error && /readonly database/.test(err.message)) {
        err = new AcmError(
          "unavailable",
          "acm can't write its database: this acm runs inside a sandbox. Use the acm tools your agent already has instead of starting acm yourself.",
        );
      }
      if (err instanceof AcmError) {
        return {
          content: [{ type: "text", text: JSON.stringify({ error: err.code, ...err.payload }) }],
          isError: true,
        };
      }
      throw err;
    } finally {
      debug(`tool ${tool}`, t0);
    }
  }

  server.registerTool(
    "context",
    {
      description: CONTEXT,
      annotations: HINTS.context,
      inputSchema: z.object({
        repo_path: repoPath,
        hold: z.array(z.string()).optional(),
        thread: z.string().optional(),
        done: z.boolean().optional(),
      }),
    },
    (args, ctx) =>
      run("context", () => {
        const s = session(ctx, args.repo_path);
        return json(context(db, s, { hold: args.hold, thread: args.thread, done: args.done }));
      }),
  );

  server.registerTool(
    "note_add",
    {
      description: NOTE_ADD,
      annotations: HINTS.note_add,
      inputSchema: z.object({
        text: z.string(),
        tier: z.enum(["short", "long"]).optional(),
        supersedes: z.string().optional(),
        repo_path: repoPath,
      }),
    },
    (args, ctx) => run("note_add", () => json(noteAdd(db, session(ctx, args.repo_path), args))),
  );

  server.registerTool(
    "note_search",
    {
      description: NOTE_SEARCH,
      annotations: HINTS.note_search,
      inputSchema: z.object({ query: z.string(), repo_path: repoPath }),
    },
    (args, ctx) =>
      run("note_search", () => {
        const s = session(ctx, args.repo_path);
        return json({ thread: s.thread_id, ...noteSearch(db, s, args.query) });
      }),
  );

  server.registerTool(
    "chats",
    {
      description: CHATS,
      annotations: HINTS.chats,
      inputSchema: z.object({ limit: z.number().optional(), repo_path: repoPath }),
    },
    (args, ctx) =>
      run("chats", () => {
        const s = session(ctx, args.repo_path);
        return json({ thread: s.thread_id, ...chats(db, s, args.limit ?? 20, roots) });
      }),
  );

  server.registerTool(
    "resume",
    {
      description: RESUME,
      annotations: HINTS.resume,
      inputSchema: z.object({
        source: z.enum(["codex", "cursor", "claude", "opencode"]).optional(),
        chat: z.string().optional(),
        repo_path: repoPath,
      }),
    },
    (args, ctx) =>
      run("resume", () =>
        json(resume(db, session(ctx, args.repo_path), { source: args.source, chat: args.chat, roots })),
      ),
  );

  const task = z.object({
    to: z.enum(["codex", "claude", "cursor", "opencode"]),
    task: z.string(),
    done_when: z.string().optional(),
    context: z.string().optional(),
    wait: z.boolean().optional(),
  });
  server.registerTool(
    "delegate",
    {
      description: DELEGATE,
      annotations: HINTS.delegate,
      inputSchema: z.object({ summary: z.string(), tasks: z.array(task), repo_path: repoPath }),
    },
    (args, ctx) =>
      run("delegate", async () => {
        const deps = opts.deps ?? defaultDeps(roots);
        const out = await delegate(db, session(ctx, args.repo_path), {
          summary: args.summary,
          tasks: args.tasks as Task[],
          home: opts.home,
          deps,
        });
        return shown(card(out, args.tasks as Task[]), out);
      }),
  );

  server.registerTool(
    "delegate_wait",
    { description: DELEGATE_WAIT, annotations: HINTS.delegate_wait, inputSchema: z.object({ repo_path: repoPath }) },
    (args, ctx) =>
      run("delegate_wait", async () => {
        const out = await delegateWait(db, session(ctx, args.repo_path), {
          home: opts.home,
          deps: opts.deps ?? defaultDeps(roots),
        });
        return shown(card(out), out);
      }),
  );

  return server;
}

export async function serve(home: string, harness?: string): Promise<void> {
  if (harness && !HARNESSES.includes(harness))
    throw new AcmError("invalid", `--harness must be one of ${HARNESSES.join(", ")}`);
  const db = connect(home);
  serveStdio(() => buildServer({ home, harness }, db));
}
