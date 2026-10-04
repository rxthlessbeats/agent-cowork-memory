import { readdirSync } from "node:fs";
import { homedir } from "node:os";
import { basename, join } from "node:path";
import {
  dashes,
  files,
  firstObjects,
  inWorkspaces,
  isFile,
  type Json,
  obj,
  type Reader,
  text,
  textBlocks,
} from "./index.ts";

const SKIP = new Set(["queue-operation", "attachment", "atis-latch", "last-prompt", "cost-state", "system", "summary"]);

export const claude: Reader = {
  root: () => join(process.env.CLAUDE_CONFIG_DIR || join(homedir(), ".claude"), "projects"),

  chats: (base, repoRoot) =>
    inWorkspaces(
      base,
      repoRoot,
      (ws) => [dashes(ws)],
      (dir) => files(dir, (n) => n.endsWith(".jsonl")),
    ),

  find(base, native) {
    try {
      for (const folder of readdirSync(base)) {
        const path = join(base, folder, `${native}.jsonl`);
        if (isFile(path)) return path;
      }
    } catch {
      // no transcripts yet
    }
    return null;
  },

  nativeId: (path) => text(firstObjects(path).find((o) => o.sessionId)?.sessionId) || basename(path, ".jsonl"),

  turnEnded: (o: Json) => o.type === "system" && o.subtype === "turn_duration",

  visible(o) {
    const kind = text(o.type);
    if (SKIP.has(kind)) return ["skip", []];
    if (kind !== "user" && kind !== "assistant") return ["unknown", []];
    const texts = textBlocks(obj(o.message).content);
    if (texts === null) return ["unknown", []];
    if (!texts.length) return ["skip", []];
    return ["message", [{ role: kind, text: texts.join("\n"), timestamp: text(o.timestamp) || null }]];
  },
};
