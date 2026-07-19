from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from transfer_vs_relearning.data.m1_canonical_form_diversity import (
    EXACT_PREFIX_HASH,
    FOUR_FORM_HASH,
    SLOTS,
    VERSION,
    build_m1_canonical_form_diversity_dataset,
)
from transfer_vs_relearning.utils.io import read_jsonl


def test_hybrid_builder_preserves_canonical_slots_and_budget(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output = build_m1_canonical_form_diversity_dataset(repo_root, output_dir=tmp_path / VERSION)
    manifest = json.loads((output / "dataset_manifest.json").read_text(encoding="utf-8"))
    rows = read_jsonl(output / "train.jsonl")
    assert manifest["status"] == "passed"
    assert manifest["slots"] == list(SLOTS)
    assert manifest["four_form_registry_sha256"] == FOUR_FORM_HASH
    assert manifest["exact_prefix_sha256"] == EXACT_PREFIX_HASH
    assert len(rows) == 3500
    assert Counter(row["training_representation"] for row in rows) == Counter({
        "decl_01": 500, "decl_02": 500, "decl_03": 500,
        "form_a_qa": 500, "form_a_direct": 500,
        "form_b_qa": 500, "form_b_direct": 500,
    })
    by_fact: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_fact.setdefault(str(row["fact_id"]), []).append(row)
    assert len(by_fact) == 500
    for fact_rows in by_fact.values():
        assert [row["training_representation"] for row in fact_rows] == list(SLOTS)
        assert {row.get("training_form_id") for row in fact_rows if row["training_representation"].startswith("form_")} == {"form_a", "form_b"}
        assert not {row.get("training_form_id") for row in fact_rows} & {"form_c", "form_d"}
