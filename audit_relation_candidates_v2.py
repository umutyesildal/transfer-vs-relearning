#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any


NULL_PROMPTS = {
    "field_of_study": {
        "en": ("Field of study:", "Academic field:", "Subject studied:"),
        "tr": ("Egitim alani:", "Akademik alan:", "Okudugu bolum:"),
    },
    "works_in_industry": {
        "en": ("Industry:", "Employment sector:", "Works in:"),
        "tr": ("Sektor:", "Calistigi sektor:", "Faaliyet alani:"),
    },
}
TOKEN_LIMITS = {"en": (1, 3), "tr": (1, 4)}
ROBUST_Z_LIMIT = 3.5
PRIOR_SHARE_LIMIT = 0.10


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_candidates(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"relation", "object_en", "object_tr", "source_taxonomy", "source_category"}
    if not rows or set(rows[0]) != required:
        raise ValueError(f"Candidate CSV must contain exactly these columns: {sorted(required)}")
    return rows


def tokenizer_path_from_manifest(manifest: dict[str, Any], manifest_path: Path) -> Path:
    value = (
        manifest.get("tokenizer_source_path_absolute")
        or manifest.get("tokenizer_source_path")
        or manifest.get("local_path_absolute")
        or manifest.get("local_path")
    )
    if not value:
        raise ValueError("Model manifest has no tokenizer or model path")
    path = Path(str(value))
    return path if path.is_absolute() else (manifest_path.parent / path).resolve()


def model_path_from_manifest(manifest: dict[str, Any], manifest_path: Path) -> Path:
    value = manifest.get("local_path_absolute") or manifest.get("local_path")
    if not value:
        raise ValueError("Model manifest has no model path")
    path = Path(str(value))
    return path if path.is_absolute() else (manifest_path.parent / path).resolve()


def token_ids(tokenizer: Any, surface: str) -> list[int]:
    return list(tokenizer(" " + surface, add_special_tokens=False)["input_ids"])


def robust_z_scores(values: list[float]) -> list[float]:
    median = statistics.median(values)
    deviations = [abs(value - median) for value in values]
    mad = statistics.median(deviations)
    if mad == 0:
        return [0.0 for _ in values]
    scale = 1.4826 * mad
    return [(value - median) / scale for value in values]


def softmax_shares(values: list[float]) -> list[float]:
    maximum = max(values)
    weights = [math.exp(value - maximum) for value in values]
    total = sum(weights)
    return [weight / total for weight in weights]


def score_surfaces(
    *,
    tokenizer: Any,
    model: Any,
    device: str,
    prompts: tuple[str, ...],
    surfaces: list[str],
    batch_size: int,
) -> list[float]:
    import torch

    totals = [0.0] * len(surfaces)
    for prompt in prompts:
        for start in range(0, len(surfaces), batch_size):
            batch_surfaces = surfaces[start : start + batch_size]
            rendered = [prompt + " " + surface for surface in batch_surfaces]
            encoded = tokenizer(
                rendered,
                return_offsets_mapping=True,
                return_tensors="pt",
                padding=True,
            )
            offsets = encoded.pop("offset_mapping")
            input_ids = encoded["input_ids"].to(device)
            attention_mask = encoded["attention_mask"].to(device)
            with torch.inference_mode():
                logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
                log_probs = torch.log_softmax(logits.float(), dim=-1)
            for row_index, surface in enumerate(batch_surfaces):
                answer_start = len(prompt) + 1
                answer_end = answer_start + len(surface)
                pairs = offsets[row_index].tolist()
                answer_indices = [
                    index
                    for index, (token_start, token_end) in enumerate(pairs)
                    if token_end > answer_start and token_start < answer_end
                ]
                label_positions = [index - 1 for index in answer_indices if index > 0]
                answer_indices = [index for index in answer_indices if index > 0]
                if not answer_indices:
                    raise ValueError(f"Could not align answer tokens for {surface!r}")
                scores = [
                    log_probs[row_index, label_index, input_ids[row_index, token_index]]
                    for token_index, label_index in zip(answer_indices, label_positions)
                ]
                totals[start + row_index] += float(torch.stack(scores).mean().item())
    return [total / len(prompts) for total in totals]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=Path("data/relation_candidates_v2.csv"))
    parser.add_argument("--model-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output/relation_candidates_v2_audit"))
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    rows = read_candidates(args.candidates)
    manifest_path = args.model_manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tokenizer_path = tokenizer_path_from_manifest(manifest, manifest_path)
    model_path = model_path_from_manifest(manifest, manifest_path)
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(str(model_path), local_files_only=True)
    device = "cuda" if args.device == "auto" and torch.cuda.is_available() else args.device
    if device == "auto":
        device = "cpu"
    model.to(device)
    model.eval()

    output_rows: list[dict[str, Any]] = []
    relation_summaries: dict[str, Any] = {}
    for relation in sorted(NULL_PROMPTS):
        relation_rows = [row for row in rows if row["relation"] == relation]
        relation_summary: dict[str, Any] = {}
        language_scores: dict[str, list[float]] = {}
        language_tokens: dict[str, list[list[int]]] = {}
        for language in ("en", "tr"):
            surfaces = [row[f"object_{language}"] for row in relation_rows]
            language_tokens[language] = [token_ids(tokenizer, surface) for surface in surfaces]
            language_scores[language] = score_surfaces(
                tokenizer=tokenizer,
                model=model,
                device=device,
                prompts=NULL_PROMPTS[relation][language],
                surfaces=surfaces,
                batch_size=args.batch_size,
            )
            z_scores = robust_z_scores(language_scores[language])
            shares = softmax_shares(language_scores[language])
            relation_summary[language] = {
                "token_count_min": min(len(ids) for ids in language_tokens[language]),
                "token_count_max": max(len(ids) for ids in language_tokens[language]),
                "prior_score_min": min(language_scores[language]),
                "prior_score_max": max(language_scores[language]),
                "max_prior_share": max(shares),
                "max_abs_robust_z": max(abs(value) for value in z_scores),
            }
            for index, row in enumerate(relation_rows):
                row.setdefault("_audit", {})[language] = {
                    "token_ids": language_tokens[language][index],
                    "score": language_scores[language][index],
                    "z": z_scores[index],
                    "share": shares[index],
                }
        for row in relation_rows:
            flags = []
            flattened = dict(row)
            for language in ("en", "tr"):
                audit = row["_audit"][language]
                count = len(audit["token_ids"])
                low, high = TOKEN_LIMITS[language]
                if not low <= count <= high:
                    flags.append(f"{language}_token_count")
                if abs(audit["z"]) > ROBUST_Z_LIMIT:
                    flags.append(f"{language}_prior_z")
                if audit["share"] > PRIOR_SHARE_LIMIT:
                    flags.append(f"{language}_prior_share")
                flattened[f"{language}_token_count"] = count
                flattened[f"{language}_token_ids"] = "|".join(map(str, audit["token_ids"]))
                flattened[f"{language}_prior_mean_logprob"] = round(audit["score"], 8)
                flattened[f"{language}_prior_robust_z"] = round(audit["z"], 6)
                flattened[f"{language}_prior_share"] = round(audit["share"], 8)
            flattened["status"] = "review" if flags else "pass"
            flattened["flags"] = "|".join(flags)
            flattened.pop("_audit", None)
            output_rows.append(flattened)
        relation_summaries[relation] = relation_summary

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "candidate_audit.csv", output_rows)
    summary = {
        "audit_version": "relation_candidates_v2_prior_audit_v1",
        "candidate_sha256": sha256_file(args.candidates),
        "model_manifest": str(manifest_path),
        "model_id": manifest.get("model_id"),
        "tokenizer_path": str(tokenizer_path),
        "model_path": str(model_path),
        "device": device,
        "thresholds": {
            "token_limits": TOKEN_LIMITS,
            "robust_z_limit": ROBUST_Z_LIMIT,
            "prior_share_limit": PRIOR_SHARE_LIMIT,
        },
        "candidate_count": len(output_rows),
        "pass_count": sum(row["status"] == "pass" for row in output_rows),
        "review_count": sum(row["status"] == "review" for row in output_rows),
        "review_candidates": [
            {"relation": row["relation"], "object_en": row["object_en"], "flags": row["flags"]}
            for row in output_rows
            if row["status"] == "review"
        ],
        "relations": relation_summaries,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
