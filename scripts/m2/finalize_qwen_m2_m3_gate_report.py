#!/usr/bin/env python3
"""Apply the frozen Qwen M2/M3 endpoint gates to an analysis output package."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.utils.io import sha256_file, write_json


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.resolve().read_text(encoding="utf-8"))


def _csv(path: Path) -> list[dict[str, str]]:
    with path.resolve().open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _single(rows: list[dict[str, str]], **filters: str) -> dict[str, str]:
    matches = [row for row in rows if all(str(row.get(key)) == value for key, value in filters.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one row for {filters}, found {len(matches)}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--results-manifest", type=Path, required=True)
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    contract_path = args.contract.resolve()
    results_manifest_path = args.results_manifest.resolve()
    analysis_dir = args.analysis_dir.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite gate report: {output_dir}")

    contract = _json(contract_path)
    results_manifest = _json(results_manifest_path)
    analysis_manifest = _json(analysis_dir / "analysis_manifest.json")
    integrity = _json(analysis_dir / "integrity_summary.json")
    interaction_rows = _csv(analysis_dir / "branch_interactions.csv")
    contrast_rows = _csv(analysis_dir / "paired_state_contrasts.csv")

    required_states = {"m1_seed42", "m1_seed43", "m2_clean_seed42", "m2_clean_seed43", "m3_fact_seed42", "m3_fact_seed43"}
    actual_states = {str(item["state_id"]) for item in results_manifest.get("states", [])}
    state_package_pass = actual_states == required_states
    integrity_pass = (
        integrity.get("status") == "passed"
        and int(integrity.get("probe_count_per_state", 0)) == 60000
        and int(integrity.get("state_count", 0)) == 6
        and state_package_pass
        and analysis_manifest.get("status") == "completed"
    )

    primary_rows = [
        row
        for row in interaction_rows
        if row.get("dimension") == "direction" and row.get("key") == "tr_to_en"
    ]
    if {row.get("seed") for row in primary_rows} != {"42", "43"}:
        raise ValueError("Primary interaction output must contain exactly both seeds")
    primary_by_seed = {
        row["seed"]: {
            "observed": float(row["difference_b_minus_a"]),
            "ci_low": float(row["bootstrap_ci_low"]),
            "ci_high": float(row["bootstrap_ci_high"]),
            "n_subjects_a": int(row["n_subjects_a"]),
            "n_subjects_b": int(row["n_subjects_b"]),
            "bootstrap_samples": int(row["bootstrap_samples"]),
        }
        for row in primary_rows
    }
    primary_pass = all(item["observed"] > 0 and item["ci_low"] > 0 for item in primary_by_seed.values())

    retention_rows: dict[str, dict[str, float]] = {}
    for seed in ("42", "43"):
        for comparison in ("m2_minus_m1", "m3_minus_m1"):
            row = _single(
                contrast_rows,
                seed=seed,
                dimension="direction",
                key="en_to_en",
                comparison=comparison,
            )
            retention_rows[f"seed{seed}_{comparison}"] = {
                "difference_first_minus_second": float(row["difference_first_minus_second"]),
                "bootstrap_ci_low": float(row["bootstrap_ci_low"]),
                "bootstrap_ci_high": float(row["bootstrap_ci_high"]),
            }
    retention_limit = -0.05
    retention_pass = all(
        item["difference_first_minus_second"] >= retention_limit
        for item in retention_rows.values()
    )

    checks = {
        "operational_validity": {
            "status": "passed" if integrity_pass else "failed",
            "required_states": sorted(required_states),
            "actual_states": sorted(actual_states),
            "analysis_manifest_status": analysis_manifest.get("status"),
            "integrity_summary_status": integrity.get("status"),
            "probe_count_per_state": integrity.get("probe_count_per_state"),
        },
        "primary_interaction": {
            "status": "passed" if primary_pass else "failed",
            "estimand": "(M3_fact-M2_clean)_B-(M3_fact-M2_clean)_A",
            "metric": "tr_to_en_top1",
            "criterion": "observed > 0 and 95% bootstrap CI lower bound > 0 for both seeds",
            "by_seed": primary_by_seed,
        },
        "english_retention_guardrail": {
            "status": "passed" if retention_pass else "failed",
            "criterion": "M2/M3 EN-to-EN top-1 difference relative to M1 >= -0.05",
            "limit": retention_limit,
            "by_seed_and_arm": retention_rows,
        },
    }
    if not integrity_pass:
        decision = "invalid_incomplete_or_integrity_failure"
    elif not primary_pass:
        decision = "primary_success_criterion_not_met"
    elif not retention_pass:
        decision = "retention_guardrail_violation"
    else:
        decision = "primary_success_with_retention_guardrail"

    report = {
        "status": "completed",
        "decision": decision,
        "contract": str(contract_path),
        "contract_sha256": sha256_file(contract_path),
        "results_manifest": str(results_manifest_path),
        "results_manifest_sha256": sha256_file(results_manifest_path),
        "analysis_dir": str(analysis_dir),
        "analysis_manifest_sha256": sha256_file(analysis_dir / "analysis_manifest.json"),
        "bootstrap_samples": int(contract["primary_estimand"]["bootstrap_samples"]),
        "bootstrap_seed": int(contract["primary_estimand"]["bootstrap_seed"]),
        "checks": checks,
        "interpretation": "Gate application only; no post-hoc threshold, checkpoint, or seed selection was performed.",
    }
    output_dir.mkdir(parents=True)
    write_json(output_dir / "final_gate_report.json", report)
    markdown = [
        "# Qwen M2/M3 Final Gate Report",
        "",
        f"- Decision: **{decision}**",
        f"- Operational validity: **{checks['operational_validity']['status']}**",
        f"- Primary interaction: **{checks['primary_interaction']['status']}**",
        f"- EN→EN retention guardrail: **{checks['english_retention_guardrail']['status']}**",
        "",
        "This report applies the frozen contract rules and does not select checkpoints, thresholds, or seeds after seeing results.",
    ]
    (output_dir / "final_gate_report.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    print(output_dir / "final_gate_report.json")


if __name__ == "__main__":
    main()
