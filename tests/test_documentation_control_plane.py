import hashlib
import json
from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "documentation/current/PROJECT_STATE.yaml"
EVAL_REGISTRY_PATH = ROOT / "configs/evaluation/eval_v1_registry.yaml"
M0_QUALIFICATION_PATH = ROOT / "configs/evaluation/m0_olmo_eval_v1_qualification_v1.yaml"
LEGACY_DIR = ROOT / "documentation/records/workspace-guidance"
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def test_project_state_is_fail_closed_and_uses_sibling_m2_arms():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))

    assert state["schema_version"] == 1
    assert state["readiness"]["evaluation_contract"] == "not_frozen"
    assert state["readiness"]["ready_to_measure"] is False
    assert state["readiness"]["ready_to_train"] is False
    assert state["readiness"]["selected_primary_model"] is None
    assert state["evaluation_target"]["status"] == "draft_upstream_semantics_qualified"
    assert state["evaluation_target"]["harness"]["git_commit"] == (
        "6d642546f4688648fced259eb3302efd36ece5af"
    )
    assert state["evaluation_target"]["harness"]["dataset_revisions_frozen"] is False
    assert state["evaluation_target"]["harness"]["environment_locked"] is False
    assert state["repository"]["publication_authorized"] is False
    assert state["repository"]["publication_blockers"] == []
    assert state["repository"]["history_sanitization"][
        "post_filter_reachable_blob_count_gte_10_mib"
    ] == 0
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
        state["scientific_design"]["current_design_plan"],
        *state["scientific_design"]["supervisor_realignments"],
        state["evaluation_target"]["draft_contract"],
        state["evaluation_target"]["registry"],
        state["evaluation_target"]["inventory"],
        state["evaluation_target"]["task_qualification"],
        state["evaluation_target"]["result_schema"],
        state["evaluation_target"]["m0_qualification_wave"]["contract"],
        state["evaluation_target"]["m0_qualification_wave"]["config"],
        state["evaluation_target"]["pipeline"]["documentation"],
        state["evaluation_target"]["pipeline"]["prospective_template"],
        state["evaluation_target"]["pipeline"]["full_study_template"],
        state["evaluation_target"]["pipeline"]["full_study_entrypoint"],
        state["evaluation_target"]["pipeline"]["luna_packet_manifest"],
        state["current_evidence"]["m1_three_model_screen"]["authority"],
        *state["current_evidence"]["dose_pareto_family"]["authorities"],
        state["current_evidence"]["vngrs_corpus_route"]["latest_contract"],
    ]
    for relative in referenced_paths:
        assert (ROOT / relative).is_file(), relative

    qualification = state["evaluation_target"]["m0_qualification_wave"]
    assert qualification["status"] == "draft_not_executable"
    assert qualification["scientific_result"] is False
    assert qualification["execution_ready"] is False
    assert qualification["execution_authorized"] is False


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


def test_eval_v1_registry_is_draft_and_fail_closed():
    registry = yaml.safe_load(EVAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    assert registry["name"] == "eval-v1"
    assert registry["status"] == "draft"
    assert registry["execution_ready"] is False
    assert registry["execution_authorized"] is False
    assert registry["harness"]["release"] == "v0.4.12"
    assert registry["harness"]["git_commit"] == (
        "6d642546f4688648fced259eb3302efd36ece5af"
    )
    tasks = {row["id"]: row for row in registry["standard_tasks"]}
    assert tasks["wikitext"]["primary_metric"] == "bits_per_byte"
    assert tasks["pile_10k"]["inclusion"] == "core_pending_runtime"
    assert tasks["hellaswag"]["primary_metric"] == "acc_norm"
    assert tasks["turblimp_core"]["primary_metric"] == "acc_norm"
    assert tasks["xnli_en"]["dataset_config"] == "en"
    assert tasks["xnli_tr"]["dataset_config"] == "tr"
    assert tasks["turkishmmlu"]["status"] == "dataset_access_unverified"
    assert registry["cadence"]["dense"]["rule"] == (
        "every_epoch_end_including_parent_for_future_runs"
    )
    assert registry["retention"]["derived_retention_score"]["scientific_gate"] is False
    assert registry["training_trace"]["epoch_snapshot_policy"] == "model_only_every_epoch"
    assert registry["pipeline"]["stage_order"][-2:] == [
        "normalization",
        "presentation_bundle",
    ]
    assert registry["freeze_blockers"]


def test_m0_qualification_is_non_scientific_and_fail_closed():
    qualification = yaml.safe_load(M0_QUALIFICATION_PATH.read_text(encoding="utf-8"))

    assert qualification["status"] == "draft_not_executable"
    assert qualification["classification"] == "qualification_only"
    assert qualification["scientific_result"] is False
    assert qualification["execution_ready"] is False
    assert qualification["execution_authorized"] is False
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
    assert qualification["freeze_blockers"]


def test_legacy_guidance_hashes_are_preserved():
    manifest = json.loads(
        (LEGACY_DIR / "LEGACY_GUIDANCE_MANIFEST.json").read_text(encoding="utf-8")
    )
    for filename, expected in manifest["files"].items():
        payload = (LEGACY_DIR / filename).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == expected
