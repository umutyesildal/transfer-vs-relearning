from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import yaml

from transfer_vs_relearning.pipeline.artifacts import CHECKPOINT_FIELDS, FACTUAL_FIELDS, METRIC_FIELDS
from transfer_vs_relearning.utils.io import sha256_file, write_json


MODEL_IDS = ("olmo", "qwen", "smollm")
CANONICAL_LANES = (
    "english_retention_wikitext",
    "english_grammar_blimp",
    "english_capability",
    "turkish_capability",
    "turkish_perplexity",
    "factual_access",
    "generation_integrity",
)
ALL_LANES = CANONICAL_LANES + ("exact_prefix",)

# These aliases are deliberately narrow. If more than one numeric source matches an alias,
# normalization stops and the source adapter must be revised; it never guesses.
METRIC_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "english_retention_wikitext": {
        "bits_per_byte": ("bits_per_byte", "bpb"),
        "word_perplexity": ("word_perplexity", "word_ppl"),
        "byte_perplexity": ("byte_perplexity", "byte_ppl"),
    },
    "english_grammar_blimp": {
        "accuracy": ("macro_accuracy", "accuracy", "acc"),
    },
    "english_capability": {
        "hellaswag_acc_norm": ("hellaswag_acc_norm", "acc_norm"),
    },
    "turkish_capability": {
        "accuracy": ("macro_accuracy", "accuracy", "acc_norm"),
    },
    "turkish_perplexity": {
        "bits_per_byte": ("bits_per_byte", "bpb"),
        "word_perplexity": ("word_perplexity", "word_ppl"),
        "byte_perplexity": ("byte_perplexity", "byte_ppl"),
    },
    "factual_access": {
        "top1_accuracy": ("top1_accuracy", "factual_top1_accuracy"),
        "robust_fact_intersection": ("robust_fact_intersection",),
    },
    "generation_integrity": {
        "empty_generation_rate": ("empty_generation_rate",),
        "repeated_3gram_fraction": ("repeated_3gram_fraction",),
    },
    "exact_prefix": {
        "exact_prefix_accuracy": ("exact_prefix_accuracy", "top1_accuracy", "accuracy"),
    },
}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _verify(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise ValueError(f"Missing {label}: {path}")
    observed = sha256_file(path)
    if observed != expected:
        raise ValueError(f"{label} hash mismatch: {observed} != {expected}")


def _numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _walk(payload: Any, prefix: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(payload, dict):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, value
            yield from _walk(value, path)
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            yield from _walk(value, f"{prefix}[{index}]")


def _candidate_values(documents: list[tuple[Path, dict[str, Any]]], aliases: tuple[str, ...]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for path, payload in documents:
        for json_path, value in _walk(payload):
            leaf = json_path.rsplit(".", 1)[-1]
            if leaf in aliases and _numeric(value):
                matches.append({"path": str(path), "json_path": json_path, "value": float(value)})
    return matches


def _load_plan(config_path: Path, *, repo_root: Path) -> dict[str, Any]:
    config_path = config_path.resolve()
    config = _mapping(yaml.safe_load(config_path.read_text(encoding="utf-8")), "normalization config")
    if config.get("schema_version") != 1 or config.get("eval_contract") != "eval-v2":
        raise ValueError("Only eval-v2 normalization schema_version 1 is supported")
    if config.get("rescore_authorized") is not False or config.get("historical_sources_read_only") is not True:
        raise ValueError("Normalization must forbid rescoring and source mutation")
    identities = _mapping(config.get("identities"), "identities")
    for label in ("eval_contract", "eval_registry", "result_schema"):
        row = _mapping(identities.get(label), f"identities.{label}")
        _verify((repo_root / str(row["path"])).resolve(), str(row["sha256"]), label)
    projection = _mapping(config.get("input_projection"), "input_projection")
    if projection.get("required_source_rows") != 24:
        raise ValueError("Normalization requires exactly 24 projection rows")
    output_root = config.get("output_root")
    if not isinstance(output_root, str) or not output_root.startswith("/"):
        raise ValueError("output_root must be an absolute fresh path")
    return {
        "config": config,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "projection": projection,
        "output_root": output_root,
    }


def _load_projection(plan: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    projection = plan["projection"]
    registry_path = Path(str(projection["source_registry"]))
    manifest_path = Path(str(projection["projection_manifest"]))
    _verify(registry_path, str(projection["source_registry_sha256"]), "source registry")
    _verify(manifest_path, str(projection["projection_manifest_sha256"]), "projection manifest")
    manifest = _json(manifest_path)
    if manifest.get("status") != "projection_complete_pending_metric_normalization":
        raise ValueError("Projection manifest is not complete and pending normalization")
    rows = [json.loads(line) for line in registry_path.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 24 or len({(row.get("model_id"), row.get("lane_id")) for row in rows}) != 24:
        raise ValueError("Projection registry must contain 24 unique rows")
    if any("pile" in str(row.get("lane_id", "")).casefold() for row in rows):
        raise ValueError("Pile evidence is forbidden")
    return rows, manifest


def _lane_documents(row: dict[str, Any]) -> tuple[list[tuple[Path, dict[str, Any]]], dict[str, Any]]:
    lane_path = Path(str(row["source_path"]))
    lane_sha = row.get("sha256", row.get("source_sha256"))
    _verify(lane_path, str(lane_sha), "lane result")
    lane = _json(lane_path)
    if lane.get("status") != "complete" or lane.get("returncode") != 0:
        raise ValueError(f"Lane is not complete: {row.get('model_id')}:{row.get('lane_id')}")
    documents: list[tuple[Path, dict[str, Any]]] = [(lane_path, lane)]
    for artifact in lane.get("artifacts", []):
        item = _mapping(artifact, "lane artifact")
        artifact_path = Path(str(item.get("path", "")))
        _verify(artifact_path, str(item.get("sha256")), "lane artifact")
        if artifact_path.suffix.casefold() == ".json" and artifact_path.stat().st_size <= 10 * 1024 * 1024:
            try:
                documents.append((artifact_path, _json(artifact_path)))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
    return documents, lane


def audit_normalization(config_path: Path, *, repo_root: Path) -> dict[str, Any]:
    plan = _load_plan(config_path, repo_root=repo_root)
    rows, manifest = _load_projection(plan)
    findings: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    for row in rows:
        model_id = str(row["model_id"])
        lane_id = str(row["lane_id"])
        if model_id not in MODEL_IDS or lane_id not in ALL_LANES:
            raise ValueError(f"Unknown source binding: {model_id}:{lane_id}")
        documents, lane = _lane_documents(row)
        for metric, aliases in METRIC_ALIASES[lane_id].items():
            matches = _candidate_values(documents, aliases)
            if len(matches) != 1:
                findings.append(
                    {
                        "model_id": model_id,
                        "lane_id": lane_id,
                        "metric": metric,
                        "status": "blocked_by_metric_schema",
                        "candidate_count": len(matches),
                        "aliases": list(aliases),
                    }
                )
                continue
            match = matches[0]
            metric_rows.append(
                {
                    "model_id": model_id,
                    "lane_id": lane_id,
                    "metric": metric,
                    "value": match["value"],
                    "raw_artifact_path": match["path"],
                    "raw_artifact_json_path": match["json_path"],
                    "raw_artifact_sha256": sha256_file(Path(match["path"])),
                    "source_lane_sha256": row.get("sha256", row.get("source_sha256")),
                    "source_status": lane.get("status"),
                }
            )
    expected_metric_count = sum(
        len(METRIC_ALIASES[str(row["lane_id"])]) for row in rows
    )
    return {
        "schema_version": 1,
        "status": "audit_pass" if not findings and len(metric_rows) == expected_metric_count else "audit_blocked",
        "config_path": plan["config_path"],
        "config_sha256": plan["config_sha256"],
        "projection_manifest_sha256": plan["projection"]["projection_manifest_sha256"],
        "source_row_count": len(rows),
        "metric_observation_candidate_count": len(metric_rows),
        "expected_metric_observation_count": expected_metric_count,
        "findings": findings,
        "normalization_performed": False,
        "rescoring_performed": False,
        "historical_sources_mutated": False,
    }


def _write_parquet(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    import pandas as pd

    frame = pd.DataFrame([{field: row.get(field) for field in fields} for row in rows], columns=list(fields))
    frame.to_parquet(path, index=False)


def normalize(config_path: Path, *, repo_root: Path) -> dict[str, Any]:
    plan = _load_plan(config_path, repo_root=repo_root)
    config = plan["config"]
    if config.get("execution_authorized") is not True or config.get("normalization_authorized") is not True:
        raise PermissionError("Normalization execution is not authorized by the frozen config")
    audit = audit_normalization(config_path, repo_root=repo_root)
    if audit["status"] != "audit_pass":
        raise ValueError("Normalization audit is blocked; no output root will be created")
    output_root = Path(plan["output_root"])
    if output_root.exists():
        raise FileExistsError(f"Normalization output root already exists: {output_root}")
    output_root.mkdir(parents=True)
    # The actual normalized rows are deliberately assembled only after the complete audit.
    rows, _ = _load_projection(plan)
    observations: list[dict[str, Any]] = []
    for row in rows:
        documents, _ = _lane_documents(row)
        for metric, aliases in METRIC_ALIASES[str(row["lane_id"])].items():
            match = _candidate_values(documents, aliases)[0]
            observations.append(
                {
                    "eval_contract": "eval-v2",
                    "experiment_id": "m0_reference_projection_v1b",
                    "state": "M0",
                    "parent_state": None,
                    "arm": "baseline",
                    "seed": None,
                    "checkpoint_id": "m0_parent",
                    "lane": row["lane_id"],
                    "family": row["lane_id"],
                    "task_id": row["lane_id"],
                    "task_version": "source_declared",
                    "dataset_id": "source_declared",
                    "dataset_revision": "source_declared",
                    "split": "source_declared",
                    "prompt_id": None,
                    "fewshot": None,
                    "metric": metric,
                    "filter": "source_declared",
                    "role": "secondary" if row["lane_id"] == "exact_prefix" else "primary",
                    "value": match["value"],
                    "unit": "native_source_unit",
                    "higher_is_better": None,
                    "denominator_name": None,
                    "denominator_value": None,
                    "sample_count": None,
                    "stderr": None,
                    "ci_low": None,
                    "ci_high": None,
                    "uncertainty_method": None,
                    "comparison_reference": "not_applicable_at_m0",
                    "absolute_delta": None,
                    "ratio_to_reference": None,
                    "result_status": "complete",
                    "missing_reason": None,
                    "raw_artifact_path": match["path"],
                    "raw_artifact_sha256": sha256_file(Path(match["path"])),
                }
            )
    _write_parquet(output_root / "checkpoint_registry.parquet", [], CHECKPOINT_FIELDS)
    _write_parquet(output_root / "metric_observations.parquet", observations, METRIC_FIELDS)
    _write_parquet(output_root / "factual_probe_results.parquet", [], FACTUAL_FIELDS)
    write_json(output_root / "m0_metric_summary.json", {"status": "complete", "observation_count": len(observations)})
    manifest = {
        "schema_version": 1,
        "status": "normalization_complete_pending_m0_interpretation",
        "config_path": plan["config_path"],
        "config_sha256": plan["config_sha256"],
        "audit": audit,
        "metric_rows_written": len(observations),
        "rescore_performed": False,
        "historical_sources_mutated": False,
    }
    write_json(output_root / "normalization_manifest.json", manifest)
    files = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(output_root.iterdir())
        if path.name != "final_inventory.json"
    ]
    write_json(output_root / "final_inventory.json", {"schema_version": 1, "inventory_excludes": ["final_inventory.json"], "file_count": len(files), "files": files})
    return manifest
