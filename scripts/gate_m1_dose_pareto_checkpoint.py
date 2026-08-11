#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.experiments.m1_dose_pareto import (
    cheap_gate,
    final_gate,
    load_registry,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--label", choices=("olmo", "falcon", "pythia"), required=True)
    parser.add_argument("--step", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--exact-summary", type=Path)
    parser.add_argument("--general-summary", type=Path)
    parser.add_argument("--cheap-gate", type=Path)
    parser.add_argument("--hard-csv", type=Path)
    args = parser.parse_args()
    registry = load_registry(args.registry.resolve())
    if args.cheap_gate or args.hard_csv:
        if not args.cheap_gate or not args.hard_csv:
            parser.error("final mode requires --cheap-gate and --hard-csv")
        payload = final_gate(registry, args.label, args.step, args.cheap_gate, args.hard_csv, args.output)
    else:
        if not args.exact_summary or not args.general_summary:
            parser.error("cheap mode requires --exact-summary and --general-summary")
        payload = cheap_gate(registry, args.label, args.step, args.exact_summary, args.general_summary, args.output)
    print(payload["status"])


if __name__ == "__main__":
    main()
