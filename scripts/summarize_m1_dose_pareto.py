#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    CHECKPOINT_STEPS,
    LABELS,
    load_registry,
)
from transfer_vs_relearning.utils.io import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    registry = load_registry(args.registry.resolve())
    root = Path(registry["scratch_root"])
    rows: list[dict[str, object]] = []
    nominees: list[dict[str, object]] = []
    for label in LABELS:
        model_rows: list[dict[str, object]] = []
        for step in CHECKPOINT_STEPS:
            checkpoint_root = root / "evaluations" / label / f"checkpoint-{step}"
            cheap_path = checkpoint_root / "cheap_gate.json"
            if not cheap_path.is_file():
                raise FileNotFoundError(cheap_path)
            cheap = json.loads(cheap_path.read_text(encoding="utf-8"))
            final_path = checkpoint_root / "final_gate.json"
            if cheap["hard_stage_open"] and not final_path.is_file():
                raise FileNotFoundError(final_path)
            final = json.loads(final_path.read_text(encoding="utf-8")) if final_path.is_file() else {}
            row = {
                "label": label,
                "step": step,
                "exact_accuracy": cheap["exact_accuracy"],
                "ppl_ratio": cheap["ppl_ratio"],
                "integrity_pass": cheap["integrity_pass"],
                "hard_stage_open": cheap["hard_stage_open"],
                "all_gates_pass": bool(final.get("all_gates_pass", False)),
                "min_cell_accuracy": final.get("min_cell_accuracy"),
                "min_heldout_cd_accuracy": final.get("min_heldout_cd_accuracy"),
                "global_robust_intersection": final.get("global_robust_intersection"),
                "min_robust_intersection": final.get("min_robust_intersection"),
                "cheap_gate_sha256": sha256_file(cheap_path),
                "final_gate_sha256": sha256_file(final_path) if final_path.is_file() else None,
            }
            rows.append(row)
            model_rows.append(row)
        passing = [row for row in model_rows if row["all_gates_pass"]]
        if passing:
            nominees.append(min(passing, key=lambda row: int(row["step"])))
    selected = None
    if nominees:
        selected = min(
            nominees,
            key=lambda row: (
                -float(row["global_robust_intersection"]),
                -float(row["min_robust_intersection"]),
                -float(row["min_heldout_cd_accuracy"]),
                float(row["ppl_ratio"]),
                LABELS.index(str(row["label"])),
            ),
        )
    args.output_root.mkdir(parents=True, exist_ok=False)
    fieldnames = list(rows[0])
    with (args.output_root / "checkpoint_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    write_json(args.output_root / "summary.json", {
        "status": "COMPLETE",
        "checkpoint_count": len(rows),
        "model_nominees": nominees,
        "selected_remediation_nominee": selected,
        "automatic_primary_promotion": False,
        "seed43_required_for_promotion": bool(selected),
        "next_action": "freeze_seed43_replication_contract" if selected else "consider_separate_lr_ladder_contract",
    })
    print(args.output_root / "summary.json")


if __name__ == "__main__":
    main()
