#!/usr/bin/env python3
"""Create explicitly exploratory diagnostics from the frozen Qwen M2/M3 aggregates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


INPUT_FILES = (
    "state_accuracy.csv",
    "paired_state_contrasts.csv",
    "branch_interactions.csv",
    "robust_state_accuracy.csv",
    "robust_paired_contrasts.csv",
    "analysis_manifest.json",
    "integrity_summary.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def float_value(row: dict[str, str], key: str) -> float:
    return float(row[key])


def git_commit(repo_root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build post-hoc exploratory Qwen M2/M3 diagnostics from frozen aggregates."
    )
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    analysis_dir = args.analysis_dir.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite exploratory output: {output_dir}")

    missing = [name for name in INPUT_FILES if not (analysis_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing frozen analysis inputs: {', '.join(missing)}")

    state_rows = read_csv(analysis_dir / "state_accuracy.csv")
    paired_rows = read_csv(analysis_dir / "paired_state_contrasts.csv")
    interaction_rows = read_csv(analysis_dir / "branch_interactions.csv")
    robust_state_rows = read_csv(analysis_dir / "robust_state_accuracy.csv")
    robust_paired_rows = read_csv(analysis_dir / "robust_paired_contrasts.csv")

    output_dir.mkdir(parents=True)

    # Keep the complete, dimension-rich descriptive state package in a new immutable namespace.
    write_csv(output_dir / "state_accuracy_exploratory.csv", state_rows, list(state_rows[0]))
    write_csv(output_dir / "paired_contrasts_exploratory.csv", paired_rows, list(paired_rows[0]))
    write_csv(
        output_dir / "branch_interactions_exploratory.csv",
        interaction_rows,
        list(interaction_rows[0]),
    )
    write_csv(
        output_dir / "robust_state_accuracy_exploratory.csv",
        robust_state_rows,
        list(robust_state_rows[0]),
    )
    write_csv(
        output_dir / "robust_paired_contrasts_exploratory.csv",
        robust_paired_rows,
        list(robust_paired_rows[0]),
    )

    # Seed contrast for every available Branch A/B interaction cell.
    interactions_by_cell: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in interaction_rows:
        cell = (row["dimension"], row["key"], row["estimand"])
        interactions_by_cell[cell][row["seed"]] = row
    seed_rows: list[dict[str, Any]] = []
    for (dimension, key, estimand), by_seed in sorted(interactions_by_cell.items()):
        if "42" not in by_seed or "43" not in by_seed:
            continue
        seed42 = by_seed["42"]
        seed43 = by_seed["43"]
        seed_rows.append(
            {
                "dimension": dimension,
                "key": key,
                "estimand": estimand,
                "seed42_interaction": float_value(seed42, "difference_b_minus_a"),
                "seed43_interaction": float_value(seed43, "difference_b_minus_a"),
                "seed43_minus_seed42": float_value(seed43, "difference_b_minus_a")
                - float_value(seed42, "difference_b_minus_a"),
                "seed42_ci_low": float_value(seed42, "bootstrap_ci_low"),
                "seed42_ci_high": float_value(seed42, "bootstrap_ci_high"),
                "seed43_ci_low": float_value(seed43, "bootstrap_ci_low"),
                "seed43_ci_high": float_value(seed43, "bootstrap_ci_high"),
            }
        )
    write_csv(
        output_dir / "seed_interaction_comparison.csv",
        seed_rows,
        list(seed_rows[0]),
    )

    # Localize the M1-to-M2 decline and the descriptive M3 recovery by direction/form/scaffold.
    decline_rows = [
        row
        for row in paired_rows
        if row["comparison"] in {"m2_minus_m1", "m3_minus_m2"}
        and (
            row["dimension"] in {"direction", "direction_relation", "direction_form", "direction_scaffold"}
            or row["key"] in {"tr_to_en", "tr_to_tr"}
        )
    ]
    write_csv(output_dir / "turkish_decline_and_recovery.csv", decline_rows, list(decline_rows[0]))

    decline_candidates = [
        row
        for row in paired_rows
        if row["comparison"] == "m2_minus_m1"
        and row["key"].startswith(("tr_to_en", "tr_to_tr"))
    ]
    decline_candidates.sort(key=lambda row: float_value(row, "difference_first_minus_second"))
    recovery_candidates = [
        row
        for row in paired_rows
        if row["comparison"] == "m3_minus_m2"
        and row["key"].startswith(("tr_to_en", "tr_to_tr"))
    ]
    recovery_candidates.sort(
        key=lambda row: float_value(row, "difference_first_minus_second"), reverse=True
    )

    report_lines = [
        "# Exploratory Qwen M2/M3 Mechanism Analysis",
        "",
        "**Status:** Exploratory/post-hoc only; the frozen primary gate is unchanged.",
        "",
        f"**Source analysis directory:** `{analysis_dir}`",
        f"**Source repository commit:** `{git_commit(args.repo_root.resolve())}`",
        "",
        "## Scope",
        "",
        "This report compares seeds, relations, directions, forms, scaffolds, and Branch A/B "
        "changes using only the frozen aggregate outputs. It does not select checkpoints, "
        "change thresholds, redefine the estimand, or authorize new training.",
        "",
        "## Frozen primary boundary",
        "",
        "The frozen decision remains `primary_success_criterion_not_met`. Any pattern below is "
        "descriptive and must not be promoted to confirmatory evidence.",
        "",
        "## Largest M1-to-M2 Turkish declines",
        "",
        "Values are percentage-point changes; this ranking is descriptive.",
        "",
        "| Seed | Dimension | Cell | Change | 95% CI |",
        "|---:|---|---|---:|---:|",
    ]
    for row in decline_candidates[:20]:
        report_lines.append(
            f"| {row['seed']} | {row['dimension']} | {row['key']} | "
            f"{100 * float_value(row, 'difference_first_minus_second'):.2f} | "
            f"[{100 * float_value(row, 'bootstrap_ci_low'):.2f}, "
            f"{100 * float_value(row, 'bootstrap_ci_high'):.2f}] |"
        )
    report_lines.extend(
        [
            "",
            "## Largest descriptive M3 recovery over M2-clean",
            "",
            "| Seed | Dimension | Cell | Recovery | 95% CI |",
            "|---:|---|---|---:|---:|",
        ]
    )
    for row in recovery_candidates[:20]:
        report_lines.append(
            f"| {row['seed']} | {row['dimension']} | {row['key']} | "
            f"{100 * float_value(row, 'difference_first_minus_second'):.2f} | "
            f"[{100 * float_value(row, 'bootstrap_ci_low'):.2f}, "
            f"{100 * float_value(row, 'bootstrap_ci_high'):.2f}] |"
        )
    report_lines.extend(
        [
            "",
            "## Seed interaction comparison",
            "",
            "The complete cell-level comparison is in `seed_interaction_comparison.csv`; positive "
            "values indicate a larger descriptive interaction for seed 43 than seed 42.",
        ]
    )
    (output_dir / "exploratory_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "analysis": "qwen_m2_m3_exploratory_mechanism_v1",
        "status": "completed",
        "interpretation": "exploratory_posthoc_only",
        "source_analysis_dir": str(analysis_dir),
        "source_repository_commit": git_commit(args.repo_root.resolve()),
        "input_files": {name: sha256_file(analysis_dir / name) for name in INPUT_FILES},
        "outputs": {},
        "questions": [
            "seed_42_vs_seed_43_interaction",
            "relation_contribution",
            "form_and_scaffold_differences",
            "branch_a_vs_branch_b_changes",
            "m1_to_m2_turkish_decline_and_m3_recovery",
        ],
    }
    for path in sorted(output_dir.iterdir()):
        if path.name == "exploratory_manifest.json":
            continue
        manifest["outputs"][path.name] = sha256_file(path)
    (output_dir / "exploratory_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
