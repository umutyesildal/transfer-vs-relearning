import hashlib
import json
from pathlib import Path
import re
import tomllib

import yaml


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "documentation/current/PROJECT_STATE.yaml"
EVAL_REGISTRY_PATH = ROOT / "configs/evaluation/eval_v1_registry.yaml"
M0_QUALIFICATION_PATH = ROOT / "configs/evaluation/m0_olmo_eval_v1_qualification_v1.yaml"
LEGACY_DIR = ROOT / "documentation/records/workspace-guidance"
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LM_EVAL_REQUIREMENT = (
    "lm-eval @ git+https://github.com/EleutherAI/lm-evaluation-harness.git@"
    "6d642546f4688648fced259eb3302efd36ece5af"
)


def test_project_state_is_fail_closed_and_uses_sibling_m2_arms():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))

    assert state["schema_version"] == 1
    assert state["readiness"]["evaluation_contract"] == "frozen"
    assert state["readiness"]["ready_to_measure"] is True
    assert state["readiness"]["ready_to_train"] is False
    assert state["readiness"]["selected_primary_model"] is None
    assert state["evaluation_target"]["status"] == "frozen_execution_not_authorized"
    assert state["evaluation_target"]["harness"]["git_commit"] == (
        "6d642546f4688648fced259eb3302efd36ece5af"
    )
    assert state["evaluation_target"]["harness"]["dataset_revisions_frozen"] is True
    assert state["evaluation_target"]["harness"]["environment_locked"] is True
    assert state["repository"]["publication_authorized"] is False
    assert state["repository"]["publication_blockers"] == []
    assert state["repository"]["history_sanitization"][
        "post_filter_reachable_blob_count_gte_10_mib"
    ] == 0
    assert state["repository"]["hu_checkouts"]["active_monorepo"] == {
        "path": "/vol/tmp2/yesildau/transfer-vs-relearning-monorepo-v1",
        "branch": "agent/m0-evaluation",
        "sync_mode": "git_pull_ff_only",
        "dependency_commit_verified": "c3f3c30a31855de920eb268b74bc94d71e9c246d",
        "clean_at_verification": True,
    }
    assert state["repository"]["hu_checkouts"]["legacy_checkout"]["status"] == (
        "preserved_dirty_do_not_pull"
    )
    retention = state["repository"]["hu_checkouts"]["legacy_retention"]
    assert retention["status"] == "inventory_complete_cleanup_not_authorized"
    assert retention["inventory_sha256"] == (
        "daad386c19a74186f37e1319f7cf07a39161d5571c2478549710d7a25d138966"
    )
    assert retention["optimizer_candidate_files"] == 203
    assert retention["optimizer_candidate_bytes"] == 426066757577
    assert retention["delete_authorized"] is False
    assert state["scientific_design"]["sibling_arms"] == {
        "parent": "M1",
        "arms": ["M2-A", "M2-B"],
        "matched_budget_required": True,
    }
    assert state["authorization"]["hu_ssh"] is False
    assert state["authorization"]["training"] is False
    assert state["authorization"]["evaluation_or_scoring"] is False
    assert state["authorization"]["cleanup_or_deletion"] is False

    referenced_paths = [
        state["repository"]["migration_record"],
        state["repository"]["history_sanitization"]["record"],
        state["repository"]["entrypoint_layout"]["record"],
        state["repository"]["entrypoint_layout"]["catalog"],
        state["repository"]["hu_checkouts"]["legacy_retention"]["current_status"],
        state["repository"]["hu_checkouts"]["legacy_retention"]["cleanup_proposal"],
        state["scientific_design"]["current_design_plan"],
        state["scientific_design"]["current_timeline"],
        *state["scientific_design"]["supervisor_realignments"],
        state["evaluation_target"]["contract"],
        state["evaluation_target"]["freeze_record"],
        state["evaluation_target"]["registry"],
        state["evaluation_target"]["scientific_inputs"],
        state["evaluation_target"]["factual_registry_manifest"],
        state["evaluation_target"]["inventory"],
        state["evaluation_target"]["task_qualification"],
        state["evaluation_target"]["result_schema"],
        state["evaluation_target"]["m0_qualification_wave"]["contract"],
        state["evaluation_target"]["m0_qualification_wave"]["recovery"]["contract"],
        state["evaluation_target"]["m0_qualification_wave"]["parity"]["contract"],
        state["evaluation_target"]["m0_qualification_wave"]["parity"]["record"],
        state["evaluation_target"]["m0_qualification_wave"]["config"],
        state["evaluation_target"]["pipeline"]["documentation"],
        state["evaluation_target"]["pipeline"]["deep_dive_guide"],
        state["evaluation_target"]["pipeline"]["prospective_template"],
        state["evaluation_target"]["pipeline"]["full_study_template"],
        state["evaluation_target"]["pipeline"]["full_study_entrypoint"],
        state["evaluation_target"]["pipeline"]["luna_packet_manifest"],
        state["evaluation_target"]["pipeline"]["three_model_matrix"]["contract"],
        state["evaluation_target"]["pipeline"]["three_model_matrix"]["config"],
        state["evaluation_target"]["pipeline"]["three_model_matrix"]["entrypoint"],
        state["evaluation_target"]["pipeline"]["scientific_m0_family"]["contract"],
        state["evaluation_target"]["pipeline"]["scientific_m0_family"]["manifest"],
        state["evaluation_target"]["pipeline"]["scientific_m0_family"]["config_source"],
        state["evaluation_target"]["pipeline"]["scientific_m0_family"]["operator"],
        state["evaluation_target"]["pipeline"]["scientific_m0_family"]["authorization_record"],
        state["evaluation_target"]["pipeline"]["scientific_m0_family"]["preflight_record"],
        state["evaluation_target"]["pipeline"]["scientific_m0_family"]["submission_record"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_recovery"]["contract"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_recovery"]["config"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_recovery"]["operator"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_recovery"]["authorization_record"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_recovery"]["execution_record"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_exclusive_a100_recovery"]["contract"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_exclusive_a100_recovery"]["config"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_exclusive_a100_recovery"]["operator"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_exclusive_a100_recovery"]["authorization_record"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_exclusive_a100_recovery"]["corrected_authorization_record"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_exclusive_a100_recovery"]["submission_record"],
        state["evaluation_target"]["pipeline"]["m0_seven_lane_exclusive_a100_recovery"]["terminal_record"],
        state["evaluation_target"]["pipeline"]["m0_five_lane_retargeted_recovery"]["contract"],
        state["evaluation_target"]["pipeline"]["m0_five_lane_retargeted_recovery"]["config"],
        state["evaluation_target"]["pipeline"]["m0_five_lane_retargeted_recovery"]["operator"],
        state["evaluation_target"]["pipeline"]["m0_five_lane_retargeted_recovery"]["authorization_record"],
        state["evaluation_target"]["pipeline"]["m0_five_lane_retargeted_recovery"]["submission_record"],
        state["evaluation_target"]["pipeline"]["m0_five_lane_retargeted_recovery"]["terminal_record"],
        state["evaluation_target"]["pipeline"]["m0_qwen_pile_single_lane_recovery"]["contract"],
        state["evaluation_target"]["pipeline"]["m0_qwen_pile_single_lane_recovery"]["config"],
        state["evaluation_target"]["pipeline"]["m0_qwen_pile_single_lane_recovery"]["operator"],
        state["evaluation_target"]["pipeline"]["m0_qwen_pile_single_lane_recovery"]["authorization_record"],
        state["evaluation_target"]["pipeline"]["m0_qwen_pile_single_lane_recovery"]["submission_record"],
        state["evaluation_target"]["pipeline"]["m0_exact_prefix_supplement"]["contract"],
        state["evaluation_target"]["pipeline"]["m0_exact_prefix_supplement"]["config"],
        state["evaluation_target"]["pipeline"]["m0_exact_prefix_supplement"]["operator"],
        state["evaluation_target"]["pipeline"]["m0_exact_prefix_supplement"]["authorization_record"],
        state["evaluation_target"]["pipeline"]["m0_exact_prefix_supplement"]["execution_record"],
        state["current_evidence"]["m1_three_model_screen"]["authority"],
        *state["current_evidence"]["dose_pareto_family"]["authorities"],
        state["current_evidence"]["vngrs_corpus_route"]["latest_contract"],
    ]
    for relative in referenced_paths:
        assert (ROOT / relative).is_file(), relative

    qualification = state["evaluation_target"]["m0_qualification_wave"]
    assert qualification["status"] == "qualification_bundle_complete_parity_pass"
    assert qualification["scientific_result"] is False
    assert qualification["completed_lane_count"] == 7
    assert qualification["normalization_allowed"] is True
    assert qualification["qualification_gate"] == "qualified_for_eval_v1_freeze_review"
    assert qualification["qualification_blockers"] == []
    assert qualification["parity"]["heading_job_id"] == "461668"
    assert qualification["parity"]["finalizer_job_id"] == "461669"
    assert qualification["execution_ready"] is False
    assert qualification["execution_authorized"] is False
    assert qualification["recovery"]["lane_job_id"] == "461595"
    assert qualification["recovery"]["finalizer_job_id"] == "461596"

    matrix = state["evaluation_target"]["pipeline"]["three_model_matrix"]
    assert matrix["status"] == "planned_not_authorized"
    assert matrix["model_count"] == 3
    assert matrix["node_count"] == 27
    assert matrix["training_node_count"] == 9
    assert matrix["state_evaluation_node_count"] == 12
    assert matrix["execution_authorized"] is False

    scientific_m0 = state["evaluation_target"]["pipeline"]["scientific_m0_family"]
    assert scientific_m0["status"] == "terminal_partial_invalid_17_of_24"
    assert scientific_m0["models"] == ["olmo", "qwen", "smollm"]
    assert scientific_m0["model_count"] == 3
    assert scientific_m0["lanes_per_model"] == 8
    assert scientific_m0["total_gpu_lanes"] == 24
    assert scientific_m0["execution_ready"] is True
    assert scientific_m0["execution_authorized"] is True
    assert scientific_m0["wave_limit"] == 1
    assert scientific_m0["automatic_retry_authorized"] is False
    assert scientific_m0["authorization_consumed"] is True
    assert scientific_m0["resubmission_authorized"] is False
    assert len(scientific_m0["job_ledger"]["olmo"]["lanes"]) == 8
    assert len(scientific_m0["job_ledger"]["qwen"]["lanes"]) == 8
    assert len(scientific_m0["job_ledger"]["smollm"]["lanes"]) == 8
    assert scientific_m0["job_ledger"]["family_finalizer"] == "461898"
    assert scientific_m0["hu_home_gate"]["limit_bytes"] == 30 * 1024**3
    assert scientific_m0["hu_home_gate"]["writes_authorized"] is False
    assert scientific_m0["hu_identity_checks_passed_for_all_models"] is True
    assert scientific_m0["hu_focused_tests"] == 39
    assert scientific_m0["scientific_work_started"] is True
    assert scientific_m0["scientific_metrics_available"] is False
    assert scientific_m0["latest_read_only_snapshot_utc"] == "2026-08-20T07:59:47Z"
    assert scientific_m0["lane_snapshot"] == {
        "complete": 17,
        "failed_pre_scoring": 7,
        "running": 0,
        "pending": 0,
    }
    assert scientific_m0["terminal_raw_bundle"] == {
        "path": "/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_v1/three_model_m0_raw_bundle.json",
        "sha256": "75fcd7cf1e388eb5a4e883264c6aa14db83797b2e7832a4bbc8e40bb38865db1",
        "written_at_local": "2026-08-16T22:23:14+02:00",
        "status": "partial_invalid_no_cross_model_summary",
        "normalization_allowed": False,
        "cross_model_pass_fail": "not_computed_by_raw_family_finalizer",
    }

    recovery = state["evaluation_target"]["pipeline"]["m0_seven_lane_recovery"]
    assert recovery["status"] == "terminal_not_run_gpu_memory_guard_all_seven"
    assert recovery["contract_sha256"] == (
        "1ee7c8d9d1da092cd1e4a64dbffa4594e041ebf2b4d56eb62f345a6aaa8c25c4"
    )
    assert recovery["pre_authorization_config_sha256"] == (
        "4a603719dd43a65dd9b36a36786407993afe84cf8d1d48f6245656d235c6bfeb"
    )
    assert recovery["config_sha256"] == (
        "d934b782fe307d1d54b7fdce47be8ebc2409a6b6c2acf3f2aa435aa4577ac6d7"
    )
    assert recovery["retained_lane_count"] == 17
    assert recovery["recovery_lane_count"] == 7
    assert recovery["gpu_lane_count"] == 7
    assert recovery["model_finalizer_count"] == 3
    assert recovery["family_finalizer_count"] == 1
    assert recovery["execution_authorized"] is False
    assert recovery["authorization_consumed"] is True
    assert recovery["resubmission_authorized"] is False
    assert recovery["scientific_score_count"] == 0
    assert len(recovery["submitted_jobs"]["lane_jobs"]) == 7
    assert len(recovery["submitted_jobs"]["model_finalizers"]) == 3
    assert recovery["submitted_jobs"]["family_finalizer"] == "470533"
    assert recovery["composite_status"] == "partial_invalid_no_cross_model_summary"
    assert recovery["automatic_retry_authorized"] is False
    assert recovery["normalization_authorized"] is False
    assert recovery["m1_or_m2_authorized"] is False

    recovery_authorization = state["authorization"]["scoped"]["m0_seven_lane_recovery"]
    assert recovery_authorization["status"] == "consumed_terminal_not_run"
    assert recovery_authorization["execution_authorized"] is False
    assert recovery_authorization["wave_consumed"] is True
    assert recovery_authorization["resubmission_authorized"] is False
    assert recovery_authorization["wave_limit"] == 1
    assert recovery_authorization["recovery_lane_count"] == 7
    assert recovery_authorization["rescore_complete_lanes_authorized"] is False
    assert len(scientific_m0["known_operational_failures"]) == 7

    isolated = state["evaluation_target"]["pipeline"]["m0_seven_lane_exclusive_a100_recovery"]
    assert isolated["status"] == "terminal_partial_invalid_cancelled_output_routing_defect"
    assert isolated["contract_sha256"] == (
        "d2a6d9e35c60a00328380fe7ecfb68bfa3fdd0528ea469ecec0acfecdc849058"
    )
    assert isolated["config_sha256"] == (
        "cdf0fbd30027dc44c1ec876606fb92f32b0df1121c0dc4fe2c10ad254494c5e8"
    )
    assert isolated["retained_lane_count"] == 17
    assert isolated["recovery_lane_count"] == 7
    assert isolated["slurm_job_count"] == 5
    assert isolated["node"] == "gruenau10"
    assert isolated["gres"] == "gpu:a10080gb:3"
    assert isolated["execution_authorized"] is True
    assert isolated["automatic_retry_authorized"] is False
    assert isolated["normalization_authorized"] is False
    assert isolated["controller_cancelled_by_user"] is True
    assert isolated["valid_recovered_lane_count"] == 2
    assert isolated["invalid_recovered_lane_count"] == 1
    assert isolated["not_run_recovery_lane_count"] == 4

    isolated_authorization = state["authorization"]["scoped"][
        "m0_seven_lane_exclusive_a100_recovery"
    ]
    assert isolated_authorization["status"] == "authorized_single_wave"
    assert isolated_authorization["execution_authorized"] is True
    assert isolated_authorization["wave_limit"] == 1
    assert isolated_authorization["slurm_job_count"] == 5

    retargeted = state["evaluation_target"]["pipeline"]["m0_five_lane_retargeted_recovery"]
    assert retargeted["status"] == "terminal_partial_invalid_23_of_24"
    assert retargeted["contract_sha256"] == (
        "1b030869455d68aa0ecf933f881c1661e1fbf504997376fdba08a626e1bc0a55"
    )
    assert retargeted["config_sha256"] == (
        "08cbe81574b63aa3f488e7f17cc1f6f41b339e85c5d5814b7cbd6fbf76f27c41"
    )
    assert retargeted["retained_lane_count"] == 19
    assert retargeted["recovery_lane_count"] == 5
    assert retargeted["slurm_job_count"] == 5
    assert retargeted["execution_authorized"] is False
    assert retargeted["authorization_consumed"] is True
    assert retargeted["resubmission_authorized"] is False
    assert retargeted["wave_job"] == "471536"
    assert retargeted["family_finalizer"] == "471540"
    assert retargeted["valid_recovered_lane_count"] == 4
    assert retargeted["blocked_recovery_lane_count"] == 1
    assert retargeted["effective_valid_lane_count"] == 23
    assert retargeted["terminal_composite_sha256"] == (
        "5871bc480d3b04027b25fd49b6eb1d65cdc234de1f34aaf39f21088e52b25243"
    )
    assert retargeted["normalization_authorized"] is False
    assert retargeted["m1_or_m2_authorized"] is False
    assert retargeted["automatic_retry_authorized"] is False

    retargeted_authorization = state["authorization"]["scoped"][
        "m0_five_lane_retargeted_recovery"
    ]
    assert retargeted_authorization["status"] == "consumed_by_single_submission"
    assert retargeted_authorization["execution_authorized"] is False
    assert retargeted_authorization["wave_consumed"] is True
    assert retargeted_authorization["resubmission_authorized"] is False
    assert retargeted_authorization["wave_limit"] == 1
    assert retargeted_authorization["retained_lane_count"] == 19
    assert retargeted_authorization["recovery_lane_count"] == 5

    single = state["evaluation_target"]["pipeline"]["m0_qwen_pile_single_lane_recovery"]
    assert single["status"] == "submitted_pending_resources"
    assert single["contract_sha256"] == (
        "88f135f74c8e1932660128e4e36f99cdb13923be15fb7ba82c6c3a2a98c40332"
    )
    assert single["pre_authorization_config_sha256"] == (
        "f394ca3ecf0e056f825545675b41f7fc7b970da240b41156fff030019a36cf36"
    )
    assert single["retained_lane_count"] == 23
    assert single["recovery_lane_count"] == 1
    assert single["target"] == "qwen:english_retention_pile_10k"
    assert single["min_free_gpu_bytes"] == 64 * 1024**3
    assert single["execution_authorized"] is False
    assert single["authorization_consumed"] is True
    assert single["resubmission_authorized"] is False
    assert single["final_preflight_checks_passed"] == 15
    assert single["final_preflight_blockers"] == []
    assert single["wave_job"] == "472809"
    assert single["family_finalizer"] == "472813"
    assert single["normalization_authorized"] is False

    single_authorization = state["authorization"]["scoped"][
        "m0_qwen_pile_single_lane_recovery"
    ]
    assert single_authorization["status"] == "consumed_by_single_submission"
    assert single_authorization["execution_authorized"] is False
    assert single_authorization["wave_consumed"] is True
    assert single_authorization["resubmission_authorized"] is False
    assert single_authorization["wave_limit"] == 1

    exact = state["evaluation_target"]["pipeline"]["m0_exact_prefix_supplement"]
    assert exact["status"] == "terminal_not_run_gpu_memory_guard_all_three"
    assert exact["semantic_classification"] == (
        "historical_exact_prefix_candidate_ranking_not_free_generation"
    )
    assert exact["models"] == ["olmo", "qwen", "smollm"]
    assert exact["probe_count_per_model"] == 500
    assert exact["slurm_job_count"] == 4
    assert exact["execution_authorized"] is False
    assert exact["robust_a_to_d_rerun_authorized"] is False
    assert exact["authorization_consumed"] is True
    assert exact["not_run_lane_count"] == 3
    assert exact["valid_scientific_score_count"] == 0
    assert exact["array_job"] == "473834"
    assert exact["finalizer_job"] == "473835"

    exact_authorization = state["authorization"]["scoped"]["m0_exact_prefix_supplement"]
    assert exact_authorization["status"] == "consumed_terminal_not_run"
    assert exact_authorization["execution_authorized"] is False
    assert exact_authorization["wave_limit"] == 1
    assert exact_authorization["robust_a_to_d_rerun_authorized"] is False
    assert exact_authorization["wave_consumed"] is True
    assert exact_authorization["resubmission_authorized"] is False


def test_active_entrypoints_stay_within_context_budget():
    limits = {
        ROOT / "AGENTS.md": 250,
        ROOT / "README.md": 180,
        ROOT / ".agents/README.md": 180,
    }
    for path, maximum in limits.items():
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        assert line_count <= maximum, f"{path.relative_to(ROOT)} has {line_count} lines"


def test_control_plane_markdown_links_resolve():
    paths = [
        ROOT / "README.md",
        ROOT / "documentation/README.md",
        *sorted((ROOT / "documentation/current").glob("*.md")),
        *sorted((ROOT / "documentation/contracts").glob("*.md")),
        *sorted((ROOT / "documentation/decisions").glob("*.md")),
        *sorted((ROOT / "documentation/evaluation").glob("*.md")),
        *sorted((ROOT / "documentation/pipeline").glob("*.md")),
        ROOT / "documentation/records/README.md",
    ]

    failures = []
    for path in paths:
        for target in MARKDOWN_LINK_RE.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0]
            if not relative:
                continue
            resolved = (path.parent / relative).resolve()
            if not resolved.exists():
                failures.append(f"{path.relative_to(ROOT)} -> {target}")
    assert not failures, "Broken documentation links:\n" + "\n".join(failures)


def test_eval_v1_registry_is_frozen_but_execution_stays_unauthorized():
    registry = yaml.safe_load(EVAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    assert registry["name"] == "eval-v1"
    assert registry["status"] == "frozen"
    assert registry["execution_ready"] is True
    assert registry["execution_authorized"] is False
    assert registry["harness"]["release"] == "v0.4.12"
    assert registry["harness"]["git_commit"] == (
        "6d642546f4688648fced259eb3302efd36ece5af"
    )
    tasks = {row["id"]: row for row in registry["standard_tasks"]}
    assert tasks["wikitext"]["primary_metric"] == "bits_per_byte"
    assert tasks["pile_10k"]["inclusion"] == "core"
    assert tasks["pile_10k"]["cadence"] == "full"
    assert tasks["hellaswag"]["primary_metric"] == "acc_norm"
    assert tasks["turblimp_core"]["primary_metric"] == "acc_norm"
    assert tasks["turkishmmlu"]["inclusion"] == "excluded_eval_v1_access_blocked"
    assert registry["cadence"]["dense"]["rule"] == (
        "every_epoch_end_including_parent_for_future_runs"
    )
    assert registry["retention"]["derived_retention_score"]["scientific_gate"] is False
    assert registry["training_trace"]["epoch_snapshot_policy"] == "model_only_every_epoch"
    assert registry["pipeline"]["stage_order"][-2:] == [
        "normalization",
        "presentation_bundle",
    ]
    assert registry["freeze_blockers"] == []
    assert registry["final_harness_task_ids"] == [
        "wikitext",
        "pile_10k",
        "blimp",
        "hellaswag",
        "winogender_female",
        "winogender_male",
        "winogender_neutral",
        "turblimp_core",
    ]
    assert registry["custom_factual"]["full_registry"]["rows"] == 12_000
    assert registry["custom_factual"]["cheap_registry"]["rows"] == 1_500
    assert registry["scientific_gates"]["transfer_m2_a_minus_m1"][
        "tr_to_en_top1_minimum_gain"
    ] == 0.05


def test_m0_qualification_is_non_scientific_and_fail_closed():
    qualification = yaml.safe_load(M0_QUALIFICATION_PATH.read_text(encoding="utf-8"))

    assert qualification["status"] == "frozen"
    assert qualification["classification"] == "qualification_only"
    assert qualification["scientific_result"] is False
    assert qualification["execution_ready"] is True
    assert qualification["execution_authorized"] is True
    assert qualification["model"]["repository"] == "allenai/OLMo-2-0425-1B"
    assert qualification["model"]["revision"] == (
        "a1847dff35000b4271fa70afc5db10fd29fedbdf"
    )
    assert qualification["harness"]["git_commit"] == (
        "6d642546f4688648fced259eb3302efd36ece5af"
    )
    assert qualification["test_only_policy"]["metrics_may_enter_scientific_tables"] is False
    assert qualification["test_only_policy"]["normalizer_must_reject_mixed_classifications"] is True
    assert qualification["allowed_final_gate_values"] == [
        "qualified_for_eval_v1_freeze_review",
        "blocked",
    ]
    assert "scientific_m0_score" in qualification["forbidden_claims"]
    assert qualification["freeze_blockers"] == []
    assert qualification["eval_v1_promotion_blockers"]


def test_lm_eval_dependency_is_pinned_to_the_qualified_commit():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    environment = yaml.safe_load((ROOT / "environment.yml").read_text(encoding="utf-8"))
    pip_dependencies = next(
        row["pip"] for row in environment["dependencies"] if isinstance(row, dict) and "pip" in row
    )

    assert LM_EVAL_REQUIREMENT in project["project"]["dependencies"]
    assert LM_EVAL_REQUIREMENT in pip_dependencies


def test_legacy_guidance_hashes_are_preserved():
    manifest = json.loads(
        (LEGACY_DIR / "LEGACY_GUIDANCE_MANIFEST.json").read_text(encoding="utf-8")
    )
    for filename, expected in manifest["files"].items():
        payload = (LEGACY_DIR / filename).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == expected
