#!/usr/bin/env node
// Checked before anything else loads: node:sqlite and the MCP SDK need Node 24.
const major = Number(process.versions.node.split(".")[0]);
if (major < 24) {
  console.error(`acm needs Node 24 or newer; this is Node ${process.versions.node}.`);
  process.exit(1);
}
const { main } = await import("../dist/cli.js");
process.exitCode = await main();
