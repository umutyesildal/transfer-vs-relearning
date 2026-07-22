#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.evaluation.general_capability import (
    _git_commit,
    _load_model,
    _score_full_blocks,
    _tokenize_corpus,
    bootstrap_weighted_nll_interval,
    split_token_ids,
)
from transfer_vs_relearning.utils.io import read_jsonl, sha256_file, sha256_text, write_csv, write_json


def _parse_corpus(value: str) -> tuple[str, Path]:
    label, separator, raw_path = value.partition("=")
    if not separator or not label or not raw_path:
        raise argparse.ArgumentTypeError("corpus must use LABEL=/absolute/path.jsonl")
    if not label.replace("_", "").isalnum():
        raise argparse.ArgumentTypeError(f"invalid corpus label: {label!r}")
    return label, Path(raw_path)


def _score_one(
    *, tokenizer: Any, model: Any, device: str, corpus_path: Path, output_dir: Path,
    block_size: int, batch_size: int, bootstrap_samples: int, seed: int,
) -> dict[str, Any]:
    corpus_path = corpus_path.resolve()
    if not corpus_path.is_file():
        raise FileNotFoundError(corpus_path)
    documents = [str(row["text"]) for row in read_jsonl(corpus_path) if str(row.get("text", "")).strip()]
    token_ids = _tokenize_corpus(tokenizer, documents)
    blocks = split_token_ids(token_ids, block_size)
    rows = _score_full_blocks(model, device, blocks, batch_size)
    output_dir.mkdir(parents=True, exist_ok=False)
    write_csv(output_dir / "loss_blocks.csv", rows)
    total_nll = sum(float(row["nll_sum"]) for row in rows)
    total_tokens = sum(int(row["token_count"]) for row in rows)
    mean_nll = total_nll / total_tokens
    ci_low, ci_high = bootstrap_weighted_nll_interval(rows, samples=bootstrap_samples, seed=seed)
    payload = {
        "status": "completed",
        "corpus_file": str(corpus_path),
        "corpus_sha256": sha256_file(corpus_path),
        "document_count": len(documents),
        "block_count": len(rows),
        "input_token_count": len(token_ids),
        "scored_token_count": total_tokens,
        "token_ids_sha256": sha256_text(json.dumps(token_ids, separators=(",", ":"))),
        "mean_token_nll": mean_nll,
        "mean_token_nll_ci95": [ci_low, ci_high],
        "perplexity": math.exp(mean_nll),
        "perplexity_ci95_from_nll": [math.exp(ci_low), math.exp(ci_high)],
    }
    write_json(output_dir / "summary.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Score one or more frozen JSONL corpora with one model load.")
    parser.add_argument("--model-manifest", type=Path, required=True)
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--corpus", action="append", type=_parse_corpus, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--no-bf16", action="store_true")
    args = parser.parse_args()
    if len({label for label, _ in args.corpus}) != len(args.corpus):
        raise ValueError("Corpus labels must be unique")
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"PPL output already exists: {output_dir}")
    started = datetime.now(timezone.utc).isoformat()
    config = {
        "model_manifest": str(args.model_manifest.resolve()),
        "runtime": {"device": args.device, "bf16": not args.no_bf16},
    }
    tokenizer, model, device, manifest, manifest_path, tokenizer_path = _load_model(config)
    results = {
        label: _score_one(
            tokenizer=tokenizer, model=model, device=device, corpus_path=path,
            output_dir=output_dir / label, block_size=args.block_size,
            batch_size=args.batch_size, bootstrap_samples=args.bootstrap_samples, seed=args.seed,
        )
        for label, path in args.corpus
    }
    import torch
    import transformers

    write_json(output_dir / "summary.json", {
        "status": "completed",
        "model_label": args.model_label,
        "model_manifest": str(manifest_path),
        "model_manifest_sha256": sha256_file(manifest_path),
        "model_id": manifest.get("model_id"),
        "model_revision": manifest.get("resolved_revision"),
        "tokenizer_path": str(tokenizer_path),
        "corpora": results,
        "runtime": {
            "git_commit": _git_commit(), "device": device,
            "dtype": str(next(model.parameters()).dtype),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cuda": torch.version.cuda, "torch": torch.__version__,
            "transformers": transformers.__version__, "python": platform.python_version(),
            "started_at": started, "completed_at": datetime.now(timezone.utc).isoformat(),
        },
    })
    print(output_dir)


if __name__ == "__main__":
    main()
