import assert from "node:assert/strict";
import { test } from "node:test";
import { bootstrap, classify, fromCursor, fromOpenCode, holm, lowerBound, signFlip, survival } from "../bench/live.ts";

test("sign-flip p: 8 tasks all one way is 2/256, ties drop out, nothing is 1", () => {
  assert.equal(signFlip([1, 1, 1, 1, 1, 1, 1, 1]), 2 / 256);
  assert.equal(signFlip([1, 0.5, 1, 1, 1, 0, 1, 1, 0]), 2 / 128);
  assert.equal(signFlip([1, -1]), 1);
  assert.equal(signFlip([0, 0]), 1);
  // 40 tasks, one way: 2 of 2^40 sign patterns are as extreme, counted without listing them.
  assert.equal(signFlip(new Array(40).fill(1)), 2 / 2 ** 40);
  // Flipping every sign changes nothing; the grid counts thirds exactly (8 of the 2^5 patterns reach |sum| 13/6).
  assert.equal(signFlip([1 / 3, -2 / 3, 1, 1, 0.5]), signFlip([-1 / 3, 2 / 3, -1, -1, -0.5]));
  assert.equal(signFlip([1 / 3, -2 / 3, 1, 1, 0.5]), 8 / 32);
});

test("the bootstrap lower bound is the mean when every task agrees, and below it when they differ", () => {
  assert.equal(lowerBound([0.5, 0.5, 0.5]), 0.5);
  const bound = lowerBound([1, 0, 0, 1, 1, 0, 1, 1]);
  assert.ok(bound > 0.2 && bound < 0.625, String(bound));
  assert.equal(lowerBound([1, 0, 0, 1, 1, 0, 1, 1]), bound); // seeded: the same every run
  assert.ok(bootstrap([1, 0, 0, 1, 1, 0, 1, 1], 0.975) > 0.625); // and the interval's top sits above the mean
});

test("Holm multiplies the smallest p by the number of tests and keeps the order", () => {
  assert.deepEqual(
    holm([0.01, 0.04, 0.03]).map((p) => +p.toFixed(4)),
    [0.03, 0.06, 0.06],
  );
});

test("steps split into atoms and kinds the way the plan's rules say", () => {
  const ran = (command: string) => ({ type: "item.completed", item: { type: "command_execution", command } });
  const log = [
    { type: "user.message", text: "Continue" },
    // Chained reads, a pipeline as one atom, and a look for the earlier chat on disk.
    ran(`/usr/bin/bash -lc "ls -la; git diff && cat TASK.md | head -40; rg --files -g 'AGENTS.md' /tmp"`),
    // A heredoc's body is data: one python run, whatever it holds; the env prefix comes off.
    ran("/usr/bin/bash -lc \"PYTHONDONTWRITEBYTECODE=1 python - <<'PY'\nimport x; ls\nPY\""),
    // Writing a file with cat is an edit; a quoted ; doesn't split; echo is noise.
    ran(`/usr/bin/bash -lc 'cat > notes.md <<'"'"'EOF'"'"'\nhi\nEOF\necho ---; grep -n "a;b" x.py'`),
    { type: "item.completed", item: { type: "file_change", changes: [] } },
    { type: "item.completed", item: { type: "mcp_tool_call", server: "acm", tool: "resume" } },
    { type: "item.completed", item: { type: "agent_message", text: "Done." } },
  ];
  assert.deepEqual(classify(log), { explore: 4, verify: 1, edit: 2, orientation: 1, other: 0, memory: 1 });
});

test("a planted detail is kept, stale, both, or dropped by its patterns", () => {
  const planted = {
    chat_cap: { value: ["20(\\.00)? cap", "cap(ped)? at 20"] },
    changed_sort: { value: ["by price"], stale: ["by (stock|units)"] },
    chat_gift: { value: ["gift cards?"] },
  };
  assert.deepEqual(survival("Discounts are capped at 20. Sort by stock.", planted), {
    chat_cap: "kept",
    changed_sort: "stale",
    chat_gift: "dropped",
  });
  assert.equal(survival("Sort by price (it was by stock).", planted).changed_sort, "both");
});

test("Cursor's stream-json reads as Codex's events: thread, one message per part run, tools as steps, usage", () => {
  const acm = { content: [{ text: { text: '{"messages":[1]}' } }] };
  const events = fromCursor([
    { type: "system", subtype: "init", session_id: "c1", model: "Grok" },
    { type: "assistant", message: { content: [{ type: "text", text: "Look" }] } },
    { type: "assistant", message: { content: [{ type: "text", text: "ing." }] } },
    { type: "tool_call", subtype: "started", tool_call: { readToolCall: { args: { path: "a.py" } } } },
    { type: "tool_call", subtype: "completed", tool_call: { readToolCall: { args: { path: "a.py" } } } },
    { type: "tool_call", subtype: "completed", tool_call: { editToolCall: { args: { path: "a.py" } } } },
    {
      type: "tool_call",
      subtype: "completed",
      tool_call: { mcpToolCall: { args: { providerIdentifier: "acm", toolName: "resume" }, result: { success: acm } } },
    },
    { type: "assistant", message: { content: [{ type: "text", text: "Done?" }] } },
    {
      type: "result",
      is_error: false,
      usage: { inputTokens: 10, outputTokens: 5, cacheReadTokens: 80, cacheWriteTokens: 10 },
    },
  ]);
  assert.deepEqual(events[0], { type: "thread.started", thread_id: "c1", model: "Grok" });
  const items = events.filter((e) => e.type === "item.completed").map((e) => e.item as Record<string, unknown>);
  assert.deepEqual(
    items.map((i) => i.type),
    ["agent_message", "command_execution", "file_change", "mcp_tool_call", "agent_message"],
  );
  assert.equal(items[0].text, "Looking.");
  assert.equal(items[1].command, "cat a.py");
  assert.equal((items[3].result as { content: { text: string }[] }).content[0].text, '{"messages":[1]}');
  assert.equal(items[4].text, "Done?");
  assert.deepEqual(events.at(-1), {
    type: "turn.completed",
    usage: { input_tokens: 100, cached_input_tokens: 80, output_tokens: 5 },
  });
  assert.deepEqual(classify(events), { explore: 1, verify: 0, edit: 1, orientation: 0, other: 0, memory: 1 });
  assert.equal(fromCursor([{ type: "result", is_error: true, result: "boom" }])[0].type, "turn.failed");
});

test("OpenCode's JSON events read as Codex's: thread, messages, tools as steps, ACM's tools as MCP, summed usage", () => {
  const tool = (name: string, input: object, output = "") => ({
    type: "tool_use",
    sessionID: "s1",
    part: { type: "tool", tool: name, state: { status: "completed", input, output } },
  });
  const step = (input: number, output: number, read: number) => ({
    type: "step_finish",
    sessionID: "s1",
    part: { tokens: { input, output, reasoning: 1, cache: { read, write: 0 } } },
  });
  const events = fromOpenCode([
    { type: "step_start", sessionID: "s1", part: {} },
    { type: "text", sessionID: "s1", part: { type: "text", text: "Reading." } },
    tool("read", { filePath: "a.py" }),
    tool("acm_resume", { source: "opencode" }, '{"messages":[1]}'),
    tool("execute", { code: "await tools.acm.context({}); return await tools.acm.resume({});" }, '{"choose":[]}'),
    tool("shell", { command: "ls" }),
    tool("edit", { filePath: "a.py" }),
    step(10, 2, 90),
    { type: "text", sessionID: "s1", part: { type: "text", text: "Done?" } },
    step(5, 3, 95),
  ]);
  assert.deepEqual(events[0], { type: "thread.started", thread_id: "s1" });
  const items = events.filter((e) => e.type === "item.completed").map((e) => e.item as Record<string, unknown>);
  assert.deepEqual(
    items.map((i) => i.type),
    [
      "agent_message",
      "command_execution",
      "mcp_tool_call",
      "mcp_tool_call",
      "mcp_tool_call",
      "command_execution",
      "file_change",
      "agent_message",
    ],
  );
  assert.equal(items[1].command, "cat a.py");
  assert.deepEqual([items[2].server, items[2].tool], ["acm", "resume"]);
  // OpenCode 2 runs MCP tools from code: one item per ACM tool the code called.
  assert.deepEqual([items[3].tool, items[4].tool], ["context", "resume"]);
  assert.equal(items[5].command, "ls");
  assert.equal(items[7].text, "Done?");
  assert.deepEqual(events.at(-1), {
    type: "turn.completed",
    usage: { input_tokens: 200, cached_input_tokens: 185, output_tokens: 7 },
  });
  assert.equal(fromOpenCode([{ type: "error", sessionID: "s1", error: { name: "X" } }]).at(-1)?.type, "error");
});
