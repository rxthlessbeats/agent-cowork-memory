import { readdirSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";
import { dashes, files, inWorkspaces, isFile, obj, type Reader, slug, text } from "./index.ts";

/** Cursor's folders for a workspace. Paths of letters, digits and / are known to map to slug(); for
 * other characters it is unconfirmed, so the all-dashes form is tried too. Windows: not confirmed. */
function folders(workspace: string): string[] {
  return [...new Set([slug(workspace), dashes(workspace).replace(/^-+|-+$/g, "")])].map((n) =>
    join(n, "agent-transcripts"),
  );
}

function chatFiles(dir: string): string[] {
  try {
    return readdirSync(dir).flatMap((id) => files(join(dir, id), (n) => n.endsWith(".jsonl")));
  } catch {
    return [];
  }
}

export const cursor: Reader = {
  root: () => process.env.CURSOR_TRANSCRIPTS || join(homedir(), ".cursor", "projects"),

  chats: (base, repoRoot) => inWorkspaces(base, repoRoot, folders, chatFiles),

  find(base, native) {
    try {
      for (const folder of readdirSync(base)) {
        const path = join(base, folder, "agent-transcripts", native, `${native}.jsonl`);
        if (isFile(path)) return path;
      }
    } catch {
      // no transcripts yet
    }
    return null;
  },

  nativeId: (path) => basename(dirname(path)),

  turnEnded: (o) => o.type === "turn_ended",

  visible(o) {
    if (o.type === "turn_ended" || !("role" in o)) return ["skip", []];
    const role = text(o.role);
    if (role !== "user" && role !== "assistant") return ["skip", []];
    const content = obj(o.message).content;
    if (typeof content === "string") return ["message", [{ role, text: content, timestamp: null }]];
    if (!Array.isArray(content)) return ["unknown", []];
    const texts: string[] = [];
    for (const block of content.map(obj)) {
      if (block.type === "tool_use") continue;
      if (block.type !== "text") return ["unknown", []];
      if (text(block.text)) texts.push(text(block.text));
    }
    if (!texts.length) return ["skip", []];
    return ["message", [{ role, text: texts.join("\n"), timestamp: null }]];
  },
};
