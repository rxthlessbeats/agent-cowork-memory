import json
from collections import Counter
import os
import signal
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from agent_cowork_memory.db import connect
from agent_cowork_memory.delegate import (
    Deps, HerdrError, _clean_jobs, _headless, build_prompt, card, delegate, delegate_wait, spawn_background,
)
from agent_cowork_memory.ledger import AcmError, context


class FakeHerdr:
    def __init__(self, roots, running=True):
        self.roots = roots
        self.running = running
        self.agents = {}
        self.panes = []
        self.prompts = []
        self.block_start = set()
        self.stuck_start = set()
        self.timeouts = {}
        self.finish = True
        self.drop = 0
        self.started = 0
        self.t = 0.0

    def clock(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds

    def start_server(self):
        self.started += 1
        self.running = True

    def deps(self, delegated=False):
        return Deps(herdr=self, start_server=self.start_server, use_herdr=lambda: True, delegated=lambda: delegated,
                    sleep=self.sleep, clock=self.clock, roots=self.roots)

    def __call__(self, *args, raw=False):
        if not self.running:
            raise HerdrError("server_not_running", "no server")
        cmd = args[:2]
        if cmd == ("workspace", "list"):
            return {"workspaces": []}
        if cmd == ("pane", "list"):
            return {"panes": list(self.panes)}
        if cmd == ("workspace", "create"):
            pane = {"pane_id": "w1:p1", "workspace_id": "w1", "tab_id": "w1:t1", "cwd": args[args.index("--cwd") + 1]}
            self.panes.append(pane)
            return {"workspace": {"workspace_id": "w1"}, "root_pane": pane}
        if cmd in (("pane", "split"), ("tab", "create")):
            assert "ACM_DELEGATED=1" in args
            tabs = {p["tab_id"] for p in self.panes}
            tab = next(p["tab_id"] for p in self.panes if p["pane_id"] == args[2]) if cmd[0] == "pane" else f"w1:t{len(tabs) + 1}"
            pane = {"pane_id": f"w1:p{len(self.panes) + 1}", "workspace_id": "w1", "tab_id": tab, "cwd": args[args.index("--cwd") + 1]}
            self.panes.append(pane)
            return {"pane": pane} if cmd[0] == "pane" else {"tab": {"tab_id": tab}, "root_pane": pane}
        if cmd == ("agent", "list"):
            return {"agents": list(self.agents.values())}
        if cmd == ("agent", "start"):
            name, kind, pane = args[2], args[args.index("--kind") + 1], args[args.index("--pane") + 1]
            timeout = int(args[args.index("--timeout") + 1])
            assert 3000 < timeout <= 300000
            self.timeouts[kind] = timeout
            if kind in self.stuck_start:
                self.t += timeout / 1000  # it waited out its whole budget
                raise HerdrError("timeout", "timed out waiting for agent startup")
            self.agents[name] = {
                "name": name, "agent": kind, "pane_id": pane, "workspace_id": "w1",
                "agent_status": "blocked" if kind in self.block_start else "idle",
                "agent_session": {"value": f"{name}-session"},
            }
            if kind in self.block_start:
                raise HerdrError("agent_not_ready", "blocked during startup")
            return {"type": "agent_started"}
        if cmd == ("agent", "prompt"):
            name, text = args[2], args[3]
            self.prompts.append((name, text))
            if self.drop:
                self.drop -= 1
                return {"type": "agent_prompted"}
            self.agents[name]["agent_status"] = "working"
            if self.finish:
                self.complete(name, text)
            return {"type": "agent_prompted"}
        if cmd == ("pane", "read"):
            return "Do you want to proceed?\n❯ Yes\n  No\n"
        raise AssertionError(f"unexpected herdr call {args}")

    def complete(self, name, text, answer=None):
        agent = self.agents[name]
        kind, native = agent["agent"], agent["agent_session"]["value"]
        answer = answer or f"{name} finished the work"
        base = Path(self.roots[kind])
        if kind == "codex":
            path = base / "2026" / f"rollout-x-{native}.jsonl"
            lines = [
                {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]}},
                {"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": answer}]}},
                {"type": "event_msg", "payload": {"type": "task_complete", "last_agent_message": answer}},
            ]
        elif kind == "cursor":
            path = base / "proj" / "agent-transcripts" / native / f"{native}.jsonl"
            lines = [
                {"role": "user", "message": {"content": [{"type": "text", "text": text}]}},
                {"role": "assistant", "message": {"content": [{"type": "text", "text": answer}]}},
                {"type": "turn_ended", "status": "success"},
            ]
        else:
            path = base / "-proj" / f"{native}.jsonl"
            lines = [
                {"type": "user", "message": {"role": "user", "content": text}},
                {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": answer}]}},
                {"type": "system", "subtype": "turn_duration"},
            ]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as handle:
            for line in lines:
                handle.write(json.dumps(line) + "\n")
        agent["agent_status"] = "idle"


class DelegateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        self.folder = base / "work"
        self.folder.mkdir()
        roots = {k: base / "t" / k for k in ("codex", "cursor", "claude")}
        for root in roots.values():
            root.mkdir(parents=True)
        self.fake = FakeHerdr(roots)
        self.conn = connect(self.home)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def run_delegate(self, tasks, summary="Plan a Lisbon trip.", session=None, **kw):
        return delegate(self.conn, harness="cursor", repo_path=self.folder, summary=summary,
                        tasks=tasks, session=session, deps=self.fake.deps(**kw))

    def test_old_job_files_are_removed_but_running_ones_stay(self):
        first = self.run_delegate([{"to": "codex", "task": "Write plan.md"}])
        job = first["jobs"][0]["job"]
        jobs = self.home / "jobs"
        jobs.mkdir(exist_ok=True)
        old, running = jobs / "acm_j_000000000000.log", jobs / f"{job}.log"
        for path in (old, running):
            path.write_text("x")
            os.utime(path, (1_000, 1_000))
        self.conn.execute("UPDATE delegations SET state = 'running' WHERE id = ?", (job,))
        _clean_jobs(self.conn)
        self.assertFalse(old.exists())
        self.assertTrue(running.exists())

    def test_two_agents_in_parallel_with_briefs(self):
        got = self.run_delegate([
            {"to": "codex", "task": "Write plan.md", "done_when": "plan.md exists"},
            {"to": "claude", "task": "Write packing.md", "context": "Carry-on only."},
        ])
        self.assertEqual([(j["agent"], j["state"]) for j in got["jobs"]], [("codex-work", "done"), ("claude-work", "done")])
        self.assertEqual(got["jobs"][0]["result"], "codex-work finished the work")
        self.assertNotIn("next", got)
        prompts = dict(self.fake.prompts)
        self.assertIn("## Problem\nPlan a Lisbon trip.", prompts["codex-work"])
        self.assertIn("## Done when\nplan.md exists", prompts["codex-work"])
        self.assertIn("- claude-work: Write packing.md", prompts["codex-work"])
        self.assertIn("- codex-work: Write plan.md", prompts["claude-work"])
        self.assertIn("## Context\nCarry-on only.", prompts["claude-work"])
        self.assertIn("Don't delegate", prompts["claude-work"])

    def test_results_become_notes_and_each_new_caller_gets_its_own_task(self):
        first = self.run_delegate([{"to": "codex", "task": "Write plan.md"}])
        second = self.run_delegate([{"to": "claude", "task": "Write packing.md"}], summary="Pack for it.")
        notes = self.conn.execute(
            """SELECT m.body, m.kind, m.task_id, s.harness, s.label FROM memories m
               JOIN sessions s ON s.id = m.author_session_id ORDER BY m.created_at, m.rowid"""
        ).fetchall()
        self.assertEqual([(n["harness"], n["label"], n["kind"]) for n in notes],
                         [("codex", "codex-work", "result"), ("claude", "claude-work", "result")])
        self.assertIn("codex-work did: Write plan.md\nResult: codex-work finished the work", notes[0]["body"])
        tasks = [self.conn.execute(
            "SELECT t.id, t.title FROM sessions s JOIN tasks t ON t.id = s.active_task_id WHERE s.id = ?", (s,)).fetchone()
            for s in (first["session"], second["session"])]
        self.assertEqual([t["title"] for t in tasks], ["Plan a Lisbon trip.", "Pack for it."])
        self.assertEqual([n["task_id"] for n in notes], [t["id"] for t in tasks])
        self.assertNotIn("Save a short acm note", self.fake.prompts[0][1])

    def test_follow_up_reuses_agent_and_skips_unchanged_problem(self):
        first = self.run_delegate([{"to": "codex", "task": "Write plan.md"}])
        again = self.run_delegate([{"to": "codex", "task": "Add a budget section"}], session=first["session"])
        self.assertEqual(again["jobs"][0]["agent"], "codex-work")
        self.assertEqual(len(self.fake.agents), 1)
        self.assertNotIn("## Problem", self.fake.prompts[-1][1])
        self.assertEqual(len(again["jobs"]), 1)

    def test_new_caller_reuses_idle_agent(self):
        self.run_delegate([{"to": "codex", "task": "Write plan.md"}])
        other = self.run_delegate([{"to": "codex", "task": "Write budget.md"}], summary="Budget the trip.")
        self.assertEqual(other["jobs"][0]["agent"], "codex-work")
        self.assertEqual(len(self.fake.agents), 1)
        self.assertIn("## Problem\nBudget the trip.", self.fake.prompts[-1][1])

    def test_busy_agent_refuses_and_wait_continues(self):
        self.fake.finish = False
        first = self.run_delegate([{"to": "codex", "task": "Long job"}])
        self.assertEqual(first["jobs"][0]["state"], "running")
        self.assertIn("next", first)
        panes = len(self.fake.panes)
        other = self.run_delegate([{"to": "codex", "task": "Another job"}], summary="Something else.")
        self.assertEqual(len(self.fake.panes), panes)
        busy = other["jobs"][0]
        self.assertEqual((busy["agent"], busy["state"]), ("codex-work", "busy"))
        self.assertIn("still working on: Long job", busy["result"])
        self.assertEqual(card(other), "codex  busy")
        self.assertEqual(len(self.fake.prompts), 1)
        self.fake.complete(*self.fake.prompts[0])
        done = delegate_wait(self.conn, session=first["session"], deps=self.fake.deps())
        self.assertEqual([j["state"] for j in done["jobs"]], ["done"])
        self.assertNotIn("next", done)
        self.assertEqual(delegate_wait(self.conn, session=first["session"], deps=self.fake.deps())["jobs"], [])
        self.fake.running = False  # herdr down, nothing open: still answers
        self.assertEqual(delegate_wait(self.conn, session=first["session"], deps=self.fake.deps())["jobs"], [])

    def test_other_chat_sees_finished_agent_and_its_holds_are_released(self):
        self.fake.finish = False
        self.run_delegate([{"to": "codex", "task": "Long job"}])
        worker = self.conn.execute("SELECT id FROM sessions WHERE label = 'codex-work'").fetchone()["id"]
        context(self.conn, session=worker, hold=["plan.md"])
        self.fake.complete(*self.fake.prompts[0])
        self.fake.finish = True
        other = self.run_delegate([{"to": "codex", "task": "Next job"}], summary="Something else.")
        self.assertEqual([j["state"] for j in other["jobs"]], ["done"])
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM holds").fetchone()[0], 0)

    def test_one_pane_per_agent(self):
        self.run_delegate([{"to": "codex", "task": "A"}, {"to": "claude", "task": "B"}])
        self.assertEqual(sorted(a["pane_id"] for a in self.fake.agents.values()), ["w1:p1", "w1:p2"])
        self.assertEqual(len(self.fake.panes), 2)
        same = self.run_delegate([{"to": "codex", "task": "A"}, {"to": "codex", "task": "C"}], summary="Other.")
        self.assertEqual([j["state"] for j in same["jobs"]], ["busy", "done"])

    def test_dropped_brief_is_sent_once_more(self):
        self.fake.drop = 1
        with mock.patch("agent_cowork_memory.delegate.RESEND_AFTER", -1):
            got = self.run_delegate([{"to": "codex", "task": "Write plan.md"}])
            self.assertEqual(got["jobs"][0]["state"], "done")
            self.assertEqual(len(self.fake.prompts), 2)
            self.fake.drop = 2
            again = self.run_delegate([{"to": "codex", "task": "Add a budget"}], session=got["session"])
        self.assertEqual(again["jobs"][0]["state"], "running")
        self.assertEqual(len(self.fake.prompts), 4)

    def test_two_panes_per_tab(self):
        self.run_delegate([{"to": k, "task": "A"} for k in ("codex", "claude", "cursor")])
        tabs = [p["tab_id"] for p in self.fake.panes]
        self.assertEqual(tabs, ["w1:t1", "w1:t1", "w1:t2"])

    def test_blocked_is_reported_not_answered(self):
        self.fake.finish = False
        got = self.run_delegate([{"to": "codex", "task": "Risky"}])
        self.fake.agents["codex-work"]["agent_status"] = "blocked"
        got = delegate_wait(self.conn, session=got["session"], deps=self.fake.deps())
        self.assertEqual(got["jobs"][0]["state"], "blocked")
        self.assertIn("Do you want to proceed?", got["jobs"][0]["result"])
        self.assertIn("blocked", got)

    def test_opencode_gets_a_tab_to_itself(self):
        self.fake.roots["opencode"] = Path(self.tmp.name) / "t" / "opencode"
        self.fake.roots["opencode"].mkdir()
        self.fake.finish = False
        self.run_delegate([
            {"to": "opencode", "task": "A"}, {"to": "claude", "task": "B"}, {"to": "codex", "task": "C"},
            {"to": "cursor", "task": "D"},
        ])
        tabs = Counter(p["tab_id"] for p in self.fake.panes)
        opencode = self.fake.agents["opencode-work"]["pane_id"]
        self.assertEqual(tabs[next(p["tab_id"] for p in self.fake.panes if p["pane_id"] == opencode)], 1)
        self.assertEqual(sorted(tabs.values()), [1, 1, 2])

    def test_a_stalled_start_does_not_shrink_the_others_budget(self):
        self.fake.stuck_start.add("codex")
        got = self.run_delegate([
            {"to": "codex", "task": "Write plan.md"}, {"to": "claude", "task": "Write packing.md"},
            {"to": "cursor", "task": "Write budget.md"},
        ])
        self.assertEqual(self.fake.timeouts, {"codex": 45000, "claude": 45000, "cursor": 45000})
        states = {j["agent"]: j["state"] for j in got["jobs"]}
        self.assertEqual(states, {"codex-work": "gone", "claude-work": "done", "cursor-work": "done"})

    def test_startup_prompt_then_task_is_sent_later(self):
        self.fake.block_start.add("claude")
        got = self.run_delegate([{"to": "claude", "task": "Write packing.md"}])
        self.assertEqual(got["jobs"][0]["state"], "starting")
        self.assertEqual(self.fake.prompts, [])
        self.fake.agents["claude-work"]["agent_status"] = "idle"
        done = delegate_wait(self.conn, session=got["session"], deps=self.fake.deps())
        self.assertEqual(done["jobs"][0]["state"], "done")

    def test_agent_that_never_starts_is_gone_and_others_still_run(self):
        self.fake.stuck_start.add("codex")
        self.fake.t = 44.0
        got = self.run_delegate([{"to": "codex", "task": "Write plan.md"}, {"to": "claude", "task": "Write packing.md"}])
        states = {j["agent"]: j["state"] for j in got["jobs"]}
        self.assertEqual(states, {"codex-work": "gone", "claude-work": "done"})
        self.assertIn("could not start codex: timed out", next(j["result"] for j in got["jobs"] if j["agent"] == "codex-work"))

    def test_denied_action_in_a_pane_comes_back_as_needs_approval(self):
        self.fake.finish = False
        got = self.run_delegate([{"to": "claude", "task": "Delete ~/old.txt"}])
        name, prompt = self.fake.prompts[0]
        self.assertIn("## If an action is denied", prompt)
        self.fake.complete(name, prompt, "BLOCKED: auto mode denied deleting ~/old.txt")
        self.fake.agents[name]["agent_status"] = "idle"
        done = delegate_wait(self.conn, session=got["session"], deps=self.fake.deps())
        self.assertEqual(done["jobs"][0]["state"], "needs_approval")
        self.assertIn("needs_approval", done)

    def test_closed_pane_is_gone(self):
        self.fake.finish = False
        got = self.run_delegate([{"to": "cursor", "task": "X"}])
        del self.fake.agents["cursor-work"]
        gone = delegate_wait(self.conn, session=got["session"], deps=self.fake.deps())["jobs"][0]
        self.assertEqual(gone["state"], "gone")
        self.assertIn("Last lines", gone["result"])

    def test_starts_herdr_when_not_running(self):
        self.fake.running = False
        self.run_delegate([{"to": "codex", "task": "X"}])
        self.assertEqual(self.fake.started, 1)

    def test_delegated_agent_can_delegate_only_between_acm_jobs(self):
        self.fake.finish = False
        self.run_delegate([{"to": "claude", "task": "Write packing.md"}])

        def from_claude():
            return delegate(self.conn, harness="claude", repo_path=self.folder, summary="User asked in the pane.",
                            tasks=[{"to": "codex", "task": "Write plan.md"}], deps=self.fake.deps(delegated=True))

        with self.assertRaises(AcmError) as caught:
            from_claude()
        self.assertEqual(caught.exception.code, "not_allowed")
        self.assertEqual(len(self.fake.prompts), 1)
        self.fake.complete(*self.fake.prompts[0])
        self.fake.finish = True
        got = from_claude()
        self.assertEqual([(j["agent"], j["state"]) for j in got["jobs"]], [("codex-work", "done")])

    def test_refusals(self):
        with self.assertRaises(AcmError) as caught:
            self.run_delegate([{"to": "codex", "task": "X"}], summary=" ")
        self.assertEqual(caught.exception.code, "invalid")
        with self.assertRaises(AcmError) as caught:
            self.run_delegate([{"to": "codex", "task": " "}])
        self.assertIn("task text", caught.exception.payload["message"])
        with self.assertRaises(AcmError) as caught:
            delegate(self.conn, harness="cursor", repo_path="/", summary="S",
                     tasks=[{"to": "codex", "task": "X"}], deps=self.fake.deps())
        self.assertIn("home folder or /", caught.exception.payload["message"])
        with mock.patch("pathlib.Path.home", return_value=self.folder):
            with self.assertRaises(AcmError) as caught:
                self.run_delegate([{"to": "codex", "task": "X"}])
        self.assertIn("home folder", caught.exception.payload["message"])
        self.assertEqual(self.fake.prompts, [])

    def test_background_without_herdr(self):
        runs = []

        def spawn(cmd, folder, out, log, exit_file):
            runs.append(cmd)
            if cmd[0] == "codex":
                Path(cmd[cmd.index("-o") + 1]).write_text("codex wrote plan.md")
            else:
                log.write_text("boom")
            out.write_text("")
            exit_file.write_text("0\n" if cmd[0] == "codex" else "1\n")

        deps = Deps(herdr=None, use_herdr=lambda: False, spawn=spawn, installed=lambda name: name,
                    delegated=lambda: False, sleep=self.fake.sleep, clock=self.fake.clock)
        got = delegate(self.conn, harness="cursor", repo_path=self.folder, summary="Plan a trip.",
                       tasks=[{"to": "codex", "task": "Write plan.md"}, {"to": "claude", "task": "Write packing.md"}],
                       deps=deps)
        self.assertEqual([(j["agent"], j["pane"], j["state"]) for j in got["jobs"]],
                         [("codex-work", "background", "done"), ("claude-work", "background", "gone")])
        self.assertEqual(got["jobs"][0]["result"], "codex wrote plan.md")
        self.assertIn("exited with code 1. Last lines: boom", got["jobs"][1]["result"])
        self.assertIn("tail -f", got["watch"])
        self.assertEqual([r[:2] for r in runs], [["codex", "exec"], ["claude", "-p"]])
        self.assertIn("## Problem\nPlan a trip.", runs[1][-1])
        with self.assertRaises(AcmError) as caught:
            delegate(self.conn, harness="cursor", repo_path=self.folder, summary="S",
                     tasks=[{"to": "cursor", "task": "X"}],
                     deps=Deps(herdr=None, use_herdr=lambda: False, spawn=spawn, installed=lambda name: None,
                               delegated=lambda: False))
        self.assertEqual(caught.exception.code, "unavailable")

    def test_background_denied_action_comes_back_to_the_caller(self):
        runs = []

        def spawn(cmd, folder, out, log, exit_file):
            runs.append(cmd)
            Path(cmd[cmd.index("-o") + 1]).write_text("BLOCKED: run `npm publish`, which pushes a release")
            out.write_text("")
            exit_file.write_text("0\n")

        deps = Deps(herdr=None, use_herdr=lambda: False, spawn=spawn, installed=lambda name: name,
                    delegated=lambda: False, sleep=self.fake.sleep, clock=self.fake.clock)
        got = delegate(self.conn, harness="cursor", repo_path=self.folder, summary="Ship it.",
                       tasks=[{"to": "codex", "task": "Publish"}], deps=deps)
        self.assertEqual(got["jobs"][0]["state"], "needs_approval")
        self.assertEqual(got["jobs"][0]["result"], "BLOCKED: run `npm publish`, which pushes a release")
        self.assertEqual(got["jobs"][0]["ask"], "run `npm publish`, which pushes a release")
        shown = card(got, [{"to": "codex", "task": "Publish"}])
        self.assertTrue(shown.startswith("acm · delegate(tasks=1 · background)\n\ncodex\nPublish\n"))
        self.assertIn("acm · delegate_wait(0/1 done)", shown)
        self.assertIn("needs_approval · codex wants to run `npm publish`, which pushes a release", shown)
        idle = delegate_wait(self.conn, session=got["session"], deps=deps)
        self.assertEqual(idle["jobs"], [])
        self.assertIn("message", idle)
        self.assertEqual(card(idle), "acm · delegate_wait(nothing running; every result was already reported)")
        self.assertIn("needs_approval", got)
        self.assertNotIn("next", got)
        self.assertIn("## If an action is denied", runs[0][-1])
        again = delegate(self.conn, harness="cursor", repo_path=self.folder, summary="Ship it.",
                         tasks=[{"to": "codex", "task": "Publish; the user approved npm publish"}], deps=deps)
        self.assertEqual(again["jobs"][0]["state"], "needs_approval")
        self.assertEqual(len(runs), 2)
        self.assertIn("--permission-prompts", _headless("claude", "p", "/w", "/a"))

    def test_background_job_still_running_is_stopped_at_the_limit(self):
        pids = []

        def hang(cmd, folder, out, log, exit_file):
            spawn_background(["sleep", "30"], folder, out, log, exit_file)
            pids.append(int(exit_file.with_suffix(".pid").read_text()))

        def stop_leftovers():
            for pid in pids:
                try:
                    os.killpg(pid, signal.SIGKILL)
                except OSError:
                    pass

        self.addCleanup(stop_leftovers)
        deps = Deps(herdr=None, use_herdr=lambda: False, spawn=hang, installed=lambda name: name,
                    delegated=lambda: False, sleep=self.fake.sleep, clock=self.fake.clock)
        with mock.patch("agent_cowork_memory.delegate.JOB_SECONDS", -1):
            stopped = delegate(self.conn, harness="cursor", repo_path=self.folder, summary="Ship it.",
                               tasks=[{"to": "cursor", "task": "Run the risky command"}], deps=deps)
            self.assertEqual(stopped["jobs"][0]["state"], "needs_approval")
            self.assertIn("no result", stopped["jobs"][0]["result"])
            self.assertIn("approval", stopped["jobs"][0]["result"])
            self.assertIn("needs_approval", stopped)
            # The group's last child can stay a zombie for a moment until init reaps it.
            for _ in range(40):
                try:
                    os.killpg(pids[-1], 0)
                except ProcessLookupError:
                    break
                time.sleep(0.05)
            else:
                self.fail("the job's process group is still there")
            again = delegate(self.conn, harness="cursor", repo_path=self.folder, summary="Ship it.",
                             tasks=[{"to": "cursor", "task": "Run it again"}], deps=deps)
        self.assertEqual(again["jobs"][0]["state"], "needs_approval")
        self.assertEqual(len(pids), 2)

    def test_prompt_leaves_out_empty_sections(self):
        text = build_prompt(job="acm_j_1", harness="codex", session="acm_s_1", folder="/w", summary="S", task="T")
        self.assertTrue(text.startswith("[acm job acm_j_1] A codex chat asked for this in /w. Your acm session is acm_s_1."))
        self.assertIn("hold set to every file", text)
        self.assertIn("You decide; say what you checked.", text)
        self.assertNotIn("## Context", text)
        self.assertNotIn("## Others", text)


if __name__ == "__main__":
    unittest.main()
