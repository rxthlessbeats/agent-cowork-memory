import assert from "node:assert/strict";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { DatabaseSync } from "node:sqlite";
import { test } from "node:test";
import { backup, doctor, VERSION } from "../src/cli.ts";

test("doctor reports the install; backup copies a readable database", () => {
  const home = mkdtempSync(join(tmpdir(), "acm-"));
  try {
    const report = doctor(home);
    assert.equal(report.version, VERSION);
    assert.equal(report.writable, true);
    assert.equal(report.fts5, true);
    const { backup: file } = backup(home);
    assert.ok(existsSync(file));
    const copy = new DatabaseSync(file);
    assert.equal((copy.prepare("PRAGMA user_version").get() as { user_version: number }).user_version, 1);
    copy.close();
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
});

test("a home with 0.2's database keeps it untouched and starts a fresh one", async () => {
  const { connect } = await import("../src/db.ts");
  const home = mkdtempSync(join(tmpdir(), "acm-"));
  try {
    const old = new DatabaseSync(join(home, "state.sqlite3"));
    old.exec("CREATE TABLE tasks (id TEXT); PRAGMA user_version = 6;");
    old.close();
    const db = connect(home);
    assert.ok(db.prepare("SELECT name FROM sqlite_master WHERE name = 'threads'").get());
    db.close();
    const again = new DatabaseSync(join(home, "state.sqlite3"));
    assert.equal((again.prepare("PRAGMA user_version").get() as { user_version: number }).user_version, 6);
    again.close();
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
});
