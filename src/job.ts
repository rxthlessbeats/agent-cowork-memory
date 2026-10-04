/**
 * The background job wrapper. acm starts it detached as `node job.js <base> <program> [args...]`; it outlives
 * the MCP server that started it. It feeds <base>.prompt to the agent on stdin, sends output to <base>.out and
 * <base>.log, and writes the exit code to <base>.exit once the agent is done.
 */
import { spawn } from "node:child_process";
import { closeSync, openSync, renameSync, writeFileSync } from "node:fs";
import { isMain, winCommand } from "./util.ts";

/** On Windows the agent is started through cmd.exe. Its arguments are flags and paths (the brief goes on
 * stdin), so quoting each one is enough. */
export function command(program: string, args: string[]): [string, string[], { shell: boolean }] {
  if (process.platform !== "win32") return [program, args, { shell: false }];
  return [winCommand(program, args), [], { shell: true }];
}

function main(): void {
  const [base, program, ...args] = process.argv.slice(2);
  const stdin = openSync(`${base}.prompt`, "r");
  const out = openSync(`${base}.out`, "w");
  const log = openSync(`${base}.log`, "w");
  const [cmd, argv, opts] = command(program, args);
  const child = spawn(cmd, argv, { ...opts, stdio: [stdin, out, log], windowsHide: true });
  const finish = (code: number) => {
    for (const fd of [stdin, out, log]) closeSync(fd);
    writeFileSync(`${base}.exit.tmp`, `${code}\n`);
    renameSync(`${base}.exit.tmp`, `${base}.exit`);
  };
  child.on("error", (err) => {
    writeFileSync(`${base}.log`, `could not start ${program}: ${err.message}\n`, { flag: "a" });
    finish(127);
  });
  child.on("exit", (code, signal) => finish(code ?? (signal ? 128 : 1)));
}

if (isMain(import.meta.url)) main();
