#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from transfer_vs_relearning.utils.io import sha256_file, write_json


DATASET_ID = "Salesforce/wikitext"
DATASET_CONFIG = "wikitext-2-raw-v1"
DATASET_SPLIT = "test"
DATASET_REVISION = "00aa25585682d4957f9e86edc73f59be7419af99"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/evaluation/general_capability_v1"),
    )
    args = parser.parse_args()

    from datasets import load_dataset

    dataset = load_dataset(
        DATASET_ID,
        DATASET_CONFIG,
        split=DATASET_SPLIT,
        revision=DATASET_REVISION,
    )
    rows = [str(row["text"]) for row in dataset if str(row.get("text", "")).strip()]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = args.output_dir / "wikitext2_raw_test.jsonl"
    with corpus_path.open("w", encoding="utf-8") as handle:
        for index, text in enumerate(rows):
            handle.write(json.dumps({"document_id": f"wikitext2_test_{index:05d}", "text": text}, ensure_ascii=False))
            handle.write("\n")
    manifest = {
        "dataset_id": DATASET_ID,
        "dataset_config": DATASET_CONFIG,
        "dataset_split": DATASET_SPLIT,
        "dataset_revision": DATASET_REVISION,
        "nonempty_document_count": len(rows),
        "corpus_file": str(corpus_path.resolve()),
        "corpus_sha256": sha256_file(corpus_path),
    }
    write_json(args.output_dir / "manifest.json", manifest)
    print(corpus_path.resolve())
    print(manifest)


if __name__ == "__main__":
    main()

