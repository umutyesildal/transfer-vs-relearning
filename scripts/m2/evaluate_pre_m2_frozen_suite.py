#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.evaluation.pre_m2_followup import PreM2FrozenEvaluator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run WP1A, WP2, and applicable WP4 probes for one frozen model.")
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--model-manifest", type=Path, required=True)
    parser.add_argument("--dataset-dir", type=Path, default=Path("artifacts/datasets/relation_v2_gate_v1"))
    parser.add_argument(
        "--probe-registry",
        type=Path,
        default=Path("artifacts/pre_m2_followup_v1/evaluations/paraphrase_probe_registry.csv"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--candidate-batch-size", type=int, default=64)
    parser.add_argument("--checkpoint-interval", type=int, default=25)
    parser.add_argument("--probe-limit", type=int, default=None)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--no-bf16", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    output_dir = PreM2FrozenEvaluator(
        model_label=args.model_label,
        model_manifest=args.model_manifest,
        dataset_dir=args.dataset_dir,
        probe_registry=args.probe_registry,
        output_dir=args.output_dir,
        candidate_batch_size=args.candidate_batch_size,
        checkpoint_interval=args.checkpoint_interval,
        probe_limit=args.probe_limit,
        device=args.device,
        bf16=not args.no_bf16,
    ).run(resume=args.resume)
    print(output_dir)


if __name__ == "__main__":
    main()
