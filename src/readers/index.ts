/**
 * One module per agent, each with the same functions:
 *
 * root()                 default transcript folder
 * chats(base, repo)      every chat of a repo: its file, its workspace, its mtime
 * find(base, native)     the chat file for the agent's own chat id, or null
 * nativeId(path)         the agent's own id for a chat file
 * visible(obj)           ["message" | "skip" | "unknown", messages]
 * turnEnded(obj)         true for the record that closes an agent turn
 *
 * Readers whose chats are not one jsonl file also have read(path) -> jsonl bytes and exists(path).
 */
import { closeSync, existsSync, openSync, readdirSync, readSync, statSync } from "node:fs";
import { dirname, join, sep } from "node:path";

export type Json = Record<string, unknown>;
export type Chat = { path: string; workspace: string; mtime: number };
export type Message = { role: string; text: string; timestamp?: string | null };
export type Visible = ["message" | "skip" | "unknown", Message[]];

export interface Reader {
  root(): string;
  chats(base: string, repoRoot: string): Chat[];
  find(base: string, native: string): string | null;
  nativeId(path: string): string;
  visible(obj: Json): Visible;
  turnEnded(obj: Json): boolean;
  read?(path: string): Buffer;
  exists?(path: string): boolean;
}

export function obj(value: unknown): Json {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Json) : {};
}

export function text(value: unknown): string {
  return typeof value === "string" ? value : "";
}

// macOS and Windows file systems ignore case by default, so the same folder can be spelled two ways.
const foldCase = process.platform === "darwin" || process.platform === "win32";

function key(path: string): string {
  const trimmed = path.length > 1 ? path.replace(/[\\/]+$/, "") : path;
  return foldCase ? trimmed.toLowerCase() : trimmed;
}

export function samePath(a: string, b: string): boolean {
  return key(a) === key(b);
}

/** True when inner is outer or inside it. */
export function within(inner: string, outer: string): boolean {
  const i = key(inner);
  const o = key(outer);
  return i === o || i.startsWith(/[\\/]$/.test(o) ? o : o + sep);
}

/** The folder and every folder above it. */
export function upward(path: string): string[] {
  const out = [path];
  for (let p = dirname(path); p !== out[out.length - 1]; p = dirname(p)) out.push(p);
  return out;
}

/** A workspace that is the repo, inside it, or above it. */
export function related(workspace: string, repoRoot: string): boolean {
  return within(workspace, repoRoot) || within(repoRoot, workspace);
}

/** Cursor's folder name for a workspace: the path without its leading separator, separators as -. */
export function slug(path: string): string {
  return path.replace(/^[\\/]+|[\\/]+$/g, "").replace(/[\\/]/g, "-");
}

/** Claude Code's folder name for a workspace: every character but a letter or digit becomes -. */
export function dashes(path: string): string {
  return path.replace(/[^A-Za-z0-9]/g, "-");
}

export function mtime(path: string): number {
  return statSync(path).mtimeMs / 1000;
}

export function isFile(path: string): boolean {
  try {
    return statSync(path).isFile();
  } catch {
    return false;
  }
}

/** Files directly in a folder (or none if it is missing), filtered by name. */
export function files(folder: string, keep: (name: string) => boolean): string[] {
  if (!existsSync(folder)) return [];
  return readdirSync(folder)
    .filter(keep)
    .map((name) => join(folder, name))
    .filter(isFile);
}

/** Chats stored per workspace folder, for the repo and each folder above it. */
export function inWorkspaces(
  base: string,
  repoRoot: string,
  folder: (workspace: string) => string[],
  list: (dir: string) => string[],
): Chat[] {
  const found = new Map<string, Chat>();
  for (const workspace of upward(repoRoot)) {
    for (const name of folder(workspace)) {
      for (const path of list(join(base, name))) {
        if (!found.has(path)) found.set(path, { path, workspace, mtime: mtime(path) });
      }
    }
  }
  return [...found.values()];
}

/** The first `count` JSON objects of a jsonl file, reading only as far as needed. */
export function firstObjects(path: string, count = 20): Json[] {
  const out: Json[] = [];
  const fd = openSync(path, "r");
  try {
    const chunk = Buffer.alloc(65_536);
    let pending = Buffer.alloc(0);
    let lines = 0;
    while (lines < count) {
      const read = readSync(fd, chunk, 0, chunk.length, null);
      if (read === 0) break;
      pending = Buffer.concat([pending, chunk.subarray(0, read)]);
      let newline = pending.indexOf(10);
      while (newline >= 0 && lines < count) {
        lines += 1;
        try {
          out.push(obj(JSON.parse(pending.subarray(0, newline).toString("utf8"))));
        } catch {
          // not JSON: skip the line
        }
        pending = pending.subarray(newline + 1);
        newline = pending.indexOf(10);
      }
    }
  } finally {
    closeSync(fd);
  }
  return out;
}

/** The text blocks of a message's content, which is a string or a list of blocks. */
export function textBlocks(content: unknown, kinds: string[] = ["text"]): string[] | null {
  if (typeof content === "string") return [content];
  if (!Array.isArray(content)) return null;
  return content.map(obj).flatMap((b) => (kinds.includes(text(b.type)) && text(b.text) ? [text(b.text)] : []));
}
