#!/usr/bin/env python3
"""Materialize exact matched OSCAR M2-A/M2-B token blocks for three frozen tokenizers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

import yaml

from transfer_vs_relearning.corpora.vngrs.d0_inputs_v3 import load_source_objects_v3
from transfer_vs_relearning.corpora.vngrs.d0_phase2 import tokenizer_compatibility
from transfer_vs_relearning.corpora.vngrs.d0_review import read_jsonl_rows
from transfer_vs_relearning.corpora.vngrs.d0_runtime import FrozenTokenizerAdapter
from transfer_vs_relearning.corpora.vngrs.parquet_loader_v3 import (
    load_verified_parquet_documents_v3,
)
from transfer_vs_relearning.corpora.vngrs.sample_transport import SOURCE_ROOT
from transfer_vs_relearning.data.qwen_pre_m2 import (
    build_branch_b_fact_registry,
    build_fixed_replacement_m2_blocks,
    deterministic_document_order,
    materialize_generic_blocks_with_audit,
)
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_json


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _assert_file(path: Path, expected_sha256: str) -> None:
    if not path.is_file() or path.is_symlink() or sha256_file(path) != expected_sha256:
        raise ValueError(f"Frozen input missing, unsafe or drifted: {path}")


def _selected_subject_ids(path: Path) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = payload.get("selected_subject_ids")
    if not isinstance(values, list) or len(values) != 100:
        raise ValueError("M2 requires the exact 100-subject M1 selection")
    result = {str(value) for value in values}
    if len(result) != 100:
        raise ValueError("M1 selected subject IDs are duplicated")
    return result


def _rows(documents: Iterable[Any], selected_ids: set[str]) -> list[dict[str, str]]:
    return [
        {"stable_document_id": row.stable_document_id, "text": row.text}
        for row in documents
        if row.corpus == "oscar" and row.stable_document_id in selected_ids
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--execution-enabled", action="store_true")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    config_path = (repo / args.config).resolve() if not args.config.is_absolute() else args.config
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not args.execution_enabled:
        raise ValueError("Exact block materialization remains execution-disabled")

    output_root = Path(config["output"]["root"])
    if output_root.exists():
        raise FileExistsError(f"Fresh materialization root already exists: {output_root}")
    for relative, expected in config["repository_inputs"].items():
        _assert_file(repo / relative, str(expected))

    source_root = Path(config["source"]["root"])
    split_root = Path(config["split"]["root"])
    _assert_file(
        source_root / "control/materialization_v3.json",
        config["source"]["materialization_manifest_sha256"],
    )
    _assert_file(
        split_root / "splits/train_document_ids.jsonl",
        config["split"]["train_ids_sha256"],
    )
    _assert_file(
        split_root / "splits/heldout_document_ids.jsonl",
        config["split"]["heldout_ids_sha256"],
    )
    train_ids = {
        row["stable_document_id"]
        for row in read_jsonl_rows(split_root / "splits/train_document_ids.jsonl")
    }
    heldout_ids = {
        row["stable_document_id"]
        for row in read_jsonl_rows(split_root / "splits/heldout_document_ids.jsonl")
    }
    if (
        len(train_ids) != config["split"]["train_documents"]
        or len(heldout_ids) != config["split"]["heldout_documents"]
        or train_ids & heldout_ids
    ):
        raise ValueError("Frozen OSCAR train/held-out split drift")

    objects = load_source_objects_v3(SOURCE_ROOT)
    documents = load_verified_parquet_documents_v3(
        source_root, objects, execution_enabled=True
    )
    selected = [row for row in documents if row.corpus == "oscar"]
    if len(selected) != config["source"]["document_count"]:
        raise ValueError("Exact lowercase OSCAR population count drift")
    if {row.stable_document_id for row in selected} != train_ids | heldout_ids:
        raise ValueError("OSCAR population no longer equals the frozen split")

    selection_path = repo / config["facts"]["selected_subjects"]
    canonical_path = repo / config["facts"]["canonical_profiles"]
    fact_rows = build_branch_b_fact_registry(
        read_csv_rows(canonical_path),
        _selected_subject_ids(selection_path),
        expected_subjects=100,
        version=config["facts"]["registry_version"],
    )
    if len(fact_rows) != config["facts"]["expected_unique_facts"]:
        raise ValueError("Branch-B fact registry cardinality drift")

    output_root.mkdir(parents=True)
    facts_path = output_root / "facts/branch_b_turkish_facts.jsonl"
    _write_jsonl(facts_path, fact_rows)
    inventory = json.loads(
        (repo / config["tokenizers"]["inventory"]).read_text(encoding="utf-8")
    )
    train_source = _rows(selected, train_ids)
    heldout_source = _rows(selected, heldout_ids)
    family: dict[str, Any] = {}
    for role in config["tokenizers"]["roles"]:
        binding = config["tokenizers"]["models"][role]
        adapter = FrozenTokenizerAdapter.load(
            role=role,
            snapshot_root=binding["snapshot_root"],
            inventory=inventory["models"][role],
            verify_snapshot_manifest=True,
        )
        compatibility = tokenizer_compatibility(adapter)
        namespace = config["packing"]["document_order_namespace"]
        seed = config["packing"]["seed"]
        ordered_train = deterministic_document_order(
            train_source, namespace=f"{namespace}|train", seed=seed
        )
        ordered_heldout = deterministic_document_order(
            heldout_source, namespace=f"{namespace}|heldout", seed=seed
        )
        train_blocks, train_audit = materialize_generic_blocks_with_audit(
            ordered_train,
            adapter,
            block_size=config["packing"]["block_size"],
            total_blocks=config["packing"]["train_blocks"],
        )
        m2_a, m2_b, matching = build_fixed_replacement_m2_blocks(
            train_blocks,
            fact_rows,
            adapter,
            replacement_block_count=config["packing"]["replacement_blocks"],
        )
        validation_blocks, validation_audit = materialize_generic_blocks_with_audit(
            ordered_heldout,
            adapter,
            block_size=config["packing"]["block_size"],
            total_blocks=config["packing"]["validation_blocks"],
        )
        role_root = output_root / "blocks" / role
        paths = {
            "m2_a_train": role_root / "m2_a_train.jsonl",
            "m2_b_train": role_root / "m2_b_train.jsonl",
            "shared_validation": role_root / "shared_validation.jsonl",
        }
        _write_jsonl(paths["m2_a_train"], m2_a)
        _write_jsonl(paths["m2_b_train"], m2_b)
        _write_jsonl(
            paths["shared_validation"],
            (
                {
                    "block_index": index,
                    "arm": "shared_validation",
                    "input_ids": block,
                    "attention_mask": [1] * config["packing"]["block_size"],
                }
                for index, block in enumerate(validation_blocks)
            ),
        )
        role_audit = {
            "schema_version": 1,
            "status": "EXACT_MATCHED_BLOCKS_PASS",
            "role": role,
            "compatibility": compatibility,
            "train_prefix": train_audit,
            "validation_prefix": validation_audit,
            "matching": matching,
            "fact_registry_sha256": sha256_file(facts_path),
            "artifacts": {
                label: {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
                for label, path in paths.items()
            },
            "ready_to_train": False,
        }
        audit_path = role_root / "audit.json"
        write_json(audit_path, role_audit)
        family[role] = {
            **role_audit,
            "audit": {"path": str(audit_path), "sha256": sha256_file(audit_path)},
        }
        del train_blocks, m2_a, m2_b, validation_blocks

    manifest = {
        "schema_version": 1,
        "status": "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED",
        "config": {"path": str(config_path), "sha256": sha256_file(config_path)},
        "source_document_ids_sha256": _canonical_sha256(
            sorted(row.stable_document_id for row in selected)
        ),
        "split": {
            "train_documents": len(train_ids),
            "heldout_documents": len(heldout_ids),
            "overlap": 0,
        },
        "facts": {
            "path": str(facts_path),
            "rows": len(fact_rows),
            "sha256": sha256_file(facts_path),
            "branch_a_exposures": 0,
        },
        "models": family,
        "training_opened": False,
        "model_weights_accessed": False,
        "ready_to_train": False,
    }
    write_json(output_root / "manifest.json", manifest)
    print(output_root / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
