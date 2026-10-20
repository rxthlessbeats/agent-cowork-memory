# Agent Cowork Memory (ACM)

```
 █████╗  ██████╗███╗   ███╗
██╔══██╗██╔════╝████╗ ████║
███████║██║     ██╔████╔██║
██╔══██║██║     ██║╚██╔╝██║
██║  ██║╚██████╗██║ ╚═╝ ██║
╚═╝  ╚═╝ ╚═════╝╚═╝     ╚═╝
```

Hit your Codex limit mid-task? Open Cursor, say **"continue from Codex"**, and keep going. ACM gives Codex, Claude Code, Cursor, and OpenCode one shared memory, so you never paste context again, and any agent can put the others to work.

**Verified by [benchmark](#benchmark):** on 38 held-out tasks, a new chat continuing with ACM finished 223 of 228 runs, against 130 with a pasted summary.

![GitHub Release](https://img.shields.io/github/v/release/rxthlessbeats/agent-cowork-memory?style=flat&color=blue)
![npm](https://img.shields.io/npm/v/agent-cowork-memory?style=flat&color=blue)
![CI](https://img.shields.io/github/actions/workflow/status/rxthlessbeats/agent-cowork-memory/ci.yml?branch=main&style=flat&label=ci)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)
![M8ven Score](https://m8ven.ai/badge/mcp/rxthlessbeats-agent-cowork-memory-1jq2qu)
![Agents supported](https://img.shields.io/badge/agents_supported-4-orange?style=flat)
![Node](https://img.shields.io/badge/node-24%2B-green?style=flat)
[![Benchmark](https://img.shields.io/badge/benchmark-verified-brightgreen?style=flat)](#benchmark)
![MCP supported](https://img.shields.io/badge/MCP-supported-lightgrey?style=flat)
![CLI supported](https://img.shields.io/badge/CLI-supported-lightgrey?style=flat)
![Codex icon](https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/codex-color.svg) Codex  ·  ![Claude Code icon](https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/claudecode-color.svg) Claude Code  ·  ![Cursor icon](https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/cursor.svg) Cursor  ·  ![OpenCode icon](https://unpkg.com/@lobehub/icons-static-svg@1.90.0/icons/opencode.svg) OpenCode

## Demo

![Claude Code delegates to Codex, Cursor, and OpenCode through ACM](assets/demo.gif)

More demos on the [ACM official site](https://acm-website-sand.vercel.app/)

## Install

With [Node 24](https://nodejs.org) or newer:

```sh
npx agent-cowork-memory setup
```

Setup adds ACM to Cursor, and to Codex, Claude Code, and OpenCode when they are installed; Installed one later? Run setup again. Restart your agents, and ACM is available in every project.

Tested for real on Linux and WSL. macOS and Windows pass CI; real runs welcome.

## Use

### Memory Sharing

Open the same project in Codex and Cursor. To pick up a chat in the other agent, ask:

> Use ACM to continue from Cursor.

Or, in Cursor:

> Use ACM to continue from Codex.

Every agent can see every chat in the project. If there is more than one, the agent lists them (agent, time, thread, first message, and whether ACM started it for a delegated job) and asks you which one to continue. You can also name it:

> Use ACM to continue the Codex chat about the trip.

Related work goes together in a **thread**: continuing a chat, or delegating from it, keeps the work on one thread, and a new chat can join one of the project's open threads. ACM keeps each thread's timeline as things happen (chats joining, jobs starting and finishing, notes added), so any agent can see where the work stands.

Ask your agent to remember a decision, and every agent in the project sees it. Notes stay true.

### Delegate to other agents

Any agent can hand work to the others:

> Tell codex to write plan.md, and claude to write packing.md.

Each agent gets a brief, joins the thread it was sent from, claims the files it edits so they don't collide, and reports back. Agents run in the background. With [herdr](https://herdr.dev) installed, each one gets its own pane you can watch (`herdr session attach acm`).

## Benchmark

**What it evaluates**
- How much of earlier chats' context survives when a new chat continues the work.
- Each task is a small Python repo in two steps: earlier chats do step 1 and leave step 2's details in the chat.
- The details sit in one short or long chat, spread over two chats, changed later, corrected mid-chat, or against a README that still says the old thing.
- A run counts only if every hidden check passes, existing tests still pass, and no old or replaced value is implemented.

**What we tested**
- Codex (gpt-6-luna, medium effort) continuing the work five ways:
  - no ACM;
  - ACM (*"Use ACM to continue from my last Codex chat…"*);
  - the summary the earlier chat writes when asked;
  - a careful handoff note;
  - every earlier chat pasted in.
- 38 held-out tasks, written, and the analysis fixed, before any run.
- Two independent histories, 3 runs per way each.

| | No ACM | ACM | Summary pasted | Handoff note pasted | Full history pasted |
|---|---|---|---|---|---|
| Finished | 0/76 | **223/228** | 130/228 | 214/228 | 222/228 |
| Implemented an old value | 13/76 | **0/228** | 7/228 | 0/228 | 0/228 |
| What you type or paste | 80 chars | **95** | 753 | 2,740 | 1,940 |

**Result**
- ACM loses far less context than a pasted summary: it finished 41 points more often (p < 0.001). It was ahead on 29 of 38 tasks and behind on none.
- It matches pasting the whole history and a careful note pasted in full, from one sentence, with nothing to find or copy.
- On the 60 development tasks the same holds: ACM finished 176/180 runs, the summary 124/180.
- Limits: the tasks are built so the details live in earlier chats; one agent, one model.

```sh
npm run bench        # offline checks, free
npm run bench:live   # the live benchmark; spends your Codex quota
```

## MCP tools

| Tool              | What it does                                                                                                                                                                                                                                                                                               |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `context`       | Your thread and its timeline, the project's notes (after the first call, only what's new), open threads, recent jobs, who is working, and held files. Pass `hold` to claim files before writing, `thread` to join one, `done` to close yours. `stale` lists notes whose files changed, to re-check. |
| `note_add`      | Saves a note every agent sees, and shows notes it may contradict. `tier`: `short` (default, kept 7 days) or `long`; `supersedes`: the note it replaces.                                                                                                                                             |
| `note_search`   | Finds notes and delegated jobs' results.                                                                                                                                                                                                                                                                   |
| `chats`         | Lists recent chats from every agent in the project, and marks the ones ACM started.                                                                                                                                                                                                                        |
| `resume`        | Asks you which chat to continue when there are several, then reads it, with what you said in its thread's other chats, and joins its thread.                                                                                                                                                               |
| `delegate`      | Starts other agents with a brief, in herdr panes or in the background, and waits for them.                                                                                                                                                                                                                 |
| `delegate_wait` | Keeps waiting on this chat's delegated agents.                                                                                                                                                                                                                                                             |

ACM tells which chat it is in on its own; no tool needs a session or, from the project folder, a path (every tool takes an optional `repo_path`).

## CLI

| Command                                                         | What it does                                                                 |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `acm setup`                                                   | Adds ACM to your agents.                                                     |
| `acm mcp --harness <agent>`                                   | Runs the MCP server; agents start it themselves.                             |
| `acm status [--repo <dir>] [--chat <id>] [--harness <agent>]` | The project's jobs, held files, and a chat's thread, as JSON.                |
| `acm doctor`                                                  | Checks the install: Node, the database, herdr, and which agents are on PATH. |
| `acm backup [--to <file>]`                                    | Copies the database.                                                         |

`--home <dir>` (or `ACM_HOME`) moves ACM's state folder from `~/.agent-cowork-memory`. Run them with `npx -y agent-cowork-memory <command>`, or `acm` once it's installed globally.
