from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.m1_form_generalization import FORM_TEMPLATES, SCAFFOLDS, _write_jsonl
from transfer_vs_relearning.data.pre_m2_followup import RELATIONS
from transfer_vs_relearning.utils.io import read_jsonl, sha256_file, write_json
from transfer_vs_relearning.utils.text import normalize_text


VERSION = "m1_canonical_form_diversity_v1"
SLOTS = ("decl_01", "decl_02", "decl_03", "form_a_qa", "form_a_direct", "form_b_qa", "form_b_direct")
FOUR_FORM_HASH = "54bf2968bcffecee8f0438b0ac489a6ab5fd0150dca2c459a4a1ad9efe50796b"
EXACT_PREFIX_HASH = "1644288d0d62c51c56ceaae71b9eef7225b88326267281c8df8aeef9d7619c8e"


def build_m1_canonical_form_diversity_dataset(repo_root: Path, *, output_dir: Path | None = None) -> Path:
    repo_root = repo_root.resolve()
    source_dir = repo_root / "artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct"
    output_dir = (output_dir or repo_root / f"artifacts/{VERSION}").resolve()
    source_rows = read_jsonl(source_dir / "train.jsonl")
    by_fact: dict[str, dict[str, dict[str, Any]]] = {}
    for row in source_rows:
        template = str(row["template_id"])
        if template.endswith(("decl_01", "decl_02", "decl_03")):
            by_fact.setdefault(str(row["fact_id"]), {})[template.rsplit("_", 2)[-2] + "_" + template.rsplit("_", 1)[-1]] = row
    if len(by_fact) != 500 or any(set(rows) != {"decl_01", "decl_02", "decl_03"} for rows in by_fact.values()):
        raise ValueError("Canonical declarative source rows are incomplete")
    train: list[dict[str, Any]] = []
    validation: list[dict[str, Any]] = []
    for fact_id in sorted(by_fact):
        declaratives = by_fact[fact_id]
        reference = declaratives["decl_01"]
        relation, subject, answer = str(reference["relation"]), str(reference["subject"]), str(reference["answer"])
        for index, slot in enumerate(SLOTS, start=1):
            if slot.startswith("decl_"):
                row = {**declaratives[slot]}
                row.update({"condition": "canonical_balanced_ab", "exposure_index": index, "training_representation": slot, "split": f"{VERSION}_train"})
            else:
                form_id, scaffold_id = slot.rsplit("_", 1)
                question = FORM_TEMPLATES[relation][form_id].format(subject=subject)
                row = {**reference, "condition": "canonical_balanced_ab", "exposure_index": index, "training_representation": slot, "training_form_id": form_id, "scaffold_id": scaffold_id, "split": f"{VERSION}_train", "template_id": f"{relation}_{slot}", "text": f"{SCAFFOLDS[scaffold_id].format(question=question)} {answer}"}
            train.append(row)
        validation.append({**reference, "condition": "canonical_balanced_ab", "split": f"{VERSION}_validation", "training_representation": "decl_01_monitor"})
    train_path, validation_path = output_dir / "train.jsonl", output_dir / "validation.jsonl"
    _write_jsonl(train_path, train)
    _write_jsonl(validation_path, validation)
    counts = Counter(row["fact_id"] for row in train)
    c_forms = Counter(row.get("training_form_id", "declarative") for row in train)
    expected = Counter({"declarative": 1500, "form_a": 1000, "form_b": 1000})
    if len(train) != 3500 or len(validation) != 500 or set(counts.values()) != {7} or c_forms != expected:
        raise ValueError("Hybrid curriculum budget integrity failed")
    write_json(output_dir / "dataset_manifest.json", {"version": VERSION, "status": "passed", "slots": list(SLOTS), "train_rows": len(train), "validation_rows": len(validation), "facts": len(counts), "training_representation_counts": dict(Counter(row["training_representation"] for row in train)), "training_form_counts": dict(c_forms), "train_sha256": sha256_file(train_path), "validation_sha256": sha256_file(validation_path), "four_form_registry_sha256": FOUR_FORM_HASH, "exact_prefix_sha256": EXACT_PREFIX_HASH})
    return output_dir
