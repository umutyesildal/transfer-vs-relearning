import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "orchestrator.py"
SPEC = importlib.util.spec_from_file_location("thesis_orchestrator", MODULE_PATH)
assert SPEC and SPEC.loader
orchestrator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(orchestrator)


def valid_decision(**overrides):
    value = {
        "goal_id": "goal-001",
        "status": "continue",
        "task_id": "task-001",
        "task": "Make one local change",
        "reason": "The goal is incomplete",
        "scope_class": "local_write",
        "requires_user_authorization": False,
        "authorization_request": "",
        "allowed_paths": ["transfer-vs-relearning/src/example.py"],
        "forbidden_actions": ["no remote access"],
        "acceptance_criteria": ["test passes"],
        "required_evidence": ["git diff"],
    }
    value.update(overrides)
    return value


class OrchestratorTests(unittest.TestCase):
    def test_extract_thread_id_from_jsonl(self):
        session_id = "019fe62f-6c94-7132-ab2d-02118875e4a4"
        events = json.dumps({"type": "thread.started", "thread_id": session_id}) + "\n"
        self.assertEqual(orchestrator.extract_thread_id(events), session_id)

    def test_validate_decision_accepts_local_write(self):
        decision = valid_decision()
        orchestrator.validate_decision(decision, "goal-001")
        config = {"auto_allowed_scope_classes": ["local_read_only", "local_write"]}
        self.assertTrue(orchestrator.decision_is_dispatchable(decision, config))

    def test_external_scope_is_never_automatically_dispatched(self):
        decision = valid_decision(scope_class="external_read_only")
        orchestrator.validate_decision(decision)
        config = {"auto_allowed_scope_classes": ["local_read_only", "local_write"]}
        self.assertFalse(orchestrator.decision_is_dispatchable(decision, config))

    def test_local_write_requires_allowed_path(self):
        with self.assertRaises(orchestrator.OrchestratorError):
            orchestrator.validate_decision(valid_decision(allowed_paths=[]))

    def test_changed_paths_preserves_baseline_logic(self):
        before = {"repo/a.py": "sha256:old", "repo/existing.txt": "same"}
        after = {"repo/a.py": "sha256:new", "repo/existing.txt": "same", "repo/new.py": "sha256:x"}
        self.assertEqual(orchestrator.changed_paths(before, after), ["repo/a.py", "repo/new.py"])

    def test_porcelain_parser_preserves_index_state(self):
        parsed = orchestrator.parse_porcelain_z(" M tracked.py\0?? new.py\0")
        self.assertEqual(parsed, {"tracked.py": " M", "new.py": "??"})

    def test_path_scope_matching(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            self.assertTrue(
                orchestrator.path_is_allowed(
                    "transfer-vs-relearning/tests/test_x.py",
                    ["transfer-vs-relearning/tests/**"],
                    workspace,
                )
            )
            self.assertFalse(
                orchestrator.path_is_allowed(
                    "syntheticFacts/output/data.jsonl",
                    ["transfer-vs-relearning/tests/**"],
                    workspace,
                )
            )

    def test_head_change_is_never_path_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            self.assertFalse(
                orchestrator.path_is_allowed(
                    "git::HEAD",
                    ["**"],
                    workspace,
                )
            )

    def test_workspace_repository_snapshot_uses_repository_relative_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            orchestrator.run_command(
                ["git", "init", str(workspace)], cwd=workspace, timeout=30
            )
            orchestrator.run_command(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=workspace,
                timeout=30,
            )
            orchestrator.run_command(
                ["git", "config", "user.name", "Test User"], cwd=workspace, timeout=30
            )
            (workspace / "tracked.txt").write_text("base\n", encoding="utf-8")
            orchestrator.run_command(["git", "add", "tracked.txt"], cwd=workspace, timeout=30)
            orchestrator.run_command(
                ["git", "commit", "-m", "base"], cwd=workspace, timeout=30
            )
            (workspace / "README.md").write_text("changed\n", encoding="utf-8")
            config = {
                "repositories": ["."],
                "root_watch_paths": [],
                "limits": {"max_file_hash_bytes": 1024},
            }
            snapshot = orchestrator.capture_snapshot(config, workspace)
            self.assertIn("git::HEAD", snapshot)
            self.assertIn("README.md", snapshot)
            self.assertNotIn("./README.md", snapshot)

    def test_goal_id_mismatch_fails_closed(self):
        with self.assertRaises(orchestrator.OrchestratorError):
            orchestrator.validate_decision(valid_decision(), "different-goal")

    def test_codex_schema_keyword_guard(self):
        schema = {"type": "array", "uniqueItems": True, "items": {"type": "string"}}
        self.assertEqual(
            orchestrator.find_unsupported_schema_keys(schema),
            ["$.uniqueItems"],
        )

    def test_task_packet_is_small_scoped_and_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            (workspace / "AGENTS.md").write_text("# Instructions\n", encoding="utf-8")
            packet = workspace / ".agents/task-packets/study/task.md"
            packet.parent.mkdir(parents=True)
            packet.write_text(
                "# Task\n\n## Objective\n\nOne task.\n\n"
                "## Context budget\n\n- `AGENTS.md`\n\n"
                "## Allowed paths\n\n- `tests/example.py`\n\n"
                "## Acceptance criteria\n\n- Pass.\n\n"
                "## Stop conditions\n\n- Stop.\n\n"
                "## Handoff\n\nReport.\n",
                encoding="utf-8",
            )
            goal = "Status: ACTIVE\nGoal ID: goal-1\nTask packet: .agents/task-packets/study/task.md\n"
            self.assertEqual(
                orchestrator.validate_task_packet(goal, workspace, 80),
                packet,
            )

    def test_task_packet_rejects_escape_placeholder_and_excess_context(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            with self.assertRaises(orchestrator.OrchestratorError):
                orchestrator.validate_task_packet(
                    "Task packet: ../outside.md\n", workspace, 80
                )
            packet = workspace / ".agents/task-packets/task.md"
            packet.parent.mkdir(parents=True)
            packet.write_text(
                "## Objective\n__TODO__\n## Context budget\n- `a`\n"
                "## Allowed paths\n- `b`\n## Acceptance criteria\n- c\n"
                "## Stop conditions\n- d\n## Handoff\n- e\n",
                encoding="utf-8",
            )
            with self.assertRaises(orchestrator.OrchestratorError):
                orchestrator.validate_task_packet(
                    "Task packet: .agents/task-packets/task.md\n", workspace, 80
                )

    def test_task_packet_rejects_context_outside_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            packet = workspace / ".agents/task-packets/task.md"
            packet.parent.mkdir(parents=True)
            packet.write_text(
                "## Objective\nOne task.\n## Context budget\n- `../outside.md`\n"
                "## Allowed paths\n- `b`\n## Acceptance criteria\n- c\n"
                "## Stop conditions\n- d\n## Handoff\n- e\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(orchestrator.OrchestratorError, "escapes workspace"):
                orchestrator.validate_task_packet(
                    "Task packet: .agents/task-packets/task.md\n", workspace, 80
                )


if __name__ == "__main__":
    unittest.main()
