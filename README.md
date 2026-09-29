# Agent Cowork Memory (ACM)

Share task context and chats across coding agents.

[![GitHub Release](https://img.shields.io/github/v/release/rxthlessbeats/agent-cowork-memory?style=flat&color=blue)](https://github.com/rxthlessbeats/agent-cowork-memory/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)
![Agents supported](https://img.shields.io/badge/agents_supported-3-orange?style=flat)
![Python](https://img.shields.io/badge/python-3.11%2B-green?style=flat)
![MCP supported](https://img.shields.io/badge/MCP-supported-lightgrey?style=flat)
![CLI supported](https://img.shields.io/badge/CLI-supported-lightgrey?style=flat)

<p>
  <img src="https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/codex-color.svg" alt="Codex icon" height="20"> Codex &nbsp;·&nbsp;
  <img src="https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/claudecode-color.svg" alt="Claude Code icon" height="20"> Claude Code &nbsp;·&nbsp;
  <img src="https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/cursor.svg" alt="Cursor icon" height="20"> Cursor
</p>

## Install

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
uvx --from "git+https://github.com/rxthlessbeats/agent-cowork-memory.git" acm setup
```

Restart Codex and Cursor. ACM is now available in every project.
Claude Code requires manual MCP setup.

## Use

Open the same project in Codex and Cursor. To pick up a chat in the other agent, ask:

> Use ACM to continue from Cursor.

Or, in Cursor:

> Use ACM to continue from Codex.

For ongoing work, ask your agent to use ACM to track the task or remember a decision. You can ask it to search those notes later.

## MCP tools

| Tool | What it does |
| --- | --- |
| `resume` | Reads the other agent's recent chat and picks up the task. |
| `attach` | Starts or joins a shared task. |
| `context` | Reads the current task state and saved notes. |
| `note_add` | Saves a short-term or long-term note. |
| `note_search` | Finds notes from the project. |
