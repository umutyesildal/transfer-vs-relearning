from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.data.m1_canonical_form_diversity import build_m1_canonical_form_diversity_dataset
from transfer_vs_relearning.data.m1_form_generalization import FORM_TEMPLATES, SCAFFOLDS
from transfer_vs_relearning.data.pre_m2_followup import RELATIONS
from transfer_vs_relearning.data.constants import RELATION_MAP
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_json


VERSION = "qwen_scale_probe_v1"


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_qwen_scale_probe_dataset(repo_root: Path, *, output_dir: Path, monitoring_validation_rows: int = 2301) -> Path:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    hybrid = build_m1_canonical_form_diversity_dataset(
        repo_root, output_dir=output_dir, subject_count=500
    )
    validation_rows = (output_dir / "validation.jsonl").read_text(encoding="utf-8").splitlines()
    if not 0 < monitoring_validation_rows <= len(validation_rows):
        raise ValueError("Invalid monitoring validation row count")
    aligned_validation = output_dir / "validation_replay_aligned.jsonl"
    aligned_validation.write_text("\n".join(validation_rows[:monitoring_validation_rows]) + "\n", encoding="utf-8")
    dataset_dir = repo_root / "artifacts/datasets/relation_v2_gate_v1"
    summary = json.loads((dataset_dir / "acquisition_500_subjects_direct/summary.json").read_text())
    selected = set(summary["selected_subject_ids"])
    profiles = [row for row in read_csv_rows(dataset_dir / "data/canonical_subject_profiles_5000.csv") if row["subject_id"] in selected]
    if len(profiles) != 500:
        raise ValueError(f"Expected 500 selected profiles, found {len(profiles)}")
    probes: list[dict[str, Any]] = []
    for profile in sorted(profiles, key=lambda row: row["subject_id"]):
        for relation in RELATIONS:
            for form_id in ("form_a", "form_b", "form_c", "form_d"):
                question = FORM_TEMPLATES[relation][form_id].format(subject=profile["subject"])
                for scaffold_id, scaffold in SCAFFOLDS.items():
                    probes.append({
                        "probe_id": f"{profile['subject_id']}_{relation}_{form_id}_{scaffold_id}",
                        "fact_id": f"{profile['subject_id']}_{relation}", "subject_id": profile["subject_id"],
                        "subject": profile["subject"], "relation": relation, "form_id": form_id,
                        "scaffold_id": scaffold_id, "question": question,
                        "rendered_prompt": scaffold.format(question=question),
                        "expected_answer": profile[RELATION_MAP[relation][0]], "branch_group": profile["branch_group"],
                        "name_type": profile["name_type"], "name_rarity_bucket": profile["name_rarity_bucket"],
                        "popularity_bucket": profile["popularity_bucket"], "frequency_bucket": profile[RELATION_MAP[relation][2]],
                    })
    if len(probes) != 20000 or len({row["probe_id"] for row in probes}) != 20000:
        raise ValueError("Expected 20,000 unique four-form probes")
    probe_path = output_dir / "evaluations" / "four_form_probe_registry.csv"
    _write_csv(probe_path, probes)
    manifest_path = output_dir / "dataset_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update({"version": VERSION, "four_form_probe_registry": str(probe_path), "four_form_probe_registry_sha256": sha256_file(probe_path), "four_form_probes": len(probes), "monitoring_validation_file": str(aligned_validation), "monitoring_validation_rows": monitoring_validation_rows, "monitoring_validation_sha256": sha256_file(aligned_validation), "nested_100_subjects": sorted(summary["selected_subject_ids"])[:100]})
    write_json(manifest_path, manifest)
    return output_dir
