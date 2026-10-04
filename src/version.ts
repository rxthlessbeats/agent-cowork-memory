import { readFileSync } from "node:fs";
import { join } from "node:path";

// src/ in development and dist/ when published both sit one level under the package root.
export const VERSION: string = JSON.parse(
  readFileSync(join(import.meta.dirname, "..", "package.json"), "utf8"),
).version;
