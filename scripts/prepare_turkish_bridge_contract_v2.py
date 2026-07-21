#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

from transfer_vs_relearning.corpora.config import load_corpus_config
from transfer_vs_relearning.corpora.io import write_jsonl
from transfer_vs_relearning.data.turkish_bridge import (
    build_bridge_probes,
    build_localization_rows,
    build_relation_distractor_registry,
    eligibility_summary,
    eligible_fact_rows,
    materialize_shared_dose,
)
from transfer_vs_relearning.models.local_manifest import create_local_model_manifest
from transfer_vs_relearning.training.clm import load_training_config, tokenizer_path_from_manifest
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_csv, write_json
from transfer_vs_relearning.utils.text import normalize_text


APPROVED_PREFIXES = ("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize the append-only Phase 109A bridge contract v2")
    parser.add_argument("--experiment-config", type=Path, default=Path("configs/experiments/turkish_bridge_v1.yaml"))
    parser.add_argument("--training-template", type=Path, default=Path("configs/training/turkish_bridge_adaptation_template.yaml"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    config = load_corpus_config(args.experiment_config.resolve())
    template = load_training_config(args.training_template.resolve())
    output_root = _scratch(Path(config["contract"]["output_root"]), "contract output")
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite bridge contract: {output_root}")
    output_root.mkdir(parents=True)

    corpus = config["frozen_corpus"]
    corpus_train = _scratch(Path(corpus["train_file"]), "corpus train")
    corpus_validation = _scratch(Path(corpus["validation_file"]), "corpus validation")
    corpus_manifest = _scratch(Path(corpus["final_manifest"]), "corpus manifest")
    if sha256_file(corpus_manifest) != corpus["final_manifest_sha256"]:
        raise ValueError("Frozen corpus manifest SHA-256 mismatch")

    canonical_path = _resolve(repo_root, config["contract"]["canonical_profiles"])
    selected_path = _resolve(repo_root, config["contract"]["selected_subjects"])
    canonical_rows = read_csv_rows(canonical_path)
    selected_payload = json.loads(selected_path.read_text(encoding="utf-8"))
    selected_ids = set(selected_payload["selected_subject_ids"])

    model_manifests = _materialize_model_manifests(config, repo_root, output_root)
    tokenizers = _load_tokenizers(model_manifests, repo_root)

    localization = build_localization_rows(canonical_rows)
    for row in localization:
        row["normalized_en"] = normalize_text(str(row["canonical_en"]))
        row["normalized_tr"] = normalize_text(str(row["canonical_tr"]))
        for label, tokenizer in tokenizers.items():
            row[f"{label}_canonical_en_tokens"] = len(tokenizer.encode(str(row["canonical_en"]), add_special_tokens=False))
            row[f"{label}_canonical_tr_tokens"] = len(tokenizer.encode(str(row["canonical_tr"]), add_special_tokens=False))
    if any(
        int(row[f"{label}_{language}_tokens"]) <= 0
        for row in localization
        for label in tokenizers
        for language in ("canonical_en", "canonical_tr")
    ):
        raise ValueError("A canonical localized answer produced zero tokens")
    localization_path = output_root / "localization/localization_candidates.csv"
    write_csv(localization_path, localization)
    distractors = build_relation_distractor_registry(localization)
    distractor_path = output_root / "localization/relation_distractor_registry.json"
    write_json(distractor_path, distractors)
    localization_audit = {
        "status": "passed",
        "object_count": len(localization),
        "alias_policy": "canonical-only-v1; no post-outcome alias expansion",
        "normalization": "NFC plus project comparison normalization",
        "ambiguous_normalized_en_within_family": 0,
        "ambiguous_normalized_tr_within_family": 0,
        "token_lengths": {
            label: {
                "en_min": min(int(row[f"{label}_canonical_en_tokens"]) for row in localization),
                "en_max": max(int(row[f"{label}_canonical_en_tokens"]) for row in localization),
                "tr_min": min(int(row[f"{label}_canonical_tr_tokens"]) for row in localization),
                "tr_max": max(int(row[f"{label}_canonical_tr_tokens"]) for row in localization),
            }
            for label in tokenizers
        },
    }
    write_json(output_root / "localization/localization_audit.json", localization_audit)

    probes = build_bridge_probes(canonical_rows, selected_ids)
    probe_path = output_root / "probes/bridge_probe_registry.csv"
    write_csv(probe_path, probes)

    eligibility_manifest, eligible_sets, strict_sets = _materialize_eligibility(config, output_root)
    shared_eligible = set.intersection(*eligible_sets.values())
    shared_strict = set.intersection(*strict_sets.values())
    shared_eligible_path = output_root / "eligibility/shared_eligible_intersection.csv"
    shared_strict_path = output_root / "eligibility/shared_strict_intersection.csv"
    write_csv(shared_eligible_path, [{"fact_id": fact_id, "shared_eligible": True} for fact_id in sorted(shared_eligible)])
    write_csv(shared_strict_path, [{"fact_id": fact_id, "shared_strict": True} for fact_id in sorted(shared_strict)])

    adaptation = config["adaptation"]
    block_size = int(adaptation["block_size"])
    target_blocks = int(adaptation["full_supervised_tokens"]) // block_size
    dose_rows, dose_audit = materialize_shared_dose(
        _iter_jsonl(corpus_train), tokenizers,
        block_size=block_size,
        target_blocks=target_blocks,
        mapping_batch_rows=int(adaptation["mapping_batch_rows"]),
    )
    dose_train = output_root / "dose/train_documents.jsonl"
    write_jsonl(dose_train, dose_rows)
    validation_count = int(config["contract"]["validation_document_count"])
    validation_rows = []
    for row in _iter_jsonl(corpus_validation):
        validation_rows.append(row)
        if len(validation_rows) == validation_count:
            break
    if len(validation_rows) != validation_count:
        raise ValueError("Frozen validation split is smaller than requested contract subset")
    dose_validation = output_root / "dose/validation_documents.jsonl"
    write_jsonl(dose_validation, validation_rows)
    dose_audit.update({
        "status": "passed_no_cycling",
        "train_file": str(dose_train),
        "train_file_sha256": sha256_file(dose_train),
        "validation_file": str(dose_validation),
        "validation_file_sha256": sha256_file(dose_validation),
        "validation_document_count": validation_count,
        "validation_tokenization": _tokenization_audit(
            validation_rows,
            tokenizers,
            block_size=block_size,
            mapping_batch_rows=int(adaptation["mapping_batch_rows"]),
        ),
        "effective_blocks_per_optimizer_step": (
            int(adaptation["per_device_train_batch_size"])
            * int(adaptation["gradient_accumulation_steps"])
            * int(adaptation["world_size"])
        ),
        "low_optimizer_steps": int(adaptation["low_checkpoint_step"]),
        "full_optimizer_steps": int(adaptation["full_checkpoint_step"]),
        "low_supervised_tokens": int(adaptation["low_supervised_tokens"]),
        "full_supervised_tokens": int(adaptation["full_supervised_tokens"]),
        "ordered_document_policy": "same frozen raw JSONL rows for both models; Trainer data_seed=42",
        "cycling_policy": "forbidden; every model has at least 128 optimizer steps in one tokenized epoch",
    })
    for label, blocks in dose_audit["model_grouped_block_counts"].items():
        if blocks // dose_audit["effective_blocks_per_optimizer_step"] < int(adaptation["full_checkpoint_step"]):
            raise ValueError(f"{label} would cycle before the full endpoint")
    dose_manifest_path = output_root / "dose/dose_manifest.json"
    write_json(dose_manifest_path, dose_audit)

    configs = _materialize_training_configs(
        template, model_manifests, dose_train, dose_validation, dose_manifest_path, output_root
    )
    storage = _storage_estimate(model_manifests)
    storage_path = output_root / "storage_estimate.json"
    write_json(storage_path, storage)

    files = [
        localization_path, distractor_path, output_root / "localization/localization_audit.json",
        probe_path, shared_eligible_path, shared_strict_path, dose_train, dose_validation,
        dose_manifest_path, storage_path, *model_manifests.values(), *configs.values(),
        *(Path(value["output"]) for value in eligibility_manifest.values()),
    ]
    manifest = {
        "version": "turkish_bridge_contract_v2",
        "status": "frozen_ready_for_training_preflight",
        "corpus_final_manifest": str(corpus_manifest),
        "corpus_final_manifest_sha256": sha256_file(corpus_manifest),
        "canonical_profiles": str(canonical_path.resolve()),
        "canonical_profiles_sha256": sha256_file(canonical_path),
        "selected_subjects": str(selected_path.resolve()),
        "selected_subjects_sha256": sha256_file(selected_path),
        "subject_count": len(selected_ids),
        "fact_count": len(selected_ids) * 5,
        "probe_count": len(probes),
        "localization_object_count": len(localization),
        "eligibility": eligibility_manifest,
        "shared_eligible_count": len(shared_eligible),
        "shared_strict_count": len(shared_strict),
        "dose": dose_audit,
        "storage": storage,
        "artifact_hashes": {str(path.relative_to(output_root)): sha256_file(path) for path in files},
    }
    manifest_path = output_root / "manifest.json"
    write_json(manifest_path, manifest)
    print(manifest_path)


def _materialize_model_manifests(config: dict[str, Any], repo_root: Path, output_root: Path) -> dict[str, Path]:
    outputs: dict[str, Path] = {}
    for model in config["models"]:
        label = str(model["label"])
        output = output_root / f"models/{label}.json"
        if model.get("model_manifest"):
            payload = json.loads(_scratch(Path(model["model_manifest"]), f"{label} model manifest").read_text(encoding="utf-8"))
            payload["local_path"] = str(_scratch(Path(payload["local_path_absolute"]), f"{label} model"))
            payload["local_path_absolute"] = payload["local_path"]
            tokenizer_value = payload.get("tokenizer_source_path_absolute") or payload["local_path_absolute"]
            payload["tokenizer_source_path_absolute"] = str(_scratch(Path(tokenizer_value), f"{label} tokenizer"))
            write_json(output, payload)
        else:
            source = _resolve(repo_root, model["source_model_manifest"])
            create_local_model_manifest(
                source_manifest_path=source,
                local_model_dir=_scratch(Path(model["model_dir"]), f"{label} model"),
                output_manifest_path=output,
                model_id=f"turkish_bridge_{label}_m1",
                resolved_revision=str(model["m1_endpoint"]),
                training_checkpoint=str(model["m1_endpoint"]),
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            payload["local_path"] = str(Path(payload["local_path_absolute"]).resolve())
            payload["local_path_absolute"] = payload["local_path"]
            payload["tokenizer_source_path_absolute"] = str(Path(payload["tokenizer_source_path_absolute"]).resolve())
            write_json(output, payload)
        outputs[label] = output
    return outputs


def _load_tokenizers(manifests: dict[str, Path], repo_root: Path) -> dict[str, Any]:
    from transformers import AutoTokenizer
    output = {}
    for label, path in manifests.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        model_path = Path(payload["local_path_absolute"])
        tokenizer_path = tokenizer_path_from_manifest(payload, repo_root, model_path)
        output[label] = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True, use_fast=True)
    return output


def _materialize_eligibility(config: dict[str, Any], output_root: Path) -> tuple[dict[str, Any], dict[str, set[str]], dict[str, set[str]]]:
    manifest: dict[str, Any] = {}
    eligible: dict[str, set[str]] = {}
    strict: dict[str, set[str]] = {}
    for model in config["models"]:
        label = str(model["label"])
        source = _scratch(Path(model["hard_result"]), f"{label} hard result")
        rows = eligible_fact_rows(source)
        output = output_root / f"eligibility/{label}.csv"
        write_csv(output, rows)
        eligible[label] = {str(row["fact_id"]) for row in rows if row["eligible_3_of_4_heldout"]}
        strict[label] = {str(row["fact_id"]) for row in rows if row["strict_8_of_8"]}
        per_subject = Counter(str(row["subject_id"]) for row in rows if row["eligible_3_of_4_heldout"])
        manifest[label] = {
            "source": str(source), "source_sha256": sha256_file(source),
            "output": str(output), "output_sha256": sha256_file(output),
            "summary": eligibility_summary(rows),
            "subjects_with_at_least_4_of_5_eligible_facts": sum(value >= 4 for value in per_subject.values()),
        }
    return manifest, eligible, strict


def _materialize_training_configs(
    template: dict[str, Any], manifests: dict[str, Path], train: Path, validation: Path,
    dose_manifest: Path, output_root: Path,
) -> dict[str, Path]:
    outputs = {}
    for label, model_manifest in manifests.items():
        payload = copy.deepcopy(template)
        payload["dataset"].update({
            "dataset_dir": str(train.parent), "dataset_manifest": str(dose_manifest),
            "train_file": str(train), "validation_file": str(validation),
        })
        payload["model"]["base_model_manifest"] = str(model_manifest)
        payload["training"].update({
            "run_name": f"turkish_bridge_{label}_seed42",
            "output_root": f"/vol/tmp2/yesildau/turkish_bridge_v1/training/{label}",
            "model_load_dtype": "bfloat16",
        })
        path = output_root / f"training_configs/{label}.json"
        write_json(path, payload)
        outputs[label] = path
    return outputs


def _storage_estimate(manifests: dict[str, Path]) -> dict[str, Any]:
    models = {}
    family_total = 0
    for label, manifest_path in manifests.items():
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        model_dir = Path(payload["local_path_absolute"])
        weight_bytes = sum(path.stat().st_size for path in model_dir.glob("*.safetensors"))
        checkpoint_bytes = weight_bytes * 3 + 64 * 1024 * 1024
        retained_model_only_bytes = weight_bytes
        active_bytes = checkpoint_bytes * 4 + retained_model_only_bytes
        family_total += active_bytes
        models[label] = {
            "model_weight_bytes": weight_bytes,
            "estimated_checkpoint_bytes_with_optimizer": checkpoint_bytes,
            "expected_checkpoint_directories": 4,
            "expected_final_model_directories": 1,
            "estimated_active_bytes": active_bytes,
        }
    return {
        "models": models,
        "estimated_family_active_bytes": family_total,
        "preflight_reserve_bytes": int(family_total * 1.3),
        "retention": "keep low checkpoint-32 and full model-only endpoint; delete intermediate optimizer states only after evaluation and checksums",
    }


def _tokenization_audit(
    rows: list[dict[str, Any]],
    tokenizers: dict[str, Any],
    *,
    block_size: int,
    mapping_batch_rows: int,
) -> dict[str, Any]:
    token_counts = {label: 0 for label in tokenizers}
    block_counts = {label: 0 for label in tokenizers}
    for start in range(0, len(rows), mapping_batch_rows):
        texts = [str(row["text"]) for row in rows[start : start + mapping_batch_rows]]
        for label, tokenizer in tokenizers.items():
            batch_tokens = sum(len(tokenizer.encode(text, add_special_tokens=False)) + 1 for text in texts)
            token_counts[label] += batch_tokens
            block_counts[label] += batch_tokens // block_size
    if any(value <= 0 for value in block_counts.values()):
        raise ValueError(f"Validation subset produced zero grouped blocks: {block_counts}")
    return {
        "model_token_counts_including_document_eos": token_counts,
        "model_grouped_block_counts": block_counts,
        "mapping_batch_rows": mapping_batch_rows,
    }


def _resolve(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else repo_root / path).resolve()


def _scratch(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not any(str(resolved).startswith(prefix) for prefix in APPROVED_PREFIXES):
        raise ValueError(f"{label} is not on approved scratch: {resolved}")
    if not resolved.exists() and "output" not in label:
        raise FileNotFoundError(resolved)
    return resolved


def _iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            yield value


if __name__ == "__main__":
    main()
