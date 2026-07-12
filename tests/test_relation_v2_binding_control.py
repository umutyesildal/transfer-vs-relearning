from __future__ import annotations

from collections import Counter
from pathlib import Path

from transfer_vs_relearning.data.relation_v2_binding_control import build_relation_v2_binding_control
from transfer_vs_relearning.utils.io import read_csv_rows, read_jsonl, sha256_file


def test_binding_control_is_symmetric_and_budget_preserving(tmp_path: Path) -> None:
    source = Path("artifacts/datasets/relation_v2_gate_v1")
    output = tmp_path / "binding_control"
    manifest = build_relation_v2_binding_control(source, output)

    original = read_jsonl(source / "acquisition_10_subjects_direct/train.jsonl")
    transformed = read_jsonl(output / "train.jsonl")
    profiles = {
        row["subject_id"]: row
        for row in read_csv_rows(source / "data/canonical_subject_profiles_5000.csv")
    }

    assert len(transformed) == 350
    assert Counter(Counter(row["fact_id"] for row in transformed).values()) == {7: 50}
    changed = [row for row in transformed if row["template_id"].endswith("_binding_control")]
    assert len(changed) == 60
    assert Counter(row["relation"] for row in changed) == {"born_in": 30, "lives_in": 30}
    assert set(Counter(row["fact_id"] for row in changed).values()) == {3}

    original_by_template = {(row["fact_id"], row["template_id"]): row for row in original}
    unchanged = [row for row in transformed if not row["template_id"].endswith("_binding_control")]
    assert all(row == original_by_template[(row["fact_id"], row["template_id"])] for row in unchanged)

    for row in changed:
        profile = profiles[row["subject_id"]]
        assert profile["birthplace_en"] in row["text"]
        assert profile["residence_en"] in row["text"]
        assert row["text"].rstrip(".").endswith(row["answer"])

    assert manifest["contract"]["heldout_validation_changed"] is False
    assert manifest["source"]["validation_sha256"] == sha256_file(
        source / "acquisition_10_subjects_direct/validation.jsonl"
    )


def test_binding_control_is_deterministic(tmp_path: Path) -> None:
    source = Path("artifacts/datasets/relation_v2_gate_v1")
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_manifest = build_relation_v2_binding_control(source, first)
    second_manifest = build_relation_v2_binding_control(source, second)
    assert first_manifest["files"] == second_manifest["files"]
