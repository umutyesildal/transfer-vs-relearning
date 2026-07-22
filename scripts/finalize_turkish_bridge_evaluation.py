#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from transfer_vs_relearning.evaluation.turkish_bridge_analysis import classify_bridge
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_json


STATES = ("m0", "m1", "low", "full")


def _true(value: Any) -> bool:
    return str(value).casefold() in {"1", "true", "yes"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize all frozen bridge strata for one model family.")
    parser.add_argument("--model-label", choices=("qwen", "smollm2"), required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--contract-root", type=Path, required=True)
    parser.add_argument("--experiment-config", type=Path, required=True)
    args = parser.parse_args()
    root, contract = args.evaluation_root.resolve(), args.contract_root.resolve()
    output = root / "results" / args.model_label
    decision_path = output / "classification_by_stratum.json"
    if decision_path.exists():
        raise FileExistsError(decision_path)
    state_rows: dict[str, list[dict[str, Any]]] = {}
    ppl_states: dict[str, dict[str, float]] = {}
    inputs: dict[str, Any] = {}
    for state in STATES:
        bridge_path = output / state / "bridge/per_probe_results.csv"
        ppl_path = output / state / "ppl/summary.json"
        state_rows[state] = read_csv_rows(bridge_path)
        ppl = json.loads(ppl_path.read_text(encoding="utf-8"))
        if ppl.get("status") != "completed":
            raise ValueError(f"Incomplete PPL state: {args.model_label}/{state}")
        ppl_states[state] = {
            "english_ppl": float(ppl["corpora"]["english"]["perplexity"]),
            "turkish_ppl": float(ppl["corpora"]["turkish"]["perplexity"]),
        }
        inputs[state] = {
            "bridge": {"path": str(bridge_path), "sha256": sha256_file(bridge_path)},
            "ppl": {"path": str(ppl_path), "sha256": sha256_file(ppl_path)},
        }
    all_facts = {str(row["fact_id"]) for row in state_rows["m1"]}
    model_rows = read_csv_rows(contract / f"eligibility/{args.model_label}.csv")
    shared_eligible_rows = read_csv_rows(contract / "eligibility/shared_eligible_intersection.csv")
    shared_strict_rows = read_csv_rows(contract / "eligibility/shared_strict_intersection.csv")
    strata = {
        "all_facts": all_facts,
        "model_eligible": {str(row["fact_id"]) for row in model_rows if _true(row.get("eligible_3_of_4_heldout"))},
        "model_strict": {str(row["fact_id"]) for row in model_rows if _true(row.get("strict_8_of_8"))},
        "shared_eligible": {str(row["fact_id"]) for row in shared_eligible_rows if _true(row.get("shared_eligible"))},
        "shared_strict": {str(row["fact_id"]) for row in shared_strict_rows if _true(row.get("shared_strict"))},
    }
    config = yaml.safe_load(args.experiment_config.resolve().read_text(encoding="utf-8"))
    results = {}
    for stratum, fact_ids in strata.items():
        filtered = {
            state: [row for row in rows if str(row["fact_id"]) in fact_ids]
            for state, rows in state_rows.items()
        }
        if any({str(row["fact_id"]) for row in rows} != fact_ids for rows in filtered.values()):
            raise ValueError(f"State fact mismatch in {stratum}")
        result = classify_bridge(
            state_rows=filtered,
            ppl_states=ppl_states,
            rule=config["promotion_rule"],
            bootstrap_samples=int(config["evaluation"]["bootstrap_samples"]),
            bootstrap_seed=int(config["evaluation"]["bootstrap_seed"]),
        )
        result["fact_count"] = len(fact_ids)
        results[stratum] = result
    payload = {
        "status": "completed",
        "model_label": args.model_label,
        "primary_stratum": "model_eligible",
        "primary_classification": results["model_eligible"]["classification"],
        "primary_all_gates_pass": results["model_eligible"]["all_gates_pass"],
        "strata": results,
        "ppl_states": ppl_states,
        "english_ppl_ratios_to_m0": {
            state: ppl_states[state]["english_ppl"] / ppl_states["m0"]["english_ppl"] for state in STATES
        },
        "inputs": inputs,
        "experiment_config": str(args.experiment_config.resolve()),
        "experiment_config_sha256": sha256_file(args.experiment_config.resolve()),
    }
    write_json(output / "ppl_metrics.json", {"states": ppl_states, "inputs": inputs})
    write_json(decision_path, payload)
    print(decision_path)


if __name__ == "__main__":
    main()
