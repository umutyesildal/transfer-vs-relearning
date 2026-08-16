from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.data.relation_v2_binding_control import build_relation_v2_binding_control


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("artifacts/datasets/relation_v2_gate_v1"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/datasets/relation_v2_binding_control_v1"),
    )
    args = parser.parse_args()
    manifest = build_relation_v2_binding_control(args.source_dir, args.output_dir)
    print(
        f"version={manifest['version']} rows={manifest['contract']['train_rows']} "
        f"changed={manifest['contract']['changed_rows']}"
    )


if __name__ == "__main__":
    main()
