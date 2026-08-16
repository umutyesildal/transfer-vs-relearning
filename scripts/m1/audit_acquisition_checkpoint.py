#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.metrics.acquisition_audit import audit_acquisition_checkpoint


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exact", type=Path, required=True)
    parser.add_argument("--direct", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--train", type=Path)
    parser.add_argument("--validation", type=Path)
    args = parser.parse_args()
    summary = audit_acquisition_checkpoint(
        args.exact,
        args.direct,
        args.qa,
        args.output_dir,
        train_path=args.train,
        validation_path=args.validation,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
