#!/usr/bin/env python3
"""Validate and assemble the 24 endpoint slices for each Qwen M2/M3 state.

The evaluator deliberately writes one scratch directory per state/slice.  This
script is the strict, CPU-only bridge from those immutable slice artifacts to
the state-level CSVs consumed by ``analyze_qwen_m2_m3_results.py``.  It refuses
to create an output directory unless every frozen slice is complete and its
probe IDs exactly match the frozen registry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json


REQUIRED_RESULT_COLUMNS = {
    "probe_id",
    "subject_id",
    "fact_id",
    "direction",
    "relation",
    "form_id",
    "scaffold_id",
    "branch_group",
    "frequency_bucket",
    "name_type",
    "name_rarity_bucket",
    "popularity_bucket",
    "correct_rank_mean",
}


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.resolve().read_text(encoding="utf-8"))


def _slice_registry(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.resolve().read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"Slice registry must be a non-empty JSON list: {path}")
    seen: set[str] = set()
    for item in payload:
        slice_id = str(item.get("slice_id", "")).strip()
        if not slice_id or slice_id in seen:
            raise ValueError(f"Invalid or duplicate slice_id in registry: {slice_id!r}")
        seen.add(slice_id)
        if int(item.get("probe_count", 0)) <= 0:
            raise ValueError(f"Invalid probe_count for {slice_id}")
        probe_path = Path(str(item.get("path", ""))).resolve()
        if not probe_path.is_file():
            raise FileNotFoundError(f"Frozen probe registry is missing: {probe_path}")
        declared_hash = str(item.get("sha256", "")).strip()
        if declared_hash and sha256_file(probe_path) != declared_hash:
            raise ValueError(f"Frozen probe registry hash mismatch: {slice_id}")
    return payload


def _validate_slice(
    *,
    state_id: str,
    results_root: Path,
    registry_item: dict[str, Any],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    slice_id = str(registry_item["slice_id"])
    result_root = results_root / slice_id
    summary_path = result_root / "summary.json"
    run_manifest_path = result_root / "run_manifest.json"
    result_path = result_root / "hard_suite_per_fact.csv"
    if not result_root.is_dir():
        raise FileNotFoundError(f"Missing result directory: {state_id}/{slice_id}")
    if not summary_path.is_file() or not run_manifest_path.is_file() or not result_path.is_file():
        raise ValueError(f"Incomplete result artifacts: {state_id}/{slice_id}")

    summary = _json(summary_path)
    run_manifest = _json(run_manifest_path)
    if summary.get("status") != "completed":
        raise ValueError(f"Slice summary is not completed: {state_id}/{slice_id}")
    if run_manifest.get("status") != "completed":
        raise ValueError(f"Slice run manifest is not completed: {state_id}/{slice_id}")

    rows = read_csv_rows(result_path)
    expected_count = int(registry_item["probe_count"])
    if len(rows) != expected_count:
        raise ValueError(
            f"Probe count mismatch for {state_id}/{slice_id}: "
            f"expected={expected_count} found={len(rows)}"
        )
    if not rows:
        raise ValueError(f"Empty result CSV: {state_id}/{slice_id}")
    missing_columns = REQUIRED_RESULT_COLUMNS - set(rows[0])
    if missing_columns:
        raise ValueError(f"Missing columns for {state_id}/{slice_id}: {sorted(missing_columns)}")
    result_ids = [str(row["probe_id"]) for row in rows]
    if len(set(result_ids)) != len(result_ids):
        raise ValueError(f"Duplicate probe_id values in {state_id}/{slice_id}")

    registry_rows = read_csv_rows(Path(str(registry_item["path"])).resolve())
    registry_ids = [str(row["probe_id"]) for row in registry_rows]
    if len(registry_ids) != expected_count or len(set(registry_ids)) != expected_count:
        raise ValueError(f"Frozen registry is malformed for {slice_id}")
    if set(result_ids) != set(registry_ids):
        missing = sorted(set(registry_ids) - set(result_ids))[:5]
        extra = sorted(set(result_ids) - set(registry_ids))[:5]
        raise ValueError(
            f"Probe registry mismatch for {state_id}/{slice_id}: missing={missing} extra={extra}"
        )

    return rows, {
        "state_id": state_id,
        "slice_id": slice_id,
        "result_root": str(result_root.resolve()),
        "result_path": str(result_path.resolve()),
        "result_sha256": sha256_file(result_path),
        "summary_sha256": sha256_file(summary_path),
        "run_manifest_sha256": sha256_file(run_manifest_path),
        "probe_count": len(rows),
    }


def _assemble_state(
    *,
    state: dict[str, Any],
    registry: list[dict[str, Any]],
    output_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    state_id = str(state["state_id"])
    results_root = Path(str(state["results_root"])).resolve()
    rows: list[dict[str, str]] = []
    slice_records: list[dict[str, Any]] = []
    for item in registry:
        slice_rows, record = _validate_slice(
            state_id=state_id,
            results_root=results_root,
            registry_item=item,
        )
        rows.extend(slice_rows)
        slice_records.append(record)

    probe_ids = [str(row["probe_id"]) for row in rows]
    if len(set(probe_ids)) != len(probe_ids):
        raise ValueError(f"Duplicate probe_id across slices for state {state_id}")
    state_path = output_dir / "states" / state_id / "per_probe_results.csv"
    state_record = {
        "state_id": state_id,
        "arm": str(state["arm"]),
        "seed": str(state["seed"]),
        "path": str(state_path.resolve()),
        "sha256": "",
        "row_count": len(rows),
        "slice_count": len(slice_records),
    }
    return state_record, {"state_id": state_id, "slices": slice_records, "row_count": len(rows)}, rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation-manifest", type=Path, required=True)
    parser.add_argument("--slice-registry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    evaluation_manifest_path = args.evaluation_manifest.resolve()
    registry_path = args.slice_registry.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite assembly output: {output_dir}")

    evaluation_manifest = _json(evaluation_manifest_path)
    states = evaluation_manifest.get("states")
    if not isinstance(states, list) or not states:
        raise ValueError("Evaluation manifest must contain a non-empty states list")
    registry = _slice_registry(registry_path)
    declared_slice_count = evaluation_manifest.get("slice_count")
    if declared_slice_count is not None and int(declared_slice_count) != len(registry):
        raise ValueError("Evaluation manifest and frozen slice registry disagree on slice count")
    declared_probes = evaluation_manifest.get("probes_per_state")
    actual_probes = sum(int(item["probe_count"]) for item in registry)
    if declared_probes is not None and int(declared_probes) != actual_probes:
        raise ValueError("Evaluation manifest and frozen slice registry disagree on probe count")

    # Validate every state and baseline before creating the output directory.  A
    # failed run therefore leaves no misleading partial aggregate behind.
    state_records: list[dict[str, Any]] = []
    state_audits: list[dict[str, Any]] = []
    state_rows: list[tuple[dict[str, Any], list[dict[str, str]]]] = []
    for state in states:
        record, audit, rows = _assemble_state(
            state=state,
            registry=registry,
            output_dir=output_dir,
        )
        state_records.append(record)
        state_audits.append(audit)
        state_rows.append((record, rows))

    baseline_states = []
    for baseline in evaluation_manifest.get("baseline_states", []):
        path = Path(str(baseline["path"])).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Missing baseline state: {path}")
        declared_hash = str(baseline.get("sha256", "")).strip()
        actual_hash = sha256_file(path)
        if declared_hash and declared_hash != actual_hash:
            raise ValueError(f"Baseline state hash mismatch: {path}")
        baseline_states.append({**baseline, "path": str(path), "sha256": actual_hash})

    output_dir.mkdir(parents=True)
    for record, rows in state_rows:
        write_csv(Path(str(record["path"])), rows)
        record["sha256"] = sha256_file(Path(str(record["path"])))

    results_manifest = {
        "status": "assembled_complete",
        "analysis": "qwen_m2_m3_matched_subject_bootstrap_v1",
        "source_evaluation_manifest": str(evaluation_manifest_path),
        "source_evaluation_manifest_sha256": sha256_file(evaluation_manifest_path),
        "slice_registry": str(registry_path),
        "slice_registry_sha256": sha256_file(registry_path),
        "states": baseline_states + state_records,
        "baseline_states": baseline_states,
        "evaluated_states": state_records,
        "slice_count": len(registry),
        "probes_per_state": actual_probes,
        "bootstrap_samples": int(evaluation_manifest.get("analysis_bootstrap_samples", 2000)),
        "bootstrap_seed": int(evaluation_manifest.get("analysis_bootstrap_seed", 20260717)),
        "integrity_status": "passed",
    }
    write_json(output_dir / "results_manifest.json", results_manifest)
    write_json(
        output_dir / "assembly_manifest.json",
        {
            "status": "completed",
            "results_manifest": str((output_dir / "results_manifest.json").resolve()),
            "results_manifest_sha256": sha256_file(output_dir / "results_manifest.json"),
            "state_count": len(state_records),
            "slice_count_per_state": len(registry),
            "probes_per_state": actual_probes,
            "states": state_audits,
            "retention_policy": "retain_state_level_csvs_and_compact_analysis; source_slice_evidence_remains_on_scratch",
        },
    )

    print(output_dir / "results_manifest.json")


if __name__ == "__main__":
    main()
