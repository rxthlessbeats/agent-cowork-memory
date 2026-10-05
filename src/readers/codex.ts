import { readdirSync } from "node:fs";
import { homedir } from "node:os";
import { basename, join } from "node:path";
import { type Chat, firstObjects, isFile, type Json, mtime, obj, type Reader, related, text } from "./index.ts";

const SKIP_TYPES = new Set(["session_meta", "event_msg", "token_usage_record", "turn_context", "world_state"]);
const SKIP_PAYLOAD = new Set([
  "reasoning",
  "function_call",
  "function_call_output",
  "custom_tool_call",
  "custom_tool_call_output",
]);
const RECENT = 200; // ponytail: only the newest 200 rollouts are checked; raise it if older chats need resuming

function rollouts(base: string): string[] {
  try {
    return (readdirSync(base, { recursive: true }) as string[])
      .filter((p) => /(^|[\\/])rollout-[^\\/]*\.jsonl$/.test(p))
      .map((p) => join(base, p))
      .filter(isFile);
  } catch {
    return [];
  }
}

function meta(path: string): Json {
  const first = firstObjects(path, 1)[0] ?? {};
  return first.type === "session_meta" ? obj(first.payload) : {};
}

export const codex: Reader = {
  root: () => join(process.env.CODEX_HOME || join(homedir(), ".codex"), "sessions"),

  chats(base, repoRoot) {
    const found: Chat[] = [];
    const recent = rollouts(base)
      .map((path) => ({ path, mtime: mtime(path) }))
      .sort((a, b) => b.mtime - a.mtime)
      .slice(0, RECENT);
    for (const { path, mtime: m } of recent) {
      const info = meta(path);
      const cwd = text(info.cwd);
      // Codex's own subagents (auto-review "guardian" chats) run in the folder too, but nobody typed them.
      const subagent =
        (typeof info.source === "object" && info.source !== null) ||
        (info.thread_source && info.thread_source !== "user");
      if (cwd && !subagent && related(cwd, repoRoot)) found.push({ path, workspace: cwd, mtime: m });
    }
    return found;
  },

  find: (base, native) => rollouts(base).find((p) => basename(p).endsWith(`${native}.jsonl`)) ?? null,

  nativeId: (path) => text(meta(path).session_id) || basename(path, ".jsonl"),

  turnEnded: (o) => o.type === "event_msg" && obj(o.payload).type === "task_complete",

  turnError: (o) => text(obj(obj(o.payload).error).message),

  visible(o) {
    const kind = text(o.type);
    if (SKIP_TYPES.has(kind)) return ["skip", []];
    if (kind !== "response_item") return ["unknown", []];
    const payload = obj(o.payload);
    const ptype = text(payload.type);
    const role = text(payload.role);
    if (SKIP_PAYLOAD.has(ptype) || role === "developer") return ["skip", []];
    if (ptype !== "message" || (role !== "user" && role !== "assistant")) return ["unknown", []];
    const texts = (Array.isArray(payload.content) ? payload.content : [])
      .map(obj)
      .filter((b) => (b.type === "input_text" || b.type === "output_text") && text(b.text))
      .map((b) => text(b.text))
      .filter((t) => !/^\s*(<environment_context>|# AGENTS\.md instructions)/.test(t));
    if (!texts.length) return ["skip", []];
    return ["message", [{ role, text: texts.join("\n"), timestamp: text(o.timestamp) || null }]];
  },
};
