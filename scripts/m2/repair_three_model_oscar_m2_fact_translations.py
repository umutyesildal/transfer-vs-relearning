#!/usr/bin/env python3
"""Rebuild only M2-B fact replacements from immutable M2-A blocks and corrected facts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Iterable

import yaml

from transfer_vs_relearning.corpora.vngrs.d0_phase2 import tokenizer_compatibility
from transfer_vs_relearning.corpora.vngrs.d0_review import read_jsonl_rows
from transfer_vs_relearning.corpora.vngrs.d0_runtime import FrozenTokenizerAdapter
from transfer_vs_relearning.pipeline.m2_block_streaming import build_fixed_replacement_schedule
from transfer_vs_relearning.utils.io import sha256_file, write_json


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _assert_file(path: Path, expected_sha256: str) -> None:
    if not path.is_file() or path.is_symlink() or sha256_file(path) != expected_sha256:
        raise ValueError(f"Frozen input missing, unsafe or drifted: {path}")


def _artifact(binding: dict[str, Any], label: str) -> Path:
    path = Path(str(binding["path"])).resolve()
    _assert_file(path, str(binding["sha256"]))
    if path.stat().st_size != int(binding["bytes"]):
        raise ValueError(f"Frozen artifact byte-size drift: {label}")
    return path


def _validate_precreated_root(root: Path) -> None:
    if not root.exists():
        return
    allowed = {"control/submission_state.json", "control/submission_result.json"}
    for path in (item for item in root.rglob("*") if item.is_file()):
        relative = str(path.relative_to(root))
        if relative not in allowed and not relative.startswith(("logs/", "tmp/")):
            raise ValueError(f"Unexpected pre-run fact-translation repair artifact: {relative}")


def rewrite_m2_b(
    *,
    m2_a_path: Path,
    prior_m2_b_path: Path,
    destination: Path,
    schedule: dict[int, tuple[list[int], list[str]]],
    block_size: int,
    total_blocks: int,
) -> dict[str, Any]:
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    changed_blocks = 0
    changed_token_positions = 0
    with m2_a_path.open("r", encoding="utf-8") as source_a, prior_m2_b_path.open(
        "r", encoding="utf-8"
    ) as source_old_b, temporary.open("w", encoding="utf-8") as target:
        for block_index in range(total_blocks):
            line_a, line_old_b = source_a.readline(), source_old_b.readline()
            if not line_a or not line_old_b:
                raise ValueError("Frozen M2 block family ended before the exact block count")
            row_a, row_old_b = json.loads(line_a), json.loads(line_old_b)
            ids = [int(value) for value in row_a.get("input_ids", [])]
            mask = [int(value) for value in row_a.get("attention_mask", [])]
            if (
                row_a.get("block_index") != block_index
                or row_a.get("arm") != "M2-A"
                or len(ids) != block_size
                or len(mask) != block_size
                or any(value != 1 for value in mask)
                or row_old_b.get("block_index") != block_index
                or row_old_b.get("arm") != "M2-B"
            ):
                raise ValueError(f"Frozen predecessor block invariant failed at {block_index}")
            replacement = schedule.get(block_index)
            repaired = replacement[0] + ids[len(replacement[0]) :] if replacement else ids
            old_ids = [int(value) for value in row_old_b.get("input_ids", [])]
            if len(old_ids) != block_size:
                raise ValueError(f"Frozen predecessor M2-B block length drift at {block_index}")
            differences = sum(left != right for left, right in zip(repaired, old_ids, strict=True))
            if differences:
                changed_blocks += 1
                changed_token_positions += differences
            target.write(
                json.dumps(
                    {
                        "block_index": block_index,
                        "arm": "M2-B",
                        "input_ids": repaired,
                        "attention_mask": [1] * block_size,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )
        if source_a.readline() or source_old_b.readline():
            raise ValueError("Frozen predecessor block family exceeds the exact block count")
    os.replace(temporary, destination)
    if changed_blocks <= 0 or changed_blocks > len(schedule):
        raise ValueError("Corrected fact registry produced an invalid changed-block count")
    return {
        "changed_blocks_vs_predecessor_m2_b": changed_blocks,
        "changed_token_positions_vs_predecessor_m2_b": changed_token_positions,
        "replacement_schedule_blocks": len(schedule),
        "non_replacement_blocks_reused_from_m2_a": total_blocks - len(schedule),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--execution-enabled", action="store_true")
    args = parser.parse_args()
    if not args.execution_enabled:
        raise PermissionError("Fact-translation block repair requires --execution-enabled")
    repo = args.repo_root.resolve()
    config_path = args.config.resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if config.get("status") != "frozen_unexecuted" or config.get("execution_authorized") is not False:
        raise ValueError("Fact-translation repair config is not frozen and execution-disabled")
    output_root = Path(config["output"]["root"]).resolve()
    _validate_precreated_root(output_root)

    predecessor_path = Path(config["predecessor"]["manifest"]).resolve()
    _assert_file(predecessor_path, config["predecessor"]["manifest_sha256"])
    predecessor = _json(predecessor_path)
    if predecessor.get("status") != "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED":
        raise ValueError("Predecessor M2 block family is not exact/materialized")
    corrected_registry = (repo / config["facts"]["corrected_registry"]).resolve()
    review_validation_path = (repo / config["facts"]["review_validation"]).resolve()
    _assert_file(corrected_registry, config["facts"]["corrected_registry_sha256"])
    _assert_file(review_validation_path, config["facts"]["review_validation_sha256"])
    review = _json(review_validation_path)
    if (
        review.get("status") != "M2_FACT_REVIEW_PASS"
        or review.get("verdicts") != {"usable": 250}
        or review.get("fact_registry_sha256") != config["facts"]["corrected_registry_sha256"]
    ):
        raise ValueError("Corrected 250-fact human review gate did not pass")
    facts = read_jsonl_rows(corrected_registry)
    if len(facts) != 250 or {row.get("branch_group") for row in facts} != {"B"}:
        raise ValueError("Corrected registry must contain exactly 250 Branch-B facts")

    output_root.mkdir(parents=True, exist_ok=True)
    inventory_path = (repo / config["tokenizers"]["inventory"]).resolve()
    _assert_file(inventory_path, config["tokenizers"]["inventory_sha256"])
    inventory = _json(inventory_path)
    models: dict[str, Any] = {}
    for role in config["tokenizers"]["roles"]:
        predecessor_role = predecessor["models"][role]
        adapter = FrozenTokenizerAdapter.load(
            role=role,
            snapshot_root=config["tokenizers"]["models"][role]["snapshot_root"],
            inventory=inventory["models"][role],
            verify_snapshot_manifest=True,
        )
        compatibility = tokenizer_compatibility(adapter)
        schedule, matching = build_fixed_replacement_schedule(
            facts,
            adapter,
            block_size=int(config["packing"]["block_size"]),
            total_blocks=int(config["packing"]["train_blocks"]),
            replacement_block_count=int(config["packing"]["replacement_blocks"]),
        )
        m2_a = _artifact(predecessor_role["artifacts"]["m2_a_train"], f"{role} M2-A")
        prior_m2_b = _artifact(predecessor_role["artifacts"]["m2_b_train"], f"{role} prior M2-B")
        validation = _artifact(
            predecessor_role["artifacts"]["shared_validation"], f"{role} validation"
        )
        role_root = output_root / "blocks" / role
        role_root.mkdir(parents=True)
        repaired_m2_b = role_root / "m2_b_train_corrected.jsonl"
        repair = rewrite_m2_b(
            m2_a_path=m2_a,
            prior_m2_b_path=prior_m2_b,
            destination=repaired_m2_b,
            schedule=schedule,
            block_size=int(config["packing"]["block_size"]),
            total_blocks=int(config["packing"]["train_blocks"]),
        )
        role_audit = {
            "schema_version": 1,
            "status": "EXACT_MATCHED_BLOCKS_PASS",
            "role": role,
            "compatibility": compatibility,
            "train_prefix": predecessor_role["train_prefix"],
            "validation_prefix": predecessor_role["validation_prefix"],
            "matching": matching,
            "translation_repair": repair,
            "fact_registry_sha256": sha256_file(corrected_registry),
            "artifacts": {
                "m2_a_train": predecessor_role["artifacts"]["m2_a_train"],
                "m2_b_train": {
                    "path": str(repaired_m2_b),
                    "bytes": repaired_m2_b.stat().st_size,
                    "sha256": sha256_file(repaired_m2_b),
                },
                "shared_validation": predecessor_role["artifacts"]["shared_validation"],
            },
            "predecessor_m2_b": predecessor_role["artifacts"]["m2_b_train"],
            "ready_to_train": False,
        }
        audit_path = role_root / "audit.json"
        write_json(audit_path, role_audit)
        models[role] = {**role_audit, "audit": {"path": str(audit_path), "sha256": sha256_file(audit_path)}}

    manifest = {
        "schema_version": 1,
        "status": "EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED",
        "repair_status": "M2_FACT_TRANSLATION_REPAIR_PASS",
        "config": {"path": str(config_path), "sha256": sha256_file(config_path)},
        "predecessor": {"path": str(predecessor_path), "sha256": sha256_file(predecessor_path)},
        "facts": {
            "path": str(corrected_registry),
            "rows": 250,
            "sha256": sha256_file(corrected_registry),
            "branch_a_exposures": 0,
            "human_review_validation_sha256": sha256_file(review_validation_path),
        },
        "models": models,
        "generic_m2_a_and_validation_reused_read_only": True,
        "predecessor_root_mutated": False,
        "model_weights_accessed": False,
        "gpu": False,
        "training_opened": False,
        "ready_to_train": False,
    }
    manifest_path = output_root / "manifest.json"
    write_json(manifest_path, manifest)
    write_json(
        output_root / "control/final_audit.json",
        {
            "schema_version": 1,
            "status": "M2_FACT_TRANSLATION_REPAIR_PASS",
            "manifest_sha256": sha256_file(manifest_path),
            "ready_to_train": False,
        },
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
