import { execFileSync } from "node:child_process";
import { existsSync, realpathSync } from "node:fs";
import { basename, dirname, parse } from "node:path";
import { AcmError } from "./util.ts";

const roots = new Map<string, string>();

/** The real path, in the case the file system uses, so one folder always gives one string. */
export function canonical(path: string): string {
  if (!existsSync(path)) throw new AcmError("invalid", `${path} does not exist`);
  return realpathSync.native(path);
}

/**
 * The project a folder belongs to: its repo's top-level folder, with every worktree mapped to the
 * main repo's folder. Without git, the folder itself, so a folder is the same project with or without git.
 */
export function projectRoot(folder: string): string {
  const real = canonical(folder);
  const cached = roots.get(real);
  if (cached) return cached;
  let root = real;
  try {
    const common = execFileSync("git", ["-C", real, "rev-parse", "--path-format=absolute", "--git-common-dir"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    if (basename(common) === ".git") root = canonical(dirname(common));
  } catch {
    // Not a git repo, or no git: the folder is the project.
  }
  roots.set(real, root);
  return root;
}

/** True for the home folder or a drive root, where acm refuses to delegate. */
export function isHomeOrRoot(folder: string, home: string): boolean {
  return folder === canonical(home) || folder === parse(folder).root;
}
