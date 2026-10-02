# Agent Cowork Memory (ACM)

<!-- mcp-name: io.github.rxthlessbeats/agent-cowork-memory -->

Tired of copying a chat into the next agent? Pick up the same task where you left off, or tell one agent to put the others to work.

[![GitHub Release](https://img.shields.io/github/v/release/rxthlessbeats/agent-cowork-memory?style=flat&color=blue)](https://github.com/rxthlessbeats/agent-cowork-memory/releases/latest)
[![PyPI](https://img.shields.io/pypi/v/agent-cowork-memory?style=flat&color=blue)](https://pypi.org/project/agent-cowork-memory/)
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

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uvx agent-cowork-memory setup
```

or

```sh
pip install agent-cowork-memory
acm setup
```

Restart Codex, Cursor, and OpenCode. ACM is now available in every project.
For Claude Code, add it yourself, then restart Claude Code:

```sh
claude mcp add -s user acm -- uvx agent-cowork-memory mcp --harness claude
```

Installed with pip, use `-- acm mcp --harness claude` instead.

## Use

### Memory Sharing

Open the same project in Codex and Cursor. To pick up a chat in the other agent, ask:

> Use ACM to continue from Cursor.

Or, in Cursor:

> Use ACM to continue from Codex.

Every agent can see every chat in the project. If there is more than one, the agent lists them (agent, time, task, first message, and whether ACM started it for a delegated job) and asks you which one to continue. You can also name it:

> Use ACM to continue the Codex chat about the trip.

For ongoing work, ask your agent to use ACM to track the task or remember a decision. You can ask it to search those notes later.

### Delegate to other agents

Any agent can hand work to the others:

> Tell codex to write plan.md, and claude to write packing.md.

Each agent gets a brief, claims the files it edits so they don't collide, and reports back. Agents run in the background. With [herdr](https://herdr.dev) installed, each one gets its own pane you can watch (`herdr session attach acm`).

Delegated agents run in each agent's auto mode: Codex `--approve-for-me`, Claude Code `--permission-mode auto`, and Cursor `--auto-review`. Safe actions run on their own. When auto mode denies an action, the agent stops, and ACM reports the job as `needs_approval` to the chat that delegated it, saying what the agent needs. A background job still running after 15 minutes is stopped and reported the same way. Approve it there, and that agent runs the step or delegates again. If an agent asks a question in its herdr pane instead, ACM reports the job as `blocked` until you answer it there. OpenCode has no auto-review mode, so it runs with `--auto`, which approves anything not explicitly denied.

There is one agent per kind per folder. A task for a busy agent comes back as `busy`.

## MCP tools

| Tool              | What it does                                                                                                          |
| ----------------- | --------------------------------------------------------------------------------------------------------------------- |
| `chats`         | Lists recent chats from every agent in the project, and marks the ones ACM started.                                  |
| `resume`        | Asks you which chat to continue when there are several, then reads it and picks up the task.                          |
| `attach`        | Starts or joins a shared task.                                                                                        |
| `context`       | Reads your task, project notes, who is working, and which files are held. Pass`hold` to claim files before writing. |
| `note_add`      | Saves a short-term or long-term note.                                                                                 |
| `note_search`   | Finds notes from the project.                                                                                         |
| `delegate`      | Starts other agents with a brief, in herdr panes or in the background, and waits for them.                            |
| `delegate_wait` | Keeps waiting on this chat's delegated agents.                                                                        |
