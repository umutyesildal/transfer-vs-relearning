from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

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
        "bits_per_byte": ("results.wikitext.bits_per_byte,none",),
        "word_perplexity": ("results.wikitext.word_perplexity,none",),
        "byte_perplexity": ("results.wikitext.byte_perplexity,none",),
    },
    "english_grammar_blimp": {
        "accuracy": ("results.blimp.acc,none",),
    },
    "english_capability": {
        "hellaswag_acc_norm": ("results.hellaswag.acc_norm,none",),
    },
    "turkish_capability": {
        "accuracy": ("results.turblimp_core.acc_norm,none",),
    },
    "turkish_perplexity": {
        "bits_per_byte": ("summary.primary_cross_tokenizer_metric=bits_per_byte.bits_per_byte",),
        # The source evaluator calls this token perplexity; the canonical eval-v2
        # long table retains word_perplexity for compatibility and stores the source
        # metric identity in raw_artifact_json_path.
        "word_perplexity": ("summary.primary_cross_tokenizer_metric=bits_per_byte.perplexity",),
        "byte_perplexity": ("summary.primary_cross_tokenizer_metric=bits_per_byte.byte_perplexity",),
    },
    "factual_access": {
        "top1_accuracy": ("summary.top1/summary.probes",),
        "robust_fact_intersection": ("all_cell_intersections.csv.all_cell_intersection/n",),
    },
    "generation_integrity": {
        "empty_generation_rate": ("summary.generation.empty_generation_count/summary.generation.prompt_count",),
        "repeated_3gram_fraction": ("summary.generation.mean_repeated_3gram_fraction",),
    },
    "exact_prefix": {
        # Historical exact-prefix lane_result.json exposes this one unambiguous
        # primary ranking value. Generic top1_accuracy is intentionally excluded:
        # summary_metrics.json contains chance and sensitivity top-1 values too.
        "exact_prefix_accuracy": ("primary_mean_logprob_top1_accuracy",),
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


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _match(path: Path, location: str, value: Any, *, source_metric: str | None = None,
           denominator_name: str | None = None, denominator_value: float | None = None) -> dict[str, Any] | None:
    if not _numeric(value):
        return None
    return {
        "path": str(path),
        "json_path": location,
        "value": float(value),
        "source_metric": source_metric or location,
        "denominator_name": denominator_name,
        "denominator_value": denominator_value,
    }


def _path_match(
    documents: list[tuple[Path, dict[str, Any]]],
    path_parts: tuple[str, ...],
    *,
    marker: tuple[str, Any] | None = None,
    source_metric: str | None = None,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for path, payload in documents:
        if marker is not None and payload.get(marker[0]) != marker[1]:
            continue
        value: Any = payload
        for part in path_parts:
            if not isinstance(value, dict) or part not in value:
                value = None
                break
            value = value[part]
        match = _match(path, ".".join(path_parts), value, source_metric=source_metric)
        if match is not None:
            matches.append(match)
    return matches


def _lm_eval_match(
    documents: list[tuple[Path, dict[str, Any]]], task: str, metric_key: str,
) -> list[dict[str, Any]]:
    return _path_match(documents, ("results", task, metric_key), source_metric=metric_key)


def _source_summary_matches(
    documents: list[tuple[Path, dict[str, Any]]], field: str,
) -> list[dict[str, Any]]:
    return _path_match(
        documents,
        (field,),
        marker=("primary_cross_tokenizer_metric", "bits_per_byte"),
        source_metric=field,
    )


def _factual_matches(
    documents: list[tuple[Path, dict[str, Any]]], tables: list[tuple[Path, list[dict[str, str]]]],
) -> dict[str, list[dict[str, Any]]]:
    top1: list[dict[str, Any]] = []
    for path, payload in documents:
        if "top1" not in payload or "probes" not in payload:
            continue
        denominator = payload.get("probes")
        if _numeric(payload.get("top1")) and _numeric(denominator) and float(denominator) > 0:
            top1.append(
                _match(
                    path,
                    "top1/probes",
                    float(payload["top1"]) / float(denominator),
                    source_metric="top1",
                    denominator_name="probes",
                    denominator_value=float(denominator),
                )
            )
    robust: list[dict[str, Any]] = []
    for path, rows in tables:
        if path.name != "all_cell_intersections.csv" or not rows:
            continue
        if not all("all_cell_intersection" in row and "n" in row for row in rows):
            continue
        numerator = sum(float(row["all_cell_intersection"]) for row in rows)
        denominator = sum(float(row["n"]) for row in rows)
        if denominator > 0:
            robust.append(
                _match(
                    path,
                    "sum(all_cell_intersection)/sum(n)",
                    numerator / denominator,
                    source_metric="all_cell_intersection",
                    denominator_name="sum(n)",
                    denominator_value=denominator,
                )
            )
    return {"top1_accuracy": top1, "robust_fact_intersection": robust}


def _generation_matches(documents: list[tuple[Path, dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    empty: list[dict[str, Any]] = []
    repeated: list[dict[str, Any]] = []
    for path, payload in documents:
        generation = payload.get("generation")
        if not isinstance(generation, dict):
            continue
        prompt_count = generation.get("prompt_count")
        empty_count = generation.get("empty_generation_count")
        if _numeric(prompt_count) and float(prompt_count) > 0:
            match = _match(
                path,
                "generation.empty_generation_count/generation.prompt_count",
                float(empty_count) / float(prompt_count) if _numeric(empty_count) else None,
                source_metric="empty_generation_count",
                denominator_name="prompt_count",
                denominator_value=float(prompt_count),
            )
            if match is not None:
                empty.append(match)
        match = _match(
            path,
            "generation.mean_repeated_3gram_fraction",
            generation.get("mean_repeated_3gram_fraction"),
            source_metric="mean_repeated_3gram_fraction",
        )
        if match is not None:
            repeated.append(match)
    return {"empty_generation_rate": empty, "repeated_3gram_fraction": repeated}


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


def _lane_documents(
    row: dict[str, Any],
) -> tuple[list[tuple[Path, dict[str, Any]]], dict[str, Any], list[tuple[Path, list[dict[str, str]]]]]:
    lane_path = Path(str(row["source_path"]))
    lane_sha = row.get("sha256", row.get("source_sha256"))
    _verify(lane_path, str(lane_sha), "lane result")
    lane = _json(lane_path)
    if lane.get("status") != "complete":
        raise ValueError(f"Lane is not complete: {row.get('model_id')}:{row.get('lane_id')}")
    # Canonical eval-v2 lanes carry a process return code; historical exact-prefix
    # supplements predate that field and are complete by status plus hash binding.
    if row.get("lane_id") != "exact_prefix" and lane.get("returncode") != 0:
        raise ValueError(f"Canonical lane returncode is not zero: {row.get('model_id')}:{row.get('lane_id')}")
    documents: list[tuple[Path, dict[str, Any]]] = [(lane_path, lane)]
    tables: list[tuple[Path, list[dict[str, str]]]] = []
    for artifact in lane.get("artifacts", []):
        item = _mapping(artifact, "lane artifact")
        artifact_path = Path(str(item.get("path", "")))
        _verify(artifact_path, str(item.get("sha256")), "lane artifact")
        if artifact_path.suffix.casefold() == ".json" and artifact_path.stat().st_size <= 10 * 1024 * 1024:
            try:
                documents.append((artifact_path, _json(artifact_path)))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        elif artifact_path.suffix.casefold() == ".csv" and artifact_path.stat().st_size <= 10 * 1024 * 1024:
            try:
                tables.append((artifact_path, _csv_rows(artifact_path)))
            except (UnicodeDecodeError, csv.Error):
                continue
    return documents, lane, tables


def _metric_matches(
    lane_id: str,
    documents: list[tuple[Path, dict[str, Any]]],
    tables: list[tuple[Path, list[dict[str, str]]]],
) -> dict[str, list[dict[str, Any]]]:
    if lane_id == "english_retention_wikitext":
        return {
            "bits_per_byte": _lm_eval_match(documents, "wikitext", "bits_per_byte,none"),
            "word_perplexity": _lm_eval_match(documents, "wikitext", "word_perplexity,none"),
            "byte_perplexity": _lm_eval_match(documents, "wikitext", "byte_perplexity,none"),
        }
    if lane_id == "english_grammar_blimp":
        return {"accuracy": _lm_eval_match(documents, "blimp", "acc,none")}
    if lane_id == "english_capability":
        return {"hellaswag_acc_norm": _lm_eval_match(documents, "hellaswag", "acc_norm,none")}
    if lane_id == "turkish_capability":
        return {"accuracy": _lm_eval_match(documents, "turblimp_core", "acc_norm,none")}
    if lane_id == "turkish_perplexity":
        return {
            "bits_per_byte": _source_summary_matches(documents, "bits_per_byte"),
            "word_perplexity": _source_summary_matches(documents, "perplexity"),
            "byte_perplexity": _source_summary_matches(documents, "byte_perplexity"),
        }
    if lane_id == "factual_access":
        return _factual_matches(documents, tables)
    if lane_id == "generation_integrity":
        return _generation_matches(documents)
    if lane_id == "exact_prefix":
        return {
            "exact_prefix_accuracy": _path_match(
                documents,
                ("primary_mean_logprob_top1_accuracy",),
                source_metric="primary_mean_logprob_top1_accuracy",
            )
        }
    raise ValueError(f"Unknown lane: {lane_id}")


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
        documents, lane, tables = _lane_documents(row)
        metric_matches = _metric_matches(lane_id, documents, tables)
        for metric, aliases in METRIC_ALIASES[lane_id].items():
            matches = metric_matches[metric]
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
                    "source_metric": match.get("source_metric"),
                    "denominator_name": match.get("denominator_name"),
                    "denominator_value": match.get("denominator_value"),
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
        "metric_rows": metric_rows,
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
    observations: list[dict[str, Any]] = []
    for match in audit["metric_rows"]:
        observations.append(
            {
                    "eval_contract": "eval-v2",
                    "experiment_id": "m0_reference_projection_v1b",
                    "state": "M0",
                    "parent_state": None,
                    "arm": "baseline",
                    "seed": None,
                    "checkpoint_id": "m0_parent",
                    "lane": match["lane_id"],
                    "family": match["lane_id"],
                    "task_id": match["lane_id"],
                    "task_version": "source_declared",
                    "dataset_id": "source_declared",
                    "dataset_revision": "source_declared",
                    "split": "source_declared",
                    "prompt_id": None,
                    "fewshot": None,
                    "metric": match["metric"],
                    "filter": "source_declared",
                    "role": "secondary" if match["lane_id"] == "exact_prefix" else "primary",
                    "value": match["value"],
                    "unit": "native_source_unit",
                    "higher_is_better": None,
                    "denominator_name": match.get("denominator_name"),
                    "denominator_value": match.get("denominator_value"),
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
