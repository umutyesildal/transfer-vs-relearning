from __future__ import annotations

"""Fail-closed validation helpers for the matched three-model M1 eval-v2 wave."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from transfer_vs_relearning.utils.io import (
    read_csv_rows,
    sha256_file,
    sha256_text,
    write_csv,
    write_json,
)


def verify_file(path: Path, expected_sha256: str, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Missing frozen file ({label}): {path}")
    observed = sha256_file(path)
    if observed != expected_sha256:
        raise ValueError(f"SHA-256 mismatch ({label}): {observed} != {expected_sha256}")


def verify_snapshot(
    *,
    snapshot_manifest_path: Path,
    snapshot_manifest_sha256: str,
    checkpoint_sha256: str,
    model_manifest_path: Path,
    model_manifest_sha256: str,
) -> dict[str, Any]:
    """Verify every model/tokenizer byte in one tracked epoch snapshot."""

    verify_file(snapshot_manifest_path, snapshot_manifest_sha256, "snapshot_manifest")
    verify_file(model_manifest_path, model_manifest_sha256, "snapshot_model_manifest")
    snapshot = json.loads(snapshot_manifest_path.read_text(encoding="utf-8"))
    files = snapshot.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Snapshot manifest requires a non-empty files inventory")
    snapshot_root = snapshot_manifest_path.parent.resolve()
    expected_paths: set[str] = set()
    total_bytes = 0
    for index, row in enumerate(files):
        if not isinstance(row, dict):
            raise ValueError(f"Invalid snapshot inventory row {index}")
        relative = Path(str(row.get("path", "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Snapshot inventory path escapes root: {relative}")
        target = (snapshot_root / relative).resolve()
        try:
            target.relative_to(snapshot_root)
        except ValueError as exc:
            raise ValueError(f"Snapshot inventory path escapes root: {target}") from exc
        relative_text = str(relative)
        if relative_text in expected_paths:
            raise ValueError(f"Duplicate snapshot inventory path: {relative_text}")
        expected_paths.add(relative_text)
        verify_file(target, str(row.get("sha256", "")), f"snapshot_file[{relative_text}]")
        expected_bytes = int(row.get("bytes", -1))
        if target.stat().st_size != expected_bytes:
            raise ValueError(f"Snapshot byte mismatch: {target}")
        total_bytes += expected_bytes
    observed_paths = {
        str(path.relative_to(snapshot_root))
        for path in snapshot_root.rglob("*")
        if path.is_file() and path.name != snapshot_manifest_path.name
    }
    if observed_paths != expected_paths:
        raise ValueError("Snapshot file inventory differs from the frozen manifest")
    calculated_checkpoint = sha256_text(
        json.dumps(files, ensure_ascii=False, sort_keys=True)
    )
    if snapshot.get("checkpoint_sha256") != checkpoint_sha256:
        raise ValueError("Snapshot manifest checkpoint identity mismatch")
    if calculated_checkpoint != checkpoint_sha256:
        raise ValueError("Snapshot inventory digest does not reproduce checkpoint_sha256")
    if int(snapshot.get("file_count", -1)) != len(files):
        raise ValueError("Snapshot file_count mismatch")
    if int(snapshot.get("total_bytes", -1)) != total_bytes:
        raise ValueError("Snapshot total_bytes mismatch")

    model_manifest = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    model_root = Path(str(model_manifest.get("local_path_absolute", ""))).resolve()
    tokenizer_root = Path(
        str(model_manifest.get("tokenizer_source_path_absolute", model_root))
    ).resolve()
    if model_root != snapshot_root or tokenizer_root != snapshot_root:
        raise ValueError("Model/tokenizer paths do not bind the tracked snapshot root")
    if model_manifest.get("checkpoint_sha256") != checkpoint_sha256:
        raise ValueError("Model manifest checkpoint identity mismatch")
    return {
        "status": "verified",
        "snapshot_manifest": str(snapshot_manifest_path),
        "snapshot_manifest_sha256": snapshot_manifest_sha256,
        "checkpoint_sha256": checkpoint_sha256,
        "file_count": len(files),
        "total_bytes": total_bytes,
    }


def verify_dataset_cache(
    *,
    content_manifest_path: Path,
    content_manifest_sha256: str,
    cache_root: Path,
    expected_files: int,
    expected_bytes: int,
) -> dict[str, Any]:
    """Verify the immutable 404-file Harness cache, including unexpected files."""

    verify_file(content_manifest_path, content_manifest_sha256, "dataset_content_manifest")
    cache_root = cache_root.resolve()
    rows: list[dict[str, Any]] = []
    expected_paths: set[Path] = set()
    with content_manifest_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            path = Path(str(row.get("path", ""))).resolve()
            try:
                path.relative_to(cache_root)
            except ValueError as exc:
                raise ValueError(
                    f"Dataset-cache manifest row {line_number} escapes cache root: {path}"
                ) from exc
            if path in expected_paths:
                raise ValueError(f"Duplicate dataset-cache path: {path}")
            expected_paths.add(path)
            verify_file(path, str(row.get("sha256", "")), f"dataset_cache[{line_number}]")
            if path.stat().st_size != int(row.get("bytes", -1)):
                raise ValueError(f"Dataset-cache byte mismatch: {path}")
            rows.append(row)
    observed_paths = {path.resolve() for path in cache_root.rglob("*") if path.is_file()}
    total_bytes = sum(int(row["bytes"]) for row in rows)
    if len(rows) != expected_files or total_bytes != expected_bytes:
        raise ValueError("Dataset-cache count/byte totals differ from the frozen contract")
    if observed_paths != expected_paths:
        raise ValueError("Dataset cache contains missing or unexpected files")
    return {
        "status": "verified",
        "file_count": len(rows),
        "total_bytes": total_bytes,
        "manifest_sha256": content_manifest_sha256,
    }


def inventory_tree(root: Path, *, excluded_names: Iterable[str] = ()) -> list[dict[str, Any]]:
    root = root.resolve()
    excluded = set(excluded_names)
    return [
        {
            "path": str(path),
            "relative_path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name not in excluded
    ]


def verify_inventory(root: Path, rows: list[dict[str, Any]]) -> None:
    root = root.resolve()
    declared: set[Path] = set()
    for row in rows:
        path = Path(str(row.get("path", ""))).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Artifact escapes state root: {path}") from exc
        if path in declared:
            raise ValueError(f"Duplicate artifact inventory path: {path}")
        declared.add(path)
        verify_file(path, str(row.get("sha256", "")), "state_artifact")
        if path.stat().st_size != int(row.get("bytes", -1)):
            raise ValueError(f"State artifact byte mismatch: {path}")


def _single_json(root: Path, pattern: str) -> tuple[Path, dict[str, Any]]:
    matches = sorted(root.rglob(pattern))
    if len(matches) != 1:
        raise ValueError(f"Expected one {pattern} under {root}, found {len(matches)}")
    path = matches[0]
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON mapping: {path}")
    return path, payload


def validate_harness_output(root: Path, expected_task_ids: list[str]) -> dict[str, Any]:
    path, payload = _single_json(root, "results_*.json")
    results = payload.get("results")
    if not isinstance(results, dict):
        raise ValueError("Harness result has no results mapping")
    groups = payload.get("groups") if isinstance(payload.get("groups"), dict) else {}
    missing = [task for task in expected_task_ids if task not in results and task not in groups]
    if missing:
        raise ValueError(f"Harness result misses requested tasks/groups: {missing}")
    samples = payload.get("n-samples")
    if not isinstance(samples, dict) or not samples:
        raise ValueError("Harness result has no n-samples denominator mapping")
    for task, row in samples.items():
        if not isinstance(row, dict):
            raise ValueError(f"Invalid Harness denominator row: {task}")
        original = int(row.get("original", -1))
        effective = int(row.get("effective", -1))
        if original <= 0 or effective != original:
            raise ValueError(f"Harness task is limited or incomplete: {task}")
    if payload.get("config", {}).get("limit") not in (None, "None"):
        raise ValueError("Scientific Harness result unexpectedly used --limit")
    return {
        "status": "complete",
        "result_path": str(path),
        "result_sha256": sha256_file(path),
        "requested_task_ids": expected_task_ids,
        "denominator_task_count": len(samples),
    }


def validate_factual_output(root: Path, expected_probes: int) -> dict[str, Any]:
    summary_path = root / "summary.json"
    verify_file(summary_path, sha256_file(summary_path), "factual_summary")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    rows = read_csv_rows(root / "hard_suite_per_fact.csv")
    probe_ids = [str(row.get("probe_id", "")) for row in rows]
    if (
        summary.get("status") != "completed"
        or int(summary.get("probes", -1)) != expected_probes
        or len(rows) != expected_probes
        or len(set(probe_ids)) != expected_probes
    ):
        raise ValueError(f"Factual output is incomplete; expected {expected_probes} probes")
    return {
        "status": "complete",
        "summary_path": str(summary_path),
        "summary_sha256": sha256_file(summary_path),
        "probe_count": expected_probes,
    }


def derive_cheap_factual_from_full(
    *, full_root: Path, cheap_root: Path, cheap_registry: Path, cheap_registry_sha256: str
) -> dict[str, Any]:
    """Filter the precommitted cheap IDs from full scores; never rescore them."""

    verify_file(cheap_registry, cheap_registry_sha256, "cheap_factual_registry")
    if cheap_root.exists():
        raise FileExistsError(f"Cheap derivation root already exists: {cheap_root}")
    registry_rows = read_csv_rows(cheap_registry)
    if len(registry_rows) != 1500:
        raise ValueError("Cheap registry must contain exactly 1,500 rows")
    cheap_to_source = {
        str(row["probe_id"]): str(row["probe_id"]).removeprefix("cheap_")
        for row in registry_rows
    }
    if len(cheap_to_source) != 1500 or any(
        not cheap_id.startswith("cheap_") for cheap_id in cheap_to_source
    ):
        raise ValueError("Cheap registry IDs do not follow the frozen cheap_<full-id> mapping")
    full_fact_path = full_root / "hard_suite_per_fact.csv"
    full_rows = read_csv_rows(full_fact_path)
    by_id = {str(row["probe_id"]): row for row in full_rows}
    if len(full_rows) != 12000 or len(by_id) != 12000:
        raise ValueError("Full factual evidence must contain 12,000 unique probes")
    missing = sorted(set(cheap_to_source.values()) - set(by_id))
    if missing:
        raise ValueError(f"Cheap/full factual join is incomplete; first={missing[0]}")
    derived_rows: list[dict[str, Any]] = []
    for registry_row in registry_rows:
        cheap_id = str(registry_row["probe_id"])
        source_id = cheap_to_source[cheap_id]
        source = dict(by_id[source_id])
        source["source_full_probe_id"] = source_id
        source["probe_id"] = cheap_id
        for field in (
            "fact_id",
            "subject_id",
            "direction",
            "relation",
            "form_id",
            "scaffold_id",
            "rendered_prompt",
            "expected_answer",
        ):
            if field in registry_row and str(source.get(field, "")) != str(registry_row[field]):
                raise ValueError(f"Cheap/full factual identity mismatch: {cheap_id}:{field}")
        derived_rows.append(source)
    cheap_root.mkdir(parents=True)
    write_csv(cheap_root / "hard_suite_per_fact.csv", derived_rows)

    full_token_path = full_root / "teacher_forced_per_token.csv"
    if full_token_path.is_file():
        token_rows = read_csv_rows(full_token_path)
        derived_tokens: list[dict[str, Any]] = []
        source_to_cheap = {source: cheap for cheap, source in cheap_to_source.items()}
        for row in token_rows:
            source_id = str(row.get("probe_id", ""))
            if source_id in source_to_cheap:
                copied = dict(row)
                copied["source_full_probe_id"] = source_id
                copied["probe_id"] = source_to_cheap[source_id]
                derived_tokens.append(copied)
        if {str(row["probe_id"]) for row in derived_tokens} != set(cheap_to_source):
            raise ValueError("Teacher-forced cheap derivation misses probe IDs")
        write_csv(cheap_root / "teacher_forced_per_token.csv", derived_tokens)

    top1 = sum(int(row["correct_rank_mean"]) == 1 for row in derived_rows)
    direction_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "top1": 0})
    relation_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "top1": 0})
    for row in derived_rows:
        correct = int(row["correct_rank_mean"]) == 1
        for key, bucket in (
            (str(row["direction"]), direction_counts),
            (str(row["relation"]), relation_counts),
        ):
            bucket[key]["n"] += 1
            bucket[key]["top1"] += int(correct)
    summary = {
        "status": "completed_derived_from_full_without_rescoring",
        "probes": len(derived_rows),
        "top1": top1,
        "top1_accuracy": top1 / len(derived_rows),
        "by_direction": dict(sorted(direction_counts.items())),
        "by_relation": dict(sorted(relation_counts.items())),
    }
    write_json(cheap_root / "summary.json", summary)
    manifest = {
        "schema_version": 1,
        "status": "complete",
        "derivation": "filter_frozen_cheap_probe_ids_from_full_scores_without_rescoring",
        "full_result_path": str(full_fact_path),
        "full_result_sha256": sha256_file(full_fact_path),
        "cheap_registry": str(cheap_registry),
        "cheap_registry_sha256": cheap_registry_sha256,
        "probe_count": 1500,
        "source_full_probe_count": 12000,
    }
    write_json(cheap_root / "derivation_manifest.json", manifest)
    return validate_factual_output(cheap_root, 1500)


def validate_exact_prefix_output(root: Path) -> dict[str, Any]:
    summary_path, summary = _single_json(root, "summary_metrics.json")
    counts = summary.get("counts")
    rows = read_csv_rows(summary_path.parent / "per_fact_results.csv")
    if (
        summary.get("completion_status") != "completed"
        or not isinstance(counts, dict)
        or int(counts.get("expected_probe_count", -1)) != 500
        or int(counts.get("successful_probe_count", -1)) != 500
        or int(counts.get("failed_probe_count", -1)) != 0
        or len(rows) != 500
    ):
        raise ValueError("Exact-prefix output is not a complete 500-probe result")
    return {
        "status": "complete",
        "summary_path": str(summary_path),
        "summary_sha256": sha256_file(summary_path),
        "probe_count": 500,
        "semantic_classification": "historical_exact_prefix_candidate_ranking_not_free_generation",
    }


def validate_turkish_perplexity_output(
    root: Path, *, corpus_sha256: str, expected_documents: int
) -> dict[str, Any]:
    summary_path = root / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    corpora = summary.get("corpora")
    row = corpora.get("trwiki_cross_domain") if isinstance(corpora, dict) else None
    if (
        summary.get("status") != "completed"
        or not isinstance(row, dict)
        or row.get("status") != "completed"
        or row.get("corpus_sha256") != corpus_sha256
        or int(row.get("document_count", -1)) != expected_documents
        or int(row.get("scored_token_count", 0)) <= 0
    ):
        raise ValueError("Turkish perplexity output is incomplete or identity-drifted")
    return {
        "status": "complete",
        "summary_path": str(summary_path),
        "summary_sha256": sha256_file(summary_path),
        "document_count": expected_documents,
    }


def validate_generation_output(
    root: Path, *, expected_prompts: int, expected_completions: int
) -> dict[str, Any]:
    summary_path, summary = _single_json(root, "summary_metrics.json")
    generation = summary.get("generation")
    completions = summary.get("generic_completions")
    if (
        summary.get("completion_status") != "completed"
        or not isinstance(generation, dict)
        or int(generation.get("prompt_count", -1)) != expected_prompts
        or not isinstance(completions, dict)
        or int(completions.get("item_count", -1)) != expected_completions
    ):
        raise ValueError("Generation-integrity output is incomplete")
    return {
        "status": "complete",
        "summary_path": str(summary_path),
        "summary_sha256": sha256_file(summary_path),
        "prompt_count": expected_prompts,
        "completion_count": expected_completions,
        "implementation": "indivisible_frozen_general_capability_panel",
    }

