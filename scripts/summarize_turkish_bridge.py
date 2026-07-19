#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from transfer_vs_relearning.evaluation.turkish_bridge_analysis import classify_bridge
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply the frozen Document 109 bridge promotion rule.")
    parser.add_argument("--experiment-config", type=Path, default=Path("configs/experiments/turkish_bridge_v1.yaml"))
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--m0", type=Path, required=True)
    parser.add_argument("--m1", type=Path, required=True)
    parser.add_argument("--low", type=Path, required=True)
    parser.add_argument("--full", type=Path, required=True)
    parser.add_argument("--ppl-metrics", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.experiment_config.read_text(encoding="utf-8"))
    paths = {state: path.resolve() for state, path in {"m0": args.m0, "m1": args.m1, "low": args.low, "full": args.full}.items()}
    ppl_path = args.ppl_metrics.resolve()
    ppl_payload = json.loads(ppl_path.read_text(encoding="utf-8"))
    result = classify_bridge(
        state_rows={state: read_csv_rows(path) for state, path in paths.items()},
        ppl_states=ppl_payload["states"],
        rule=config["promotion_rule"],
        bootstrap_samples=int(config["evaluation"]["bootstrap_samples"]),
        bootstrap_seed=int(config["evaluation"]["bootstrap_seed"]),
    )
    result.update({
        "model_label": args.model_label,
        "experiment_config": str(args.experiment_config.resolve()),
        "experiment_config_sha256": sha256_file(args.experiment_config.resolve()),
        "inputs": {state: {"path": str(path), "sha256": sha256_file(path)} for state, path in paths.items()},
        "ppl_metrics": {"path": str(ppl_path), "sha256": sha256_file(ppl_path)},
    })
    write_json(args.output.resolve(), result)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
