#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.data.qwen_pre_m2 import (
    VERSION,
    build_bilingual_hard_probes,
    build_m3_branch_b_fact_registry,
    selected_profiles,
    validate_intermediate_population,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the compact 2,500-fact Qwen pre-M2 registries."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite pre-M2 contract: {output_root}")

    dataset_root = repo_root / "artifacts/datasets/relation_v2_gate_v1"
    profiles_path = dataset_root / "data/canonical_subject_profiles_5000.csv"
    selection_path = dataset_root / "acquisition_500_subjects_direct/summary.json"
    canonical_rows = read_csv_rows(profiles_path)
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selected_ids = set(selection["selected_subject_ids"])
    profiles = selected_profiles(canonical_rows, selected_ids)
    population = validate_intermediate_population(profiles)

    probes = build_bilingual_hard_probes(canonical_rows, selected_ids)
    facts = build_m3_branch_b_fact_registry(canonical_rows, selected_ids)
    output_root.mkdir(parents=True)
    selected_path = output_root / "population/selected_subjects.csv"
    probes_path = output_root / "evaluation/bilingual_hard_probe_registry.csv"
    facts_path = output_root / "adaptation/m3_branch_b_fact_registry.csv"
    write_csv(selected_path, profiles)
    write_csv(probes_path, probes)
    write_csv(facts_path, facts)

    slice_registry: list[dict[str, object]] = []
    for direction in ("en_to_en", "tr_to_en", "tr_to_tr"):
        for form_id in ("form_a", "form_b", "form_c", "form_d"):
            for scaffold_id in ("direct", "qa"):
                slice_rows = [
                    row
                    for row in probes
                    if row["direction"] == direction
                    and row["form_id"] == form_id
                    and row["scaffold_id"] == scaffold_id
                ]
                if len(slice_rows) != 2_500:
                    raise ValueError(
                        f"Expected 2,500 probes for {direction}/{form_id}/{scaffold_id}"
                    )
                slice_id = f"{direction}_{form_id}_{scaffold_id}"
                slice_path = output_root / f"evaluation/slices/{slice_id}.csv"
                write_csv(slice_path, slice_rows)
                slice_registry.append(
                    {
                        "task_index": len(slice_registry),
                        "slice_id": slice_id,
                        "direction": direction,
                        "form_id": form_id,
                        "scaffold_id": scaffold_id,
                        "probe_count": len(slice_rows),
                        "path": str(slice_path),
                        "sha256": sha256_file(slice_path),
                    }
                )
    slice_registry_path = output_root / "evaluation/slice_registry.json"
    write_json(slice_registry_path, slice_registry)

    manifest_path = output_root / "manifest.json"
    artifacts = {
        "selected_subjects": selected_path,
        "bilingual_hard_probes": probes_path,
        "evaluation_slice_registry": slice_registry_path,
        "m3_branch_b_facts": facts_path,
    }
    write_json(
        manifest_path,
        {
            "status": "compact_pre_m2_registries_ready",
            "version": VERSION,
            "population": population,
            "directions": ["en_to_en", "tr_to_en", "tr_to_tr"],
            "forms": ["form_a", "form_b", "form_c", "form_d"],
            "scaffolds": ["direct", "qa"],
            "probe_count": len(probes),
            "evaluation_slice_count": len(slice_registry),
            "probes_per_slice": 2_500,
            "m3_branch_b_fact_count": len(facts),
            "source_files": {
                "canonical_profiles": {
                    "path": str(profiles_path.resolve()),
                    "sha256": sha256_file(profiles_path),
                },
                "selected_subject_summary": {
                    "path": str(selection_path.resolve()),
                    "sha256": sha256_file(selection_path),
                },
            },
            "artifacts": {
                label: {"path": str(path), "sha256": sha256_file(path)}
                for label, path in artifacts.items()
            },
            "not_yet_materialized": [
                "m2_clean_token_blocks",
                "m3_fact_token_blocks",
                "matched_token_budget_audit",
                "selected_qwen_model_reload_evaluation",
            ],
        },
    )
    print(manifest_path)


if __name__ == "__main__":
    main()
