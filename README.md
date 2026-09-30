# Agent Cowork Memory (ACM)

Tired of copying a chat into the next agent? Pick up the same task where you left off, or tell one agent to put the others to work.

[![GitHub Release](https://img.shields.io/github/v/release/rxthlessbeats/agent-cowork-memory?style=flat&color=blue)](https://github.com/rxthlessbeats/agent-cowork-memory/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)
![Agents supported](https://img.shields.io/badge/agents_supported-4-orange?style=flat)
![Python](https://img.shields.io/badge/python-3.11%2B-green?style=flat)
![MCP supported](https://img.shields.io/badge/MCP-supported-lightgrey?style=flat)
![CLI supported](https://img.shields.io/badge/CLI-supported-lightgrey?style=flat)

<p>
  <img src="https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/codex-color.svg" alt="Codex icon" height="20"> Codex  · 
  <img src="https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/claudecode-color.svg" alt="Claude Code icon" height="20"> Claude Code  · 
  <img src="https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/cursor.svg" alt="Cursor icon" height="20"> Cursor &nbsp;·&nbsp;
  <img src="https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/opencode.svg" alt="OpenCode icon" height="20"> OpenCode
</p>

## Install

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
uvx --from "git+https://github.com/rxthlessbeats/agent-cowork-memory.git" acm setup
```

Restart Codex, Cursor, and OpenCode. ACM is now available in every project.
For Claude Code, add it yourself, then restart Claude Code:

```sh
claude mcp add -s user acm -- uvx --from "git+https://github.com/rxthlessbeats/agent-cowork-memory.git" acm mcp --harness claude
```

## Use

### Memory Sharing

Open the same project in Codex and Cursor. To pick up a chat in the other agent, ask:

> Use ACM to continue from Cursor.

Or, in Cursor:

> Use ACM to continue from Codex.

For ongoing work, ask your agent to use ACM to track the task or remember a decision. You can ask it to search those notes later.

### Delegate to other agents

Any agent can hand work to the others:

> Tell codex to write plan.md, and claude to write packing.md.

Each agent gets a brief, claims the files it edits so they don't collide, and reports back. Agents run in the background. With [herdr](https://herdr.dev) installed, each one gets its own pane you can watch (`herdr session attach acm`).

Delegated agents run without sandbox or approval prompts, one per kind per folder. A task for a busy agent comes back as `busy`.

## MCP tools

| Tool              | What it does                                                                                                          |
| ----------------- | --------------------------------------------------------------------------------------------------------------------- |
| `resume`        | Reads the other agent's recent chat and picks up the task.                                                            |
| `attach`        | Starts or joins a shared task.                                                                                        |
| `context`       | Reads your task, project notes, who is working, and which files are held. Pass`hold` to claim files before writing. |
| `note_add`      | Saves a short-term or long-term note.                                                                                 |
| `note_search`   | Finds notes from the project.                                                                                         |
| `delegate`      | Starts other agents with a brief, in herdr panes or in the background, and waits for them.                            |
| `delegate_wait` | Keeps waiting on this chat's delegated agents.                                                                        |
