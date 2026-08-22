from __future__ import annotations

from pathlib import Path

from transfer_vs_relearning.study.m1_wave_controller import build_m1_wave_plan


ROOT = Path(__file__).resolve().parents[1]
CONFIGS = [
    ROOT / "configs/pipelines/m1_olmo_epoch_trajectory_draft.yaml",
    ROOT / "configs/pipelines/m1_qwen_epoch_trajectory_draft.yaml",
    ROOT / "configs/pipelines/m1_smollm_epoch_trajectory_draft.yaml",
]
STATE = ROOT / "documentation/current/PROJECT_STATE.yaml"


def test_fresh_m1_wave_is_matched_and_fail_closed() -> None:
    plan = build_m1_wave_plan(CONFIGS, repo_root=ROOT, project_state_path=STATE)

    assert plan["status"] == "blocked"
    assert plan["execution_authorized"] is False
    assert plan["training"]["expected_epoch_snapshots_per_model"] == 36
    assert plan["training"]["expected_trajectory_states_per_model"] == 37
    assert plan["training"]["expected_total_eval_states"] == 111
    assert plan["evaluation"]["checkpoint_evaluation_tasks"] == 111
    assert not [row for row in plan["training"]["recipe_checks"] if row["status"] != "pass"]
    assert "project_ready_to_train_and_checkpoint" in plan["blockers"]


def test_fresh_m1_wave_has_parallel_training_barriers_and_final_barrier() -> None:
    plan = build_m1_wave_plan(CONFIGS, repo_root=ROOT, project_state_path=STATE)
    tasks = plan["tasks"]

    assert sum(task["kind"] == "training_preflight" for task in tasks) == 3
    assert sum(task["kind"] == "training_and_epoch_trace" for task in tasks) == 3
    assert sum(task["kind"] == "checkpoint_evaluation" for task in tasks) == 111
    assert tasks[-2]["kind"] == "normalization"
    assert tasks[-1]["kind"] == "presentation"

    training_ids = {
        task["task_id"]
        for task in tasks
        if task["kind"] == "training_and_epoch_trace"
    }
    eval_tasks = [task for task in tasks if task["kind"] == "checkpoint_evaluation"]
    assert {dependency for task in eval_tasks for dependency in task["depends_on"]} == training_ids
    assert set(tasks[-2]["depends_on"]) == {task["task_id"] for task in eval_tasks}
