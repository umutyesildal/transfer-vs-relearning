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
    assert state["readiness"]["ready_to_measure"] is False
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
        state["evaluation_target"]["pipeline"]["prospective_template"],
        state["evaluation_target"]["pipeline"]["full_study_template"],
        state["evaluation_target"]["pipeline"]["full_study_entrypoint"],
        state["evaluation_target"]["pipeline"]["luna_packet_manifest"],
        state["evaluation_target"]["pipeline"]["three_model_matrix"]["contract"],
        state["evaluation_target"]["pipeline"]["three_model_matrix"]["config"],
        state["evaluation_target"]["pipeline"]["three_model_matrix"]["entrypoint"],
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
