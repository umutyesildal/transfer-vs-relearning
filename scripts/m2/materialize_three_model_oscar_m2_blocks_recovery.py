#!/usr/bin/env python3
"""Fail-persistent, memory-bounded recovery for three-model OSCAR M2 blocks."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import time
import traceback
from typing import Any, Iterable

import yaml

from transfer_vs_relearning.corpora.vngrs.d0_inputs_v3 import load_source_objects_v3
from transfer_vs_relearning.corpora.vngrs.d0_phase2 import tokenizer_compatibility
from transfer_vs_relearning.corpora.vngrs.d0_review import read_jsonl_rows
from transfer_vs_relearning.corpora.vngrs.d0_runtime import FrozenTokenizerAdapter
from transfer_vs_relearning.corpora.vngrs.parquet_loader_v3 import load_verified_parquet_documents_v3
from transfer_vs_relearning.corpora.vngrs.sample_transport import SOURCE_ROOT
from transfer_vs_relearning.data.qwen_pre_m2 import (
    build_branch_b_fact_registry,
    deterministic_document_order,
)
from transfer_vs_relearning.pipeline.m2_block_streaming import (
    stream_matched_train_files,
    stream_validation_file,
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
        if row.stable_document_id in selected_ids
    ]


def _resource_snapshot() -> dict[str, Any]:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "pid": os.getpid(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "ru_maxrss_kib_linux": usage.ru_maxrss,
        "user_cpu_seconds": usage.ru_utime,
        "system_cpu_seconds": usage.ru_stime,
    }


def _progress(root: Path, stage: str, **extra: Any) -> None:
    write_json(
        root / "control/progress.json",
        {
            "schema_version": 1,
            "status": "RUNNING",
            "stage": stage,
            "unix_time": time.time(),
            "resource": _resource_snapshot(),
            **extra,
        },
    )


def _validate_precreated_root(root: Path, contract_id: str) -> None:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Recovery output root must be precreated safely by the submitter")
    state_path = root / "control/submission_state.json"
    if not state_path.is_file() or state_path.is_symlink():
        raise ValueError("Recovery submission state is absent or unsafe")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("contract_id") != contract_id or state.get("status") != "SUBMISSION_PREPARED":
        raise ValueError("Recovery submission state drift")
    allowed_exact = {"submission_state.json", "submission_result.json"}
    for path in (value for value in root.rglob("*") if value.is_file()):
        relative = path.relative_to(root)
        if (
            len(relative.parts) != 2
            or relative.parts[0] != "control"
            or (
                relative.name not in allowed_exact
                and not relative.name.startswith("slurm-")
            )
        ):
            raise ValueError(f"Unexpected pre-run recovery artifact: {relative}")


def _validate_predecessor(config: dict[str, Any]) -> None:
    predecessor = config["predecessor"]
    root = Path(predecessor["root"])
    fact_path = root / predecessor["fact_path"]
    _assert_file(fact_path, predecessor["fact_sha256"])
    files = [path for path in root.rglob("*") if path.is_file()]
    blocks_root = root / "blocks"
    block_files = [
        path for path in blocks_root.rglob("*") if path.is_file()
    ] if blocks_root.exists() else []
    if (
        len(files) != predecessor["exact_files"]
        or fact_path.stat().st_size != predecessor["fact_bytes"]
        or sum(1 for _ in fact_path.open("rb")) != predecessor["fact_rows"]
        or (root / "manifest.json").exists()
        or len(block_files) != predecessor["block_files"]
    ):
        raise ValueError("Frozen predecessor partial root drift")


def run(repo: Path, config_path: Path) -> Path:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output_root = Path(config["output"]["root"])
    _validate_precreated_root(output_root, config["contract_id"])
    _progress(output_root, "validate_frozen_inputs")
    _validate_predecessor(config)
    for relative, expected in config["repository_inputs"].items():
        _assert_file(repo / relative, str(expected))

    source_root = Path(config["source"]["root"])
    split_root = Path(config["split"]["root"])
    _assert_file(
        source_root / "control/materialization_v3.json",
        config["source"]["materialization_manifest_sha256"],
    )
    _assert_file(split_root / "splits/train_document_ids.jsonl", config["split"]["train_ids_sha256"])
    _assert_file(
        split_root / "splits/heldout_document_ids.jsonl", config["split"]["heldout_ids_sha256"]
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

    _progress(output_root, "load_verified_source_population")
    objects = load_source_objects_v3(SOURCE_ROOT)
    documents = load_verified_parquet_documents_v3(source_root, objects, execution_enabled=True)
    selected = [row for row in documents if row.corpus == "oscar"]
    if len(selected) != config["source"]["document_count"]:
        raise ValueError("Exact lowercase OSCAR population count drift")
    selected_ids = {row.stable_document_id for row in selected}
    if selected_ids != train_ids | heldout_ids:
        raise ValueError("OSCAR population no longer equals the frozen split")
    del documents
    gc.collect()
    _progress(output_root, "non_oscar_population_released", oscar_documents=len(selected))

    fact_rows = build_branch_b_fact_registry(
        read_csv_rows(repo / config["facts"]["canonical_profiles"]),
        _selected_subject_ids(repo / config["facts"]["selected_subjects"]),
        expected_subjects=100,
        version=config["facts"]["registry_version"],
    )
    if len(fact_rows) != config["facts"]["expected_unique_facts"]:
        raise ValueError("Branch-B fact registry cardinality drift")
    facts_path = output_root / "facts/branch_b_turkish_facts.jsonl"
    _write_jsonl(facts_path, fact_rows)
    if sha256_file(facts_path) != config["predecessor"]["fact_sha256"]:
        raise ValueError("Recovery fact registry differs from the preserved predecessor")

    inventory = json.loads((repo / config["tokenizers"]["inventory"]).read_text(encoding="utf-8"))
    train_source = _rows(selected, train_ids)
    heldout_source = _rows(selected, heldout_ids)
    del selected
    gc.collect()
    _progress(
        output_root,
        "oscar_split_rows_ready",
        train_documents=len(train_source),
        heldout_documents=len(heldout_source),
    )

    family: dict[str, Any] = {}
    packing = config["packing"]
    for role in config["tokenizers"]["roles"]:
        _progress(output_root, "load_tokenizer", role=role)
        binding = config["tokenizers"]["models"][role]
        adapter = FrozenTokenizerAdapter.load(
            role=role,
            snapshot_root=binding["snapshot_root"],
            inventory=inventory["models"][role],
            verify_snapshot_manifest=True,
        )
        compatibility = tokenizer_compatibility(adapter)
        namespace = packing["document_order_namespace"]
        seed = packing["seed"]
        ordered_train = deterministic_document_order(
            train_source, namespace=f"{namespace}|train", seed=seed
        )
        ordered_heldout = deterministic_document_order(
            heldout_source, namespace=f"{namespace}|heldout", seed=seed
        )
        role_root = output_root / "blocks" / role
        paths = {
            "m2_a_train": role_root / "m2_a_train.jsonl",
            "m2_b_train": role_root / "m2_b_train.jsonl",
            "shared_validation": role_root / "shared_validation.jsonl",
        }
        _progress(output_root, "stream_train_blocks", role=role)
        train_audit, matching = stream_matched_train_files(
            ordered_train,
            adapter,
            fact_rows,
            m2_a_path=paths["m2_a_train"],
            m2_b_path=paths["m2_b_train"],
            block_size=packing["block_size"],
            total_blocks=packing["train_blocks"],
            replacement_block_count=packing["replacement_blocks"],
        )
        _progress(output_root, "stream_validation_blocks", role=role)
        validation_audit = stream_validation_file(
            ordered_heldout,
            adapter,
            path=paths["shared_validation"],
            block_size=packing["block_size"],
            total_blocks=packing["validation_blocks"],
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
        del ordered_train, ordered_heldout, adapter
        gc.collect()
        _progress(output_root, "role_complete", role=role)

    manifest = {
        "schema_version": 1,
        "status": "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED",
        "config": {"path": str(config_path), "sha256": sha256_file(config_path)},
        "source_document_ids_sha256": _canonical_sha256(sorted(selected_ids)),
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
        "memory_bounded_streaming": True,
        "predecessor_root_mutated": False,
        "training_opened": False,
        "model_weights_accessed": False,
        "ready_to_train": False,
    }
    manifest_path = output_root / "manifest.json"
    write_json(manifest_path, manifest)
    write_json(
        output_root / "control/final_audit.json",
        {
            "schema_version": 1,
            "status": "PASS",
            "manifest_sha256": sha256_file(manifest_path),
            "resource": _resource_snapshot(),
            "ready_to_train": False,
        },
    )
    _progress(output_root, "complete", terminal_status="PASS")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--execution-enabled", action="store_true")
    args = parser.parse_args()
    if not args.execution_enabled:
        raise ValueError("Exact block recovery remains execution-disabled")
    repo = args.repo_root.resolve()
    config_path = (repo / args.config).resolve() if not args.config.is_absolute() else args.config
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output_root = Path(config["output"]["root"])

    def interrupted(signum: int, _frame: Any) -> None:
        raise RuntimeError(f"received signal {signum}")

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        manifest = run(repo, config_path)
    except BaseException as exc:
        if output_root.exists() and output_root.is_dir():
            write_json(
                output_root / "control/failure.json",
                {
                    "schema_version": 1,
                    "status": "BLOCKED",
                    "exception_type": type(exc).__name__,
                    "message": str(exc)[:4096],
                    "traceback": traceback.format_exc()[-32768:],
                    "resource": _resource_snapshot(),
                    "automatic_retry_authorized": False,
                    "ready_to_train": False,
                },
            )
        raise
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
