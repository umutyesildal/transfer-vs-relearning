#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.evaluation.turkish_bridge import TurkishBridgeEvaluator


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate EN->EN, TR->EN, and TR->TR bridge access.")
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--model-manifest", type=Path, required=True)
    parser.add_argument("--dataset-dir", type=Path, default=Path("artifacts/datasets/relation_v2_gate_v1"))
    parser.add_argument("--probe-registry", type=Path, default=Path("artifacts/turkish_bridge_v1/bridge_probe_registry.csv"))
    parser.add_argument("--eligible-facts", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--candidate-batch-size", type=int, default=64)
    parser.add_argument("--checkpoint-interval", type=int, default=25)
    parser.add_argument("--probe-limit", type=int)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--no-bf16", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    result = TurkishBridgeEvaluator(
        model_label=args.model_label,
        model_manifest=args.model_manifest,
        dataset_dir=args.dataset_dir,
        probe_registry=args.probe_registry,
        output_dir=args.output_dir,
        eligible_facts=args.eligible_facts,
        candidate_batch_size=args.candidate_batch_size,
        checkpoint_interval=args.checkpoint_interval,
        device=args.device,
        bf16=not args.no_bf16,
    ).run(resume=args.resume, probe_limit=args.probe_limit)
    print(result)


if __name__ == "__main__":
    main()
