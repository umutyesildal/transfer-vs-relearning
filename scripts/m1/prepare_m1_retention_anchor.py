#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import unicodedata
from pathlib import Path
from typing import Any


DATASET_ID = "Salesforce/wikitext"
DATASET_CONFIG = "wikitext-2-raw-v1"
DATASET_REVISION = "main"


def _normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(value.split())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_surfaces(path: Path, count: int) -> tuple[list[str], list[str]]:
    subjects: list[str] = []
    seen_subjects: set[str] = set()
    answers: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            subject = str(row["subject"])
            if subject not in seen_subjects:
                seen_subjects.add(subject)
                subjects.append(subject)
            answers.add(str(row["answer"]))
    if len(subjects) != count:
        raise ValueError(f"Expected {count} subjects, found {len(subjects)}")
    return subjects, sorted(answers)


def _candidate_rows(
    split: Any,
    *,
    source_split: str,
    subjects: list[str],
    answers: list[str],
) -> tuple[list[dict[str, Any]], int, int]:
    normalized_subjects = [_normalized(value) for value in subjects]
    normalized_answers = [_normalized(value) for value in answers]
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    subject_hits = 0
    answer_hits = 0
    for source_index, raw_text in enumerate(split["text"]):
        text = " ".join(str(raw_text).split())
        normalized = _normalized(text)
        if not normalized or re.fullmatch(r"=+\s*[^=]+\s*=+", normalized):
            continue
        if normalized in seen:
            continue
        if any(subject in normalized for subject in normalized_subjects):
            subject_hits += 1
            continue
        row_answer_hits = sum(answer in normalized for answer in normalized_answers if answer)
        answer_hits += row_answer_hits
        seen.add(normalized)
        rows.append(
            {
                "document_id": f"wikitext2_{source_split}_{source_index:06d}",
                "source_split": source_split,
                "source_index": source_index,
                "text": text,
                "answer_label_surface_hits": row_answer_hits,
            }
        )
    return rows, subject_hits, answer_hits


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-manifest", type=Path, required=True)
    parser.add_argument("--factual-train-file", type=Path, required=True)
    parser.add_argument("--subject-count", type=int, default=100)
    parser.add_argument("--train-rows", type=int, default=3500)
    parser.add_argument("--validation-rows", type=int, default=500)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite anchor directory: {args.output_dir}")
    args.output_dir.mkdir(parents=True)

    from datasets import load_dataset
    from transformers import AutoTokenizer

    model_manifest = json.loads(args.model_manifest.read_text(encoding="utf-8"))
    tokenizer_path = Path(
        model_manifest.get("tokenizer_source_path_absolute")
        or model_manifest["local_path_absolute"]
    )
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True, use_fast=True)
    subjects, answers = _load_surfaces(args.factual_train_file, args.subject_count)

    source = load_dataset(DATASET_ID, DATASET_CONFIG, revision=DATASET_REVISION)
    selected: dict[str, list[dict[str, Any]]] = {}
    audits: dict[str, dict[str, int]] = {}
    for split_name, row_count in (("train", args.train_rows), ("validation", args.validation_rows)):
        candidates, subject_hits, answer_hits = _candidate_rows(
            source[split_name],
            source_split=split_name,
            subjects=subjects,
            answers=answers,
        )
        rng = random.Random(args.seed)
        rng.shuffle(candidates)
        if len(candidates) < row_count:
            raise ValueError(
                f"Not enough clean {split_name} anchors: {len(candidates)} < {row_count}"
            )
        rows = candidates[:row_count]
        token_total = 0
        for row in rows:
            token_ids = tokenizer(
                row["text"],
                add_special_tokens=False,
                truncation=True,
                max_length=args.max_tokens,
            )["input_ids"]
            if not token_ids:
                raise ValueError(f"Selected empty-token anchor: {row['document_id']}")
            row["supervised_tokens_with_eos"] = len(token_ids) + 1
            token_total += len(token_ids) + 1
        selected[split_name] = rows
        audits[split_name] = {
            "source_candidates_after_filtering": len(candidates),
            "excluded_subject_surface_rows": subject_hits,
            "candidate_answer_label_surface_hits": answer_hits,
            "selected_rows": len(rows),
            "selected_answer_label_surface_hits": sum(
                int(row["answer_label_surface_hits"]) for row in rows
            ),
            "supervised_tokens_with_eos": token_total,
        }

    train_path = args.output_dir / "train.jsonl"
    validation_path = args.output_dir / "validation.jsonl"
    _write_jsonl(train_path, selected["train"])
    _write_jsonl(validation_path, selected["validation"])
    manifest = {
        "version": "m1_retention_anchor_v1",
        "source": {
            "dataset_id": DATASET_ID,
            "dataset_config": DATASET_CONFIG,
            "requested_revision": DATASET_REVISION,
            "training_split": "train",
            "validation_split": "validation",
            "forbidden_ppl_split": "test",
        },
        "selection": {
            "seed": args.seed,
            "subject_count": args.subject_count,
            "max_tokens_before_eos": args.max_tokens,
            "factual_train_file": str(args.factual_train_file.resolve()),
            "factual_train_file_sha256": _sha256(args.factual_train_file),
            "zero_selected_subject_surface_occurrences": True,
        },
        "tokenizer": {
            "path": str(tokenizer_path.resolve()),
            "model_manifest": str(args.model_manifest.resolve()),
            "model_manifest_sha256": _sha256(args.model_manifest),
        },
        "audit": audits,
        "files": {
            "train": {"path": str(train_path), "sha256": _sha256(train_path)},
            "validation": {"path": str(validation_path), "sha256": _sha256(validation_path)},
        },
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "manifest": str(manifest_path), "audit": audits}, sort_keys=True))


if __name__ == "__main__":
    main()
