import json
import os
import re
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

from agent_cowork_memory.db import connect
from agent_cowork_memory.ledger import AcmError, attach, checkpoint
from agent_cowork_memory.readers import opencode
from agent_cowork_memory.transcript import chats, cursor_for, resume, transcript_read


def git_repo(path):
    path.mkdir()
    subprocess.run(["git", "-C", path, "init", "-q"], check=True)
    subprocess.run(["git", "-C", path, "config", "user.email", "acm@localhost"], check=True)
    subprocess.run(["git", "-C", path, "config", "user.name", "acm"], check=True)
    (path / "README.md").write_text("x\n")
    subprocess.run(["git", "-C", path, "add", "README.md"], check=True)
    subprocess.run(["git", "-C", path, "commit", "-qm", "init"], check=True)


def cursor_line(session_id, text, tool=True):
    content = []
    if tool:
        content.append({"type": "tool_use", "name": "attach", "input": {"session": session_id}})
    content.append({"type": "text", "text": text})
    return json.dumps({"role": "assistant", "message": {"content": content}}) + "\n"


class TranscriptTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.repo = Path(self.tmp.name) / "repo"
        self.root = Path(self.tmp.name) / "transcripts"
        self.root.mkdir()
        git_repo(self.repo)
        self.conn = connect(self.home)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def attach_pair(self):
        owner = attach(self.conn, repo_path=self.repo, harness="cursor", label="a", title="T")
        other = attach(self.conn, repo_path=self.repo, harness="codex", label="b", task=owner["task"])
        return owner, other

    def test_bind_read_ack_and_partial(self):
        owner, other = self.attach_pair()
        path = self.root / "chat.jsonl"
        path.write_text(cursor_line(owner["session"], "hello"))
        pending = transcript_read(self.conn, session=other["session"], target=owner["session"], root=self.root / "missing")
        self.assertEqual(pending["status"], "pending")
        got = transcript_read(self.conn, session=other["session"], target=owner["session"], root=self.root)
        self.assertEqual(got["status"], "ok")
        self.assertEqual(got["records"][0]["text"], "hello")
        self.assertIsNone(cursor_for(self.conn, consumer=owner["session"], target=other["session"]))
        path.write_text(path.read_text() + '{"role":')
        again = transcript_read(
            self.conn, session=other["session"], target=owner["session"],
            root=self.root, since_cursor=got["next_cursor"],
        )
        self.assertEqual(again["records"], [])
        path.write_text(path.read_text() + '"user","message":{"content":[{"type":"text","text":"more"}]}}\n')
        more = transcript_read(
            self.conn, session=other["session"], target=owner["session"],
            root=self.root, since_cursor=got["next_cursor"],
        )
        self.assertEqual([row["text"] for row in more["records"]], ["more"])
        checkpoint(
            self.conn, session=owner["session"], task=owner["task"], expect_version=1,
            summary="acked", ack_target=owner["session"], ack_cursor=more["next_cursor"],
        )
        self.assertEqual(cursor_for(self.conn, consumer=owner["session"], target=owner["session"]), more["next_cursor"])
        other_conn = connect(self.home)
        try:
            self.assertEqual(
                cursor_for(other_conn, consumer=owner["session"], target=owner["session"]),
                more["next_cursor"],
            )
        finally:
            other_conn.close()

    def test_ambiguous_missing_and_other_task(self):
        owner, other = self.attach_pair()
        (self.root / "a.jsonl").write_text(cursor_line(other["session"], "a"))
        (self.root / "b.jsonl").write_text(cursor_line(other["session"], "b"))
        fuzzy = transcript_read(self.conn, session=owner["session"], target=other["session"], root=self.root)
        self.assertEqual(fuzzy["status"], "ambiguous")
        lone = Path(self.tmp.name) / "one"
        lone.mkdir()
        file = lone / "only.jsonl"
        file.write_text(cursor_line(other["session"], "only"))
        transcript_read(self.conn, session=owner["session"], target=other["session"], root=lone)
        file.unlink()
        gone = transcript_read(self.conn, session=owner["session"], target=other["session"], root=lone)
        self.assertEqual(gone["status"], "unavailable")
        stranger = attach(self.conn, repo_path=self.repo, harness="claude", label="c", title="Other")
        with self.assertRaises(AcmError) as caught:
            transcript_read(self.conn, session=owner["session"], target=stranger["session"], root=lone)
        self.assertEqual(caught.exception.code, "not_found")

    def test_replacement_bumps_generation(self):
        owner, other = self.attach_pair()
        path = self.root / "chat.jsonl"
        path.write_text(cursor_line(owner["session"], "one"))
        first = transcript_read(self.conn, session=other["session"], target=owner["session"], root=self.root)
        path.write_bytes(b'{"role":"user","message":{"content":[{"type":"text","text":"replaced"}]}}\n')
        second = transcript_read(self.conn, session=other["session"], target=owner["session"], root=self.root)
        self.assertGreater(second["generation"], first["generation"])
        self.assertEqual(second["records"][0]["text"], "replaced")

    def test_resume_latest_chat_per_harness(self):
        repo = self.repo.resolve()
        slug = str(repo).strip("/").replace("/", "-")
        owner = attach(self.conn, repo_path=self.repo, harness="cursor", label="a", title="Trip")
        chat = self.root / slug.rsplit("-", 1)[0] / "agent-transcripts" / "c1" / "c1.jsonl"
        chat.parent.mkdir(parents=True)
        chat.write_text(
            '{"role":"user","message":{"content":[{"type":"text","text":"pick a city"}]}}\n'
            + cursor_line(owner["session"], "Lisbon")
        )
        got = resume(self.conn, harness="codex", repo_path=self.repo, source="cursor", root=self.root)
        self.assertEqual(got["task"], owner["task"])
        self.assertEqual([m["text"] for m in got["messages"]], ["pick a city", "Lisbon"])
        self.assertEqual(got["chat_workspace"], str(repo.parent))

        rollout = self.root / "codex" / "2026" / "rollout-x.jsonl"
        rollout.parent.mkdir(parents=True)
        rollout.write_text(
            json.dumps({"type": "session_meta", "payload": {"session_id": "cx", "cwd": str(repo)}}) + "\n"
            + json.dumps({"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "plan it"}]}}) + "\n"
        )
        fresh = resume(self.conn, harness="claude", repo_path=self.repo, source="codex", root=self.root / "codex")
        self.assertNotEqual(fresh["task"], owner["task"])
        self.assertEqual(fresh["title"], "plan it")

        claude_chat = self.root / "claude" / re.sub(r"[^A-Za-z0-9]", "-", str(repo)) / "s1.jsonl"
        claude_chat.parent.mkdir(parents=True)
        claude_chat.write_text(json.dumps({"type": "user", "sessionId": "s1", "message": {"role": "user", "content": "hi"}}) + "\n")
        back = resume(self.conn, harness="cursor", repo_path=self.repo, source="claude", root=self.root / "claude")
        self.assertEqual(back["messages"], [{"role": "user", "text": "hi"}])

        with self.assertRaises(AcmError) as caught:
            resume(self.conn, harness="cursor", repo_path=self.repo, source="cursor", root=self.root)
        self.assertEqual(caught.exception.code, "invalid")
        own_kind = resume(self.conn, harness="cursor", repo_path=self.repo, chat="c1", root=self.root, roots={"cursor": self.root})
        self.assertEqual(own_kind["native_id"], "c1")

    def test_resume_lets_the_user_choose_between_chats(self):
        slug = str(self.repo.resolve()).strip("/").replace("/", "-")
        mine = self.root / slug / "agent-transcripts" / "c1" / "c1.jsonl"
        job = self.root / slug / "agent-transcripts" / "c2" / "c2.jsonl"
        older = self.root / slug / "agent-transcripts" / "c3" / "c3.jsonl"
        for path, text in ((mine, "plan the trip"), (job, "[acm job acm_j_0123456789ab] A codex chat asked for this"), (older, "pack bags")):
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"role": "user", "message": {"content": [{"type": "text", "text": text}]}}) + "\n")
        owner = attach(self.conn, repo_path=self.repo, harness="cursor", label="a", title="Trip")
        with mine.open("a") as out:
            out.write(cursor_line(owner["session"], "Lisbon"))
        os.utime(mine, (1_000, 1_000))
        os.utime(older, (500, 500))
        roots = {kind: self.root / "missing" for kind in ("codex", "claude", "opencode")} | {"cursor": self.root}

        listed = chats(self.conn, repo_path=self.repo, roots=roots)["chats"]
        self.assertEqual([(c["agent"], c["chat"], c["job"]) for c in listed], [
            ("cursor", "c2", "acm_j_0123456789ab"), ("cursor", "c1", None), ("cursor", "c3", None),
        ])
        self.assertEqual(listed[1]["first"], "plan the trip")

        picked = resume(self.conn, harness="codex", repo_path=self.repo, chat="c1", roots=roots)
        self.assertEqual(picked["native_id"], "c1")
        self.assertEqual(picked["task"], owner["task"])
        asked = resume(self.conn, harness="codex", repo_path=self.repo, roots=roots)
        self.assertNotIn("messages", asked)
        self.assertEqual([(c["chat"], c["task"]) for c in asked["choose"]], [("c1", "Trip"), ("c3", None), ("c2", None)])
        self.assertEqual(asked["more"], 0)

        with self.assertRaises(AcmError) as caught:
            resume(self.conn, harness="codex", repo_path=self.repo, source="cursor", chat="nope", root=self.root)
        self.assertEqual(caught.exception.code, "not_found")
        with self.assertRaises(AcmError) as caught:
            resume(self.conn, harness="cursor", repo_path=self.repo, roots=roots)
        self.assertEqual(caught.exception.code, "not_found")

    def test_resume_picks_the_users_one_chat_over_job_chats(self):
        slug = str(self.repo.resolve()).strip("/").replace("/", "-")
        for name, text in (("c1", "plan the trip"), ("j1", "[acm job acm_j_0123456789ab] A codex chat asked"),
                           ("j2", "Note: The user opened the file x.md. [acm job acm_j_ba9876543210] A codex chat asked")):
            path = self.root / slug / "agent-transcripts" / name / f"{name}.jsonl"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"role": "user", "message": {"content": [{"type": "text", "text": text}]}}) + "\n")
        got = resume(self.conn, harness="codex", repo_path=self.repo, roots={"cursor": self.root})
        self.assertEqual(got["native_id"], "c1")

    def test_resume_picks_the_one_chat_in_the_repo_over_parent_folder_chats(self):
        slug = str(self.repo.resolve()).strip("/").replace("/", "-")
        for folder, name, text in ((slug, "c1", "x" * 30_000), (slug.rsplit("-", 1)[0], "c2", "home chat")):
            path = self.root / folder / "agent-transcripts" / name / f"{name}.jsonl"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps({"role": "user", "message": {"content": [{"type": "text", "text": text}]}}) + "\n"
                + json.dumps({"role": "user", "message": {"content": [{"type": "text", "text": "y" * 2_000}]}}) + "\n"
            )
        got = resume(self.conn, harness="codex", repo_path=self.repo, roots={"cursor": self.root})
        self.assertEqual(got["native_id"], "c1")
        self.assertEqual(got["omitted_messages"], 1)
        self.assertEqual(got["clipped_messages"], 0)

    def test_resume_claude_dotted_folder_image_and_done_task(self):
        repo = Path(self.tmp.name) / "my.app_x"
        git_repo(repo)
        chat = self.root / re.sub(r"[^A-Za-z0-9]", "-", str(repo.resolve())) / "s1.jsonl"
        chat.parent.mkdir(parents=True)
        image = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "x"}}
        chat.write_text(json.dumps({
            "type": "user", "sessionId": "s1",
            "message": {"role": "user", "content": [image, {"type": "text", "text": "fix this screen"}]},
        }) + "\n")
        first = resume(self.conn, harness="cursor", repo_path=repo, source="claude", root=self.root)
        self.assertEqual(first["messages"], [{"role": "user", "text": "fix this screen"}])
        checkpoint(self.conn, session=first["session"], task=first["task"], expect_version=1, summary="done", status="done")
        again = resume(self.conn, harness="codex", repo_path=repo, source="claude", root=self.root)
        self.assertNotEqual(again["task"], first["task"])

    def test_resume_clips_one_huge_message_and_finds_cursor_folders_with_odd_names(self):
        repo = Path(self.tmp.name) / "my_app.v2"
        git_repo(repo)
        dashed = re.sub(r"[^A-Za-z0-9]", "-", str(repo.resolve())).strip("-")
        chat = self.root / dashed / "agent-transcripts" / "c9" / "c9.jsonl"
        chat.parent.mkdir(parents=True)
        huge = "start " + "x" * 50_000 + " end"
        chat.write_text(json.dumps({"role": "user", "message": {"content": [{"type": "text", "text": huge}]}}) + "\n")

        got = resume(self.conn, harness="codex", repo_path=repo, source="cursor", root=self.root, budget=1_000)
        self.assertEqual(got["native_id"], "c9")
        self.assertEqual(got["clipped_messages"], 1)
        text = got["messages"][0]["text"]
        self.assertLess(len(text), 1_100)
        self.assertTrue(text.startswith("start ") and text.endswith(" end"))
        self.assertIn("characters cut", text)

    def test_resume_reads_opencode_files_and_sqlite(self):
        repo = self.repo.resolve()
        storage = self.root / "storage"
        session = storage / "session" / "proj" / "ses_old.json"
        session.parent.mkdir(parents=True)
        session.write_text(json.dumps({"id": "ses_old", "directory": str(repo)}))
        msg = storage / "message" / "ses_old" / "m1.json"
        msg.parent.mkdir(parents=True)
        msg.write_text(json.dumps({"id": "m1", "role": "user"}))
        part = storage / "part" / "m1" / "p1.json"
        part.parent.mkdir(parents=True)
        part.write_text(json.dumps({"type": "text", "text": "from files"}))
        os_utime = session.stat().st_mtime

        db = self.root / "opencode.db"
        conn = sqlite3.connect(db)
        conn.executescript(
            """CREATE TABLE session (id TEXT, directory TEXT, time_updated INTEGER, parent_id TEXT);
               CREATE TABLE message (id TEXT, session_id TEXT, time_created INTEGER, data TEXT);
               CREATE TABLE part (id TEXT, message_id TEXT, time_created INTEGER, data TEXT);"""
        )
        conn.execute("INSERT INTO session VALUES ('ses_new', ?, ?, NULL)", (str(repo), int((os_utime + 10) * 1000)))
        conn.execute("INSERT INTO message VALUES ('m2', 'ses_new', 2, ?)", (json.dumps({"role": "user"}),))
        conn.execute("INSERT INTO part VALUES ('p2', 'm2', 2, ?)", (json.dumps({"type": "text", "text": "from sqlite"}),))
        conn.commit()
        conn.close()
        asked = resume(self.conn, harness="cursor", repo_path=self.repo, source="opencode", root=self.root)
        self.assertEqual([c["chat"] for c in asked["choose"]], ["ses_new", "ses_old"])
        got = resume(self.conn, harness="cursor", repo_path=self.repo, source="opencode", chat="ses_new", root=self.root)
        self.assertEqual([m["text"] for m in got["messages"]], ["from sqlite"])
        self.assertEqual(got["native_id"], "ses_new")

        conn = sqlite3.connect(db)
        conn.execute("INSERT INTO session VALUES ('ses_old', ?, ?, NULL)", (str(repo), int((os_utime + 20) * 1000)))
        conn.commit()
        conn.close()
        asked = resume(self.conn, harness="cursor", repo_path=self.repo, source="opencode", root=self.root)
        self.assertEqual([c["chat"] for c in asked["choose"]], ["ses_old", "ses_new"])

    def test_opencode_turn_ends_only_after_a_finished_reply(self):
        session = self.root / "session" / "ses_1.json"
        session.parent.mkdir(parents=True)
        session.write_text(json.dumps({"id": "ses_1", "directory": "/w"}))
        messages = [
            ("m1", {"role": "user", "time": {"created": 1}}, "go"),
            ("m2", {"role": "assistant", "finish": "tool-calls", "time": {"created": 2, "completed": 3}}, "reading"),
            ("m3", {"role": "assistant", "finish": "stop", "time": {"created": 4}}, "still writing"),
        ]
        for mid, msg, text in messages:
            (self.root / "message" / "ses_1").mkdir(parents=True, exist_ok=True)
            (self.root / "message" / "ses_1" / f"{mid}.json").write_text(json.dumps({"id": mid, **msg}))
            (self.root / "part" / mid).mkdir(parents=True)
            (self.root / "part" / mid / "p.json").write_text(json.dumps({"type": "text", "text": text}))
        self.assertNotIn(b"turn_ended", opencode.read(session))
        done = {"id": "m3", "role": "assistant", "finish": "stop", "time": {"created": 4, "completed": 5}}
        (self.root / "message" / "ses_1" / "m3.json").write_text(json.dumps(done))
        self.assertEqual(opencode.read(session).count(b"turn_ended"), 1)

    def test_plain_folder_is_a_project(self):
        plain = Path(self.tmp.name) / "plain" / "sub"
        plain.mkdir(parents=True)
        first = attach(self.conn, repo_path=plain, harness="cursor", label="a", title="No git")
        again = attach(self.conn, repo_path=plain, harness="codex", label="b", task=first["task"])
        self.assertEqual(first["project"], again["project"])

    def test_resume_keeps_recent_messages_before_large_tool_output(self):
        rollout = self.root / "codex" / "2026" / "rollout-large.jsonl"
        rollout.parent.mkdir(parents=True)
        def line(payload):
            return json.dumps({"type": "response_item", "payload": payload}) + "\n"
        rollout.write_text(
            json.dumps({"type": "session_meta", "payload": {"session_id": "cx", "cwd": str(self.repo)}}) + "\n"
            + line({"type": "message", "role": "user", "content": [{"type": "input_text", "text": "install grill-me"}]})
            + line({"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Installed grill-me"}]})
            + line({"type": "function_call_output", "output": "x" * 1_100_000})
            + line({"type": "message", "role": "user", "content": [{"type": "input_text", "text": "what happened?"}]})
        )
        got = resume(self.conn, harness="cursor", repo_path=self.repo, source="codex", root=self.root / "codex")
        self.assertEqual([m["text"] for m in got["messages"]], ["install grill-me", "Installed grill-me", "what happened?"])
        self.assertEqual(got["omitted_messages"], 0)


if __name__ == "__main__":
    unittest.main()
