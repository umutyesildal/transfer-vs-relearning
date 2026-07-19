#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.data.turkish_bridge import (
    VERSION,
    build_bridge_probes,
    build_localization_rows,
    eligibility_summary,
    eligible_fact_rows,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


def _model_path(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Use MODEL_LABEL=/path/to/hard_suite_per_fact.csv")
    label, path = value.split("=", 1)
    if not label.strip() or not path.strip():
        raise argparse.ArgumentTypeError("Model label and result path must be non-empty")
    return label.strip(), Path(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze the Document 109 Turkish bridge data/evaluation contract.")
    parser.add_argument("--canonical-profiles", type=Path, default=Path("artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv"))
    parser.add_argument("--selected-subjects", type=Path, default=Path("artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/summary.json"))
    parser.add_argument("--hard-result", action="append", type=_model_path, default=[])
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/turkish_bridge_v1"))
    args = parser.parse_args()

    canonical_path = args.canonical_profiles.resolve()
    selected_path = args.selected_subjects.resolve()
    output_dir = args.output_dir.resolve()
    canonical_rows = read_csv_rows(canonical_path)
    selected = json.loads(selected_path.read_text(encoding="utf-8"))
    selected_ids = set(selected["selected_subject_ids"])

    localization_rows = build_localization_rows(canonical_rows)
    probe_rows = build_bridge_probes(canonical_rows, selected_ids)
    localization_path = output_dir / "localization_candidates.csv"
    probe_path = output_dir / "bridge_probe_registry.csv"
    write_csv(localization_path, localization_rows)
    write_csv(probe_path, probe_rows)

    eligibility: dict[str, object] = {}
    eligible_sets: dict[str, set[str]] = {}
    for label, raw_path in args.hard_result:
        result_path = raw_path.resolve()
        rows = eligible_fact_rows(result_path)
        out_path = output_dir / "eligibility" / f"{label}.csv"
        write_csv(out_path, rows)
        eligible_sets[label] = {str(row["fact_id"]) for row in rows if row["eligible_3_of_4_heldout"]}
        eligibility[label] = {
            "source": str(result_path),
            "source_sha256": sha256_file(result_path),
            "output": str(out_path),
            "output_sha256": sha256_file(out_path),
            "summary": eligibility_summary(rows),
        }

    if eligible_sets:
        shared = set.intersection(*eligible_sets.values())
        shared_rows = [{"fact_id": fact_id, "shared_eligible": True} for fact_id in sorted(shared)]
        shared_path = output_dir / "eligibility" / "shared_intersection.csv"
        write_csv(shared_path, shared_rows, ["fact_id", "shared_eligible"])
    else:
        shared, shared_path = set(), None

    manifest = {
        "version": VERSION,
        "status": "contract_ready_eligibility_pending" if not eligibility else "contract_ready",
        "canonical_profiles": str(canonical_path),
        "canonical_profiles_sha256": sha256_file(canonical_path),
        "selected_subjects": str(selected_path),
        "selected_subjects_sha256": sha256_file(selected_path),
        "subject_count": len(selected_ids),
        "fact_count": len(selected_ids) * 5,
        "directions": ["en_to_en", "tr_to_en", "tr_to_tr"],
        "probe_count": len(probe_rows),
        "probe_registry": str(probe_path),
        "probe_registry_sha256": sha256_file(probe_path),
        "localization_registry": str(localization_path),
        "localization_registry_sha256": sha256_file(localization_path),
        "alias_policy": "canonical-only-v1; aliases may be expanded only before outcome evaluation",
        "eligibility_rule": "top1 and positive margin on at least 3 of 4 held-out C/D x direct/QA English cells",
        "strict_rule": "top1 and positive margin on all 8 A/B/C/D x direct/QA English cells",
        "eligibility": eligibility,
        "shared_eligible_count": len(shared) if eligibility else None,
        "shared_eligible_file": str(shared_path) if shared_path else None,
        "shared_eligible_sha256": sha256_file(shared_path) if shared_path else None,
    }
    write_json(output_dir / "manifest.json", manifest)
    print(output_dir / "manifest.json")


if __name__ == "__main__":
    main()
