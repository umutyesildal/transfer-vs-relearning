import hashlib
import json
from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "documentation/current/PROJECT_STATE.yaml"
LEGACY_DIR = ROOT / "documentation/records/workspace-guidance"
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def test_project_state_is_fail_closed_and_uses_sibling_m2_arms():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))

    assert state["schema_version"] == 1
    assert state["readiness"]["evaluation_contract"] == "not_frozen"
    assert state["readiness"]["ready_to_measure"] is False
    assert state["readiness"]["ready_to_train"] is False
    assert state["readiness"]["selected_primary_model"] is None
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
        state["scientific_design"]["current_design_plan"],
        *state["scientific_design"]["supervisor_realignments"],
        state["current_evidence"]["m1_three_model_screen"]["authority"],
        *state["current_evidence"]["dose_pareto_family"]["authorities"],
        state["current_evidence"]["vngrs_corpus_route"]["latest_contract"],
    ]
    for relative in referenced_paths:
        assert (ROOT / relative).is_file(), relative


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


def test_legacy_guidance_hashes_are_preserved():
    manifest = json.loads(
        (LEGACY_DIR / "LEGACY_GUIDANCE_MANIFEST.json").read_text(encoding="utf-8")
    )
    for filename, expected in manifest["files"].items():
        payload = (LEGACY_DIR / filename).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == expected
