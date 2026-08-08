"""Bounded local vngrs preparation pipeline.

This module is preparation-only: it accepts already available records and emits compact,
text-free evidence.  It has no network client, downloader, materializer, evaluator download or
model access.  Scientific-profile calls fail closed whenever a required gate is unresolved.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol

from .contamination import ContaminationPattern, benchmark_overlap, scan_contamination
from .dedup import NEAR_DEDUP_VERSION, exact_deduplicate, near_duplicate_summary
from .manifest import (
    manifest_row_from_processed,
    serialize_record_manifest,
    serialize_request_ledger,
    validate_record_manifest,
    validate_final_evidence_relationships,
    validate_final_sampling_schedule,
    validate_request_ledger,
    validate_request_ledger_aggregate,
    validate_request_response_bindings,
)
from .metadata import (
    FROZEN_SELECTED_SHARD_PATHS,
    VNGRS_REPOSITORY,
    VNGRS_REVISION,
    canonical_json_bytes,
    canonical_json_sha256,
    validate_final_source_evidence,
)
from .outputs import (
    validate_artifact_payloads,
    validate_final_audit,
    validate_output_artifact_manifest,
    output_artifact_manifest_sha256,
)
from .quality import ADULT_EVALUATOR_SCOPE, PII_EVALUATOR_SCOPE, QualityConfig, detect_pii, evaluate_quality
from .records import decoded_text_character_count, normalize_text, serialized_record_bytes, source_identity_key, stable_record_id
from .split import assign_document_disjoint, assert_document_disjoint


SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
FINAL_SAMPLE_TARGET = 10_000


def _metric_json(payload: bytes, path: str) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(payload, bytes):
        return None, f"{path}: payload is not bytes"
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"{path}: invalid JSON ({exc})"
    if not isinstance(value, dict):
        return None, f"{path}: metric payload must be a JSON object"
    if canonical_json_bytes(value) != payload:
        return None, f"{path}: metric payload is not canonical JSON"
    return value, None


def _canonical_metric_input(rows: Iterable[Mapping[str, Any]], fields: tuple[str, ...]) -> str:
    values = [{field: row.get(field) for field in fields} for row in rows]
    return canonical_json_sha256(values)


def _validate_metric_payloads(
    raw_manifest: list[dict[str, Any]],
    request_rows: list[dict[str, Any]],
    source_evidence: Mapping[str, Any],
    artifact_payloads: Mapping[str, bytes],
) -> dict[str, Any]:
    """Validate canonical metric payloads and recompute every derivable final gate input."""

    errors: list[str] = []
    required = (
        "selection_plan.json",
        "raw_population_metrics.json",
        "retained_population_metrics.json",
        "dedup_metrics.json",
        "contamination_overlap_metrics.json",
    )
    payloads: dict[str, dict[str, Any]] = {}
    for path in required:
        value, error = _metric_json(artifact_payloads.get(path), path)
        if error:
            errors.append(error)
        elif value is not None:
            payloads[path] = value
    record_manifest_sha = hashlib.sha256(serialize_record_manifest(raw_manifest, expected_count=FINAL_SAMPLE_TARGET).encode()).hexdigest()
    request_ledger_sha = hashlib.sha256(serialize_request_ledger(request_rows).encode()).hexdigest()
    expected_record_payload = serialize_record_manifest(raw_manifest, expected_count=FINAL_SAMPLE_TARGET).encode()
    expected_request_payload = serialize_request_ledger(request_rows).encode()
    if artifact_payloads.get("record_manifest.jsonl") != expected_record_payload:
        errors.append("record_manifest.jsonl: actual payload does not equal the validated raw manifest")
    if artifact_payloads.get("request_ledger.jsonl") != expected_request_payload:
        errors.append("request_ledger.jsonl: actual payload does not equal the validated request ledger")
    retained = [row for row in raw_manifest if row.get("retention_status") == "retained"]
    retained_input = _canonical_metric_input(retained, ("stable_source_row_document_id", "normalized_text_sha256"))
    overlap_input = _canonical_metric_input(
        raw_manifest, ("stable_source_row_document_id", "normalized_text_sha256", "benchmark_overlap_status")
    )
    split_input = _canonical_metric_input(raw_manifest, ("stable_source_row_document_id", "split"))
    exact_duplicate_count = FINAL_SAMPLE_TARGET - len({row.get("exact_dedup_key") for row in raw_manifest})
    retained_quality_rate = len(retained) / FINAL_SAMPLE_TARGET
    turkish_labels = {"tur", "tr", "turkish"}
    raw_turkish_count = sum(str(row.get("lid_top1_language", "")).casefold() in turkish_labels for row in raw_manifest)
    raw_unknown_lid_count = sum(
        row.get("lid_status") != "verified" or not str(row.get("lid_top1_language", "")).strip()
        for row in raw_manifest
    )
    overlap_count = sum(row.get("benchmark_overlap_status") != "clean" for row in raw_manifest)
    contamination_count = sum(row.get("synthetic_contamination_status") != "clean" for row in raw_manifest)
    tier3_count = sum("tier3" in row.get("synthetic_contamination_tiers", []) for row in raw_manifest)
    tier2_retained_count = sum("tier2" in row.get("synthetic_contamination_tiers", []) for row in retained)
    retained_pii_count = sum(row.get("pii_status") != "clean" for row in retained)
    retained_quality_bad_count = sum(row.get("quality_status") != "accepted" for row in retained)
    split_values = {row.get("split") for row in raw_manifest}
    split_disjoint = split_values.issubset({"train", "held_out"}) and len({row.get("stable_source_row_document_id") for row in raw_manifest}) == len(raw_manifest)

    def require_equal(path: str, payload: Mapping[str, Any], field: str, expected: Any) -> None:
        if payload.get(field) != expected:
            errors.append(f"{path}: {field} does not match recomputed value")

    plan = payloads.get("selection_plan.json")
    if plan is not None:
        require_equal(plan and "selection_plan.json", plan, "source_evidence_sha256", source_evidence.get("evidence_sha256"))
        require_equal(plan and "selection_plan.json", plan, "selection_payload_sha256", source_evidence.get("selection_payload_sha256"))
        require_equal(plan and "selection_plan.json", plan, "immutable_revision", VNGRS_REVISION)
        require_equal(plan and "selection_plan.json", plan, "selected_paths", list(FROZEN_SELECTED_SHARD_PATHS))

    raw_metrics = payloads.get("raw_population_metrics.json")
    if raw_metrics is not None:
        for field, expected in {
            "record_manifest_sha256": record_manifest_sha,
            "request_ledger_sha256": request_ledger_sha,
            "source_repository": VNGRS_REPOSITORY,
            "immutable_revision": VNGRS_REVISION,
            "raw_count": FINAL_SAMPLE_TARGET,
            "sample_index_count": FINAL_SAMPLE_TARGET,
            "sample_index_min": 0,
            "sample_index_max": FINAL_SAMPLE_TARGET - 1,
            "source_identity_unique": True,
            "raw_turkish_count": raw_turkish_count,
            "raw_unknown_lid_count": raw_unknown_lid_count,
        }.items():
            require_equal("raw_population_metrics.json", raw_metrics, field, expected)
        require_equal("raw_population_metrics.json", raw_metrics, "raw_turkish_fraction", raw_turkish_count / FINAL_SAMPLE_TARGET)

    retained_metrics = payloads.get("retained_population_metrics.json")
    if retained_metrics is not None:
        for field, expected in {
            "record_manifest_sha256": record_manifest_sha,
            "raw_count": FINAL_SAMPLE_TARGET,
            "retained_count": len(retained),
            "retained_pii_count": retained_pii_count,
            "retained_quality_bad_count": retained_quality_bad_count,
            "tier3_contamination_count": sum(
                "tier3" in row.get("synthetic_contamination_tiers", []) for row in retained
            ),
        }.items():
            require_equal("retained_population_metrics.json", retained_metrics, field, expected)
        require_equal("retained_population_metrics.json", retained_metrics, "retained_quality_rate", retained_quality_rate)

    dedup_metrics = payloads.get("dedup_metrics.json")
    near_affected_count: int | None = None
    near_affected_rate: float | None = None
    if dedup_metrics is not None:
        for field, expected in {
            "record_manifest_sha256": record_manifest_sha,
            "raw_count": FINAL_SAMPLE_TARGET,
            "exact_duplicate_count": exact_duplicate_count,
            "exact_duplicate_rate": exact_duplicate_count / FINAL_SAMPLE_TARGET,
            "near_dedup_input_sha256": retained_input,
            "near_dedup_feature_cap": None,
        }.items():
            require_equal("dedup_metrics.json", dedup_metrics, field, expected)
        if not isinstance(dedup_metrics.get("near_dedup_version"), str) or not dedup_metrics["near_dedup_version"]:
            errors.append("dedup_metrics.json: near_dedup_version is missing")
        affected = dedup_metrics.get("near_dedup_affected_record_rate")
        if not isinstance(affected, (int, float)) or isinstance(affected, bool):
            errors.append("dedup_metrics.json: near_dedup_affected_record_rate is missing")
        affected_ids = dedup_metrics.get("near_dedup_affected_record_ids")
        pairs = dedup_metrics.get("near_dedup_pairs")
        if dedup_metrics.get("near_dedup_evidence_class") != "hash_bound_execution_evidence":
            errors.append("dedup_metrics.json: near-dedup evidence class is not hash_bound_execution_evidence")
        if not isinstance(affected_ids, list) or any(not isinstance(value, str) for value in affected_ids):
            errors.append("dedup_metrics.json: affected-record evidence is missing or malformed")
            affected_ids = []
        if affected_ids != sorted(set(affected_ids)):
            errors.append("dedup_metrics.json: affected-record IDs are not sorted and unique")
        if not isinstance(pairs, list):
            errors.append("dedup_metrics.json: near-dedup pair evidence is missing")
            pairs = []
        normalized_pairs: list[tuple[str, str]] = []
        if isinstance(pairs, list):
            for pair in pairs:
                if not isinstance(pair, list) or len(pair) != 2 or any(not isinstance(value, str) for value in pair):
                    errors.append("dedup_metrics.json: near-dedup pair evidence is malformed")
                    continue
                normalized = tuple(pair)
                if normalized[0] >= normalized[1] or normalized in normalized_pairs:
                    errors.append("dedup_metrics.json: near-dedup pairs are not canonical unique pairs")
                normalized_pairs.append(normalized)
        pair_ids = sorted({value for pair in normalized_pairs for value in pair})
        retained_ids = {str(row["stable_source_row_document_id"]) for row in retained}
        if not set(pair_ids).issubset(retained_ids) or set(affected_ids) != set(pair_ids):
            errors.append("dedup_metrics.json: pair/affected-record evidence does not reconcile")
        near_affected_count = len(affected_ids)
        near_affected_rate = near_affected_count / len(retained) if retained else None
        require_equal("dedup_metrics.json", dedup_metrics, "near_dedup_affected_record_count", near_affected_count)
        require_equal("dedup_metrics.json", dedup_metrics, "near_dedup_affected_record_rate", near_affected_rate)

    contamination_metrics = payloads.get("contamination_overlap_metrics.json")
    if contamination_metrics is not None:
        for field, expected in {
            "record_manifest_sha256": record_manifest_sha,
            "request_ledger_sha256": request_ledger_sha,
            "benchmark_overlap_input_sha256": overlap_input,
            "split_input_sha256": split_input,
            "benchmark_overlap_count": overlap_count,
            "synthetic_contamination_count": contamination_count,
            "tier2_retained_count": tier2_retained_count,
            "split_document_disjoint": split_disjoint,
            "split_namespace": "vngrs_primary_in_domain_heldout_v2",
            "split_seed": 42,
        }.items():
            require_equal("contamination_overlap_metrics.json", contamination_metrics, field, expected)
        require_equal("contamination_overlap_metrics.json", contamination_metrics, "tier3_contamination_count", tier3_count)

    return {
        "record_manifest_sha256": record_manifest_sha,
        "request_ledger_sha256": request_ledger_sha,
        "raw_turkish_fraction": raw_turkish_count / FINAL_SAMPLE_TARGET,
        "raw_unknown_lid_count": raw_unknown_lid_count,
        "retained_count": len(retained),
        "retained_quality_rate": retained_quality_rate,
        "retained_pii_count": retained_pii_count,
        "retained_quality_bad_count": retained_quality_bad_count,
        "exact_duplicate_count": exact_duplicate_count,
        "exact_duplicate_rate": exact_duplicate_count / FINAL_SAMPLE_TARGET,
        "benchmark_overlap_count": overlap_count,
        "synthetic_contamination_count": contamination_count,
        "tier3_contamination_count": tier3_count,
        "tier2_retained_count": tier2_retained_count,
        "near_dedup_affected_record_count": near_affected_count,
        "near_dedup_affected_record_rate": near_affected_rate,
        "split_document_disjoint": split_disjoint,
        "payloads_canonical_and_linked": not errors,
        "errors": errors,
    }


@dataclass(frozen=True)
class VngrsPreparationConfig:
    source_revision: str
    max_records: int = 10_000
    sample_target_records: int = 10_000
    enforce_exact_sample: bool = False
    scientific_profile: bool = False
    source_integrity_verified: bool = False
    validation_fraction: float = 0.02
    seed: int = 42
    near_duplicate_threshold: float = 0.80
    near_duplicate_num_perm: int = 128
    near_duplicate_num_bands: int = 32
    near_duplicate_rows_per_band: int = 4
    max_near_duplicate_candidates: int = 1_000_000
    max_near_duplicate_pairs: int = 100_000
    accepted_lid_labels: frozenset[str] = frozenset({"tur", "tr", "turkish"})
    min_lid_confidence: float = 0.80
    quality: QualityConfig = QualityConfig()


@dataclass(frozen=True)
class LidResult:
    status: str
    top1_language: str | None = None
    confidence: float | None = None
    mixed_line_flag: bool | None = None
    evaluator_id: str | None = None
    evaluator_sha256: str | None = None


class LidAdapter(Protocol):
    def classify(self, text: str) -> LidResult: ...


class FailClosedLidAdapter:
    """Default adapter: no LID claim is made without a frozen evaluator artifact."""

    def classify(self, text: str) -> LidResult:
        del text
        return LidResult(status="blocked_missing_frozen_evaluator")


def _validate_source_ids(records: list[Mapping[str, Any]]) -> None:
    source_ids: list[tuple[str, str]] = []
    for record in records:
        try:
            source_ids.append(source_identity_key(record))
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("duplicate composite source key (corpus, original_id): wave fails closed")


def _lid_retention_decision(lid: LidResult, config: VngrsPreparationConfig) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if lid.status != "verified":
        reasons.append("lid_status_unresolved")
    if not lid.evaluator_id or not lid.evaluator_sha256 or SHA256_RE.fullmatch(lid.evaluator_sha256) is None:
        reasons.append("lid_evaluator_identity_unresolved")
    if (lid.top1_language or "").casefold() not in {label.casefold() for label in config.accepted_lid_labels}:
        reasons.append("lid_non_turkish_or_unaccepted_label")
    if lid.confidence is None or lid.confidence < config.min_lid_confidence:
        reasons.append("lid_confidence_below_threshold")
    return not reasons, tuple(dict.fromkeys(reasons))


def _overlap_ids(rows: Iterable[Mapping[str, Any]]) -> set[str]:
    return {str(row["record_id"]) for row in rows}


def _evaluate_contract_gate(
    *,
    config: VngrsPreparationConfig,
    processed: list[Mapping[str, Any]],
    retained: list[Mapping[str, Any]],
    raw_manifest_validation: Mapping[str, Any],
    benchmark_overlaps: Mapping[str, list[Mapping[str, Any]]],
    near_duplicates: Mapping[str, Any],
    exact_duplicate_count: int,
    split_disjoint: bool,
) -> dict[str, Any]:
    scientific = config.scientific_profile or config.enforce_exact_sample
    if not scientific:
        return {
            "status": "DIAGNOSTIC_ONLY",
            "scientific_profile": False,
            "blocking_reasons": [],
            "gate_results": {},
        }
    reasons: list[str] = []
    raw_count = len(processed)
    retained_count = len(retained)
    raw_target_exact = raw_count == config.sample_target_records
    if not raw_target_exact:
        reasons.append("incomplete_exact_raw_sample")
    if not raw_manifest_validation["complete"]:
        reasons.append("raw_manifest_schema_or_cardinality_incomplete")
    if any(item["lid"]["status"] != "verified" for item in processed):
        reasons.append("lid_status_unresolved")
    if any(
        not item["lid"].get("evaluator_id")
        or not item["lid"].get("evaluator_sha256")
        or SHA256_RE.fullmatch(str(item["lid"].get("evaluator_sha256"))) is None
        for item in processed
    ):
        reasons.append("lid_evaluator_identity_unresolved_in_raw_manifest")
    turkish_count = sum(
        (item["lid"].get("top1_language") or "").casefold() in {label.casefold() for label in config.accepted_lid_labels}
        for item in processed
    )
    turkish_fraction = turkish_count / raw_count if raw_count else None
    if turkish_fraction is None or turkish_fraction < 0.95:
        reasons.append("raw_turkish_lid_threshold_failed")
    if any(not item["lid"]["accepted_for_retention"] for item in retained):
        reasons.append("retained_lid_decision_inconsistent")
    if retained_count and near_duplicates.get("affected_record_rate") is None:
        reasons.append("near_dedup_rate_unresolved")
    if raw_count and not retained_count:
        reasons.append("retained_population_empty_or_unresolved")
    if raw_count and retained_count / raw_count < 0.50:
        reasons.append("retained_quality_rate_below_threshold")
    if near_duplicates.get("affected_record_rate") is not None and near_duplicates["affected_record_rate"] > 0.05:
        reasons.append("near_dedup_threshold_failed")
    if raw_count and exact_duplicate_count / raw_count > 0.10:
        reasons.append("exact_dedup_threshold_failed")
    if not split_disjoint:
        reasons.append("document_disjoint_split_failed")
    if any(benchmark_overlaps.values()):
        reasons.append("benchmark_overlap_nonzero")
    if any(item["contamination"]["status"] != "clean" for item in retained):
        reasons.append("retained_synthetic_contamination")
    if any(item["quality"]["accepted"] is False for item in retained):
        reasons.append("retained_quality_gate_inconsistent")
    if any(item["pii_types"] for item in retained):
        reasons.append("retained_pii_gate_inconsistent")
    return {
        # This is a local preparation-stage status.  It is deliberately never the
        # final scientific decision; only evaluate_final_contract may return PASS.
        "status": "DIAGNOSTIC_ONLY" if not reasons else "BLOCKED",
        "scientific_profile": True,
        "blocking_reasons": sorted(set(reasons)),
        "gate_results": {
            "raw_count_exact": raw_target_exact,
            "raw_manifest_complete": bool(raw_manifest_validation["complete"]),
            "source_integrity_claim_not_final_evidence": bool(config.source_integrity_verified),
            "raw_turkish_lid_fraction": turkish_fraction,
            "raw_turkish_lid_threshold_pass": turkish_fraction is not None and turkish_fraction >= 0.95,
            "retained_quality_rate": retained_count / raw_count if raw_count else None,
            "retained_quality_threshold_pass": raw_count > 0 and retained_count / raw_count >= 0.50,
            "near_dedup_threshold_pass": near_duplicates.get("affected_record_rate") is not None and near_duplicates["affected_record_rate"] <= 0.05,
            "exact_dedup_threshold_pass": raw_count == 0 or exact_duplicate_count / raw_count <= 0.10,
            "benchmark_overlap_zero": not any(benchmark_overlaps.values()),
            "document_disjoint_split": split_disjoint,
        },
    }


def prepare_records(
    records: Iterable[Mapping[str, Any]],
    *,
    config: VngrsPreparationConfig,
    lid_adapter: LidAdapter | None = None,
    contamination_patterns: Iterable[ContaminationPattern] = (),
    benchmark_item_hashes: Iterable[str] = (),
    benchmark_item_ids: Iterable[str] = (),
) -> dict[str, Any]:
    """Prepare a bounded sample and return exact raw/retained denominators plus compact evidence."""

    if config.max_records <= 0 or config.sample_target_records <= 0:
        raise ValueError("max_records must be positive")
    input_records = [dict(record) for record in records]
    if len(input_records) > config.max_records:
        raise ValueError("input exceeds frozen max_records bound")
    _validate_source_ids(input_records)
    adapter = lid_adapter or FailClosedLidAdapter()
    patterns = tuple(contamination_patterns)
    processed: list[dict[str, Any]] = []
    for index, record in enumerate(input_records):
        text = record.get("text")
        if not isinstance(text, (str, bytes)):
            raise ValueError(f"record {index} has no valid text")
        normalized = normalize_text(text)
        identity = source_identity_key(record)
        record_id = stable_record_id(
            record, source_revision=config.source_revision, shard_path=str(record.get("shard_path", "")),
            row_group_index=int(record.get("row_group_index", 0)), row_index=int(record.get("row_index", index)),
        )
        lid = adapter.classify(normalized.text)
        lid_accepted, lid_reasons = _lid_retention_decision(lid, config)
        quality = evaluate_quality(normalized.text, config.quality)
        pii_types = detect_pii(normalized.text)
        contamination = scan_contamination(normalized.text, patterns)
        rejection_reasons = list(lid_reasons)
        rejection_reasons.extend(f"quality_{reason}" for reason in quality.reasons)
        rejection_reasons.extend(f"pii_{reason}" for reason in pii_types)
        if contamination["status"] != "clean":
            rejection_reasons.append("synthetic_contamination")
        processed.append(
            {
                "record_id": record_id,
                "source_identity_key": {"corpus": identity[0], "original_id": identity[1]},
                "stable_source_row_document_id": str(record.get("stable_source_row_document_id", record_id)),
                "original_id": identity[1],
                "corpus": identity[0],
                "source_repo": record.get("source_repo"),
                "immutable_revision": record.get("immutable_revision", config.source_revision),
                "request_id": record.get("request_id"),
                "record_index_within_response": record.get("record_index_within_response"),
                "sample_index": record.get("sample_index"),
                "retrieved_at_utc": record.get("retrieved_at_utc"),
                "shard_path": record.get("shard_path"),
                "exact_serialized_record_payload_bytes": len(serialized_record_bytes(record)),
                "normalized_text": normalized.text,
                "normalized_text_sha256": normalized.sha256,
                "raw_text_character_count": decoded_text_character_count(text),
                "normalized_text_character_count": len(normalized.text),
                "normalization_version": "nfc_control_whitespace_v1",
                "normalization": {
                    "utf8_replacement_count": normalized.utf8_replacement_count,
                    "control_chars_removed": normalized.control_chars_removed,
                    "whitespace_changes": normalized.whitespace_changes,
                },
                "lid": {**lid.__dict__, "accepted_for_retention": lid_accepted, "rejection_reasons": list(lid_reasons)},
                "quality": {
                    "accepted": quality.accepted,
                    "reasons": list(quality.reasons),
                    "metrics": quality.metrics,
                    "threshold_status": quality.threshold_status,
                    "evaluator_scope": quality.evaluator_scope,
                    "adult_evaluator_scope": ADULT_EVALUATOR_SCOPE,
                },
                "pii_types": list(pii_types),
                "pii_evaluator_scope": PII_EVALUATOR_SCOPE,
                "contamination": contamination,
                "retention_status": "pending",
                "rejection_reason_codes": rejection_reasons,
                "raw_eligible": True,
            }
        )
    exact_keepers, exact_duplicates = exact_deduplicate(processed)
    duplicate_map = {item["duplicate_record_id"]: item["keeper_record_id"] for item in exact_duplicates}
    exact_keeper_ids = {item["record_id"] for item in exact_keepers}
    retained = [
        item for item in exact_keepers
        if item["lid"]["accepted_for_retention"] and item["quality"]["accepted"]
        and not item["pii_types"] and item["contamination"]["status"] == "clean"
    ]
    retained_ids = {item["record_id"] for item in retained}
    for item in processed:
        if item["record_id"] in duplicate_map:
            item["retention_status"] = "excluded"
            item["rejection_reason_codes"].append("exact_duplicate")
            item["exact_duplicate_keeper_record_id"] = duplicate_map[item["record_id"]]
        elif item["record_id"] in retained_ids:
            item["retention_status"] = "retained"
        elif item["record_id"] in exact_keeper_ids:
            item["retention_status"] = "excluded"
        else:
            raise AssertionError("processed record is neither an exact keeper nor a duplicate")
        item["rejection_reason_codes"] = sorted(set(item["rejection_reason_codes"]))
    retained_with_split = assign_document_disjoint(retained, seed=config.seed, validation_fraction=config.validation_fraction)
    assert_document_disjoint(retained_with_split)
    raw_overlap = benchmark_overlap(processed, benchmark_item_hashes=benchmark_item_hashes, benchmark_item_ids=benchmark_item_ids)
    raw_exact_canonical_overlap = benchmark_overlap(exact_keepers, benchmark_item_hashes=benchmark_item_hashes, benchmark_item_ids=benchmark_item_ids)
    retained_overlap = benchmark_overlap(retained_with_split, benchmark_item_hashes=benchmark_item_hashes, benchmark_item_ids=benchmark_item_ids)
    overlap_surfaces = {
        "raw_sampled": raw_overlap,
        "raw_exact_canonical": raw_exact_canonical_overlap,
        "retained": retained_overlap,
    }
    near_duplicates = near_duplicate_summary(
        retained_with_split, threshold=config.near_duplicate_threshold, num_perm=config.near_duplicate_num_perm,
        seed=config.seed, num_bands=config.near_duplicate_num_bands, rows_per_band=config.near_duplicate_rows_per_band,
        max_candidate_pairs=config.max_near_duplicate_candidates, max_output_pairs=config.max_near_duplicate_pairs,
    )
    overlap_ids = {key: _overlap_ids(value) for key, value in overlap_surfaces.items()}
    split_by_id = {str(item["record_id"]): item.get("split") for item in retained_with_split}
    raw_manifest = [
        manifest_row_from_processed(
            item, split=split_by_id.get(str(item["record_id"])), near_dedup_version=NEAR_DEDUP_VERSION,
            benchmark_overlap_status="overlap" if str(item["record_id"]) in overlap_ids["raw_sampled"] else "clean",
        )
        for item in processed
    ]
    retained_manifest = [row for row in raw_manifest if row["retention_status"] == "retained"]
    manifest_validation = validate_record_manifest(
        raw_manifest,
        expected_count=config.sample_target_records if (config.scientific_profile or config.enforce_exact_sample) else None,
        require_lid_identity=config.scientific_profile or config.enforce_exact_sample,
    )
    gate = _evaluate_contract_gate(
        config=config, processed=processed, retained=retained_with_split, raw_manifest_validation=manifest_validation,
        benchmark_overlaps=overlap_surfaces, near_duplicates=near_duplicates,
        exact_duplicate_count=len(exact_duplicates), split_disjoint=True,
    )
    return {
        "status": gate["status"],
        "gate": gate,
        "raw_denominator": len(processed),
        "raw_manifest_complete": manifest_validation["complete"],
        "manifest_validation": manifest_validation,
        "raw_exact_canonical_denominator": len(exact_keepers),
        "exact_duplicate_count": len(exact_duplicates),
        "retained_denominator": len(retained_with_split),
        "held_out_count": sum(item["split"] == "held_out" for item in retained_with_split),
        "training_count": sum(item["split"] == "train" for item in retained_with_split),
        "lid_statuses": sorted({item["lid"]["status"] for item in processed}),
        "exact_duplicates": exact_duplicates,
        "near_duplicate": near_duplicates,
        "benchmark_overlaps": overlap_surfaces,
        "raw_manifest": raw_manifest,
        "retained_records": retained_manifest,
        "records": raw_manifest,
        "sample_target_records": config.sample_target_records,
    }


def evaluate_final_contract(
    preparation_result: Mapping[str, Any],
    *,
    request_ledger: Iterable[Mapping[str, Any]],
    source_evidence: Mapping[str, Any] | None,
    output_artifact_manifest: Iterable[Mapping[str, Any]] | None,
    output_artifact_manifest_sha256: str | None,
    final_audit: Mapping[str, Any] | None,
    conditional_reasons: Iterable[str] = (),
    artifact_payloads: Mapping[str, bytes] | None = None,
    output_artifact_manifest_payload: bytes | None = None,
    final_audit_payload: bytes | None = None,
    source_evidence_artifact_payloads: Mapping[str, bytes] | None = None,
    request_response_payloads: Mapping[str, bytes] | None = None,
) -> dict[str, Any]:
    """Return the final 151ak decision only after every frozen evidence chain is present.

    The preparation stage cannot produce a final PASS.  In particular, the legacy boolean
    ``source_integrity_verified`` is intentionally not consulted as evidence here.
    """

    blockers: list[str] = []
    raw_manifest = [dict(row) for row in preparation_result.get("raw_manifest", [])]
    if preparation_result.get("sample_target_records") != FINAL_SAMPLE_TARGET:
        blockers.append("caller_sample_target_is_not_immutable_10000")
    request_rows = [dict(row) for row in request_ledger]
    manifest_validation = validate_record_manifest(
        raw_manifest,
        expected_count=FINAL_SAMPLE_TARGET,
        require_lid_identity=True,
        require_operational_fields=True,
    )
    request_validation = validate_request_ledger(request_rows)
    request_aggregate = validate_request_ledger_aggregate(request_rows)
    response_bindings = validate_request_response_bindings(request_rows, request_response_payloads)
    relationships = validate_final_evidence_relationships(raw_manifest, request_rows)
    if not manifest_validation["complete"]:
        blockers.append("record_manifest_incomplete_or_missing_raw_lid_identity")
    if not request_validation["complete"] or not request_aggregate["complete"]:
        blockers.append("request_ledger_schema_or_aggregate_bounds_unresolved")
    if not response_bindings["complete"]:
        blockers.append("request_response_hashes_unbound")
    if not relationships["complete"]:
        blockers.append("record_manifest_request_ledger_relationships_invalid")

    source_validation = validate_final_source_evidence(
        source_evidence,
        artifact_payloads=source_evidence_artifact_payloads,
    )
    if not source_validation["complete"]:
        blockers.append("strict_source_evidence_invalid")
    if isinstance(source_evidence, Mapping) and source_evidence.get("evidence_class") == "STRUCTURAL_SYNTHETIC_CONTROL":
        blockers.append("structural_synthetic_control_not_source_evidence")
    sampling_validation = validate_final_sampling_schedule(raw_manifest, request_rows, source_evidence)
    if not sampling_validation["complete"]:
        blockers.append("sampling_schedule_or_source_windows_invalid")

    manifest_rows: list[dict[str, Any]] | None = None
    artifact_validation: dict[str, Any] | None = None
    if output_artifact_manifest is None or output_artifact_manifest_sha256 is None:
        blockers.append("output_artifact_manifest_missing")
    else:
        try:
            manifest_rows = validate_output_artifact_manifest(output_artifact_manifest)
            if artifact_payloads is None:
                raise ValueError("actual artifact payloads are required")
            artifact_validation = validate_artifact_payloads(
                manifest_rows,
                artifact_payloads,
                output_manifest_payload=output_artifact_manifest_payload,
            )
            if output_artifact_manifest_payload is None:
                raise ValueError("actual output_artifact_manifest.jsonl payload is required")
            computed_manifest_sha = artifact_validation["manifest_sha256"]
            if output_artifact_manifest_sha256 != computed_manifest_sha:
                raise ValueError("caller manifest SHA-256 does not match recomputed canonical bytes")
        except (TypeError, ValueError) as exc:
            blockers.append("output_artifact_payload_chain_invalid")
            artifact_validation = {"errors": [str(exc)]}

    metric_validation: dict[str, Any] = {"errors": ["metric artifact payloads unavailable"]}
    if source_validation["complete"] and artifact_payloads is not None:
        try:
            metric_validation = _validate_metric_payloads(raw_manifest, request_rows, source_evidence, artifact_payloads)
        except (TypeError, ValueError) as exc:
            metric_validation = {"errors": [str(exc)]}
        if not metric_validation.get("payloads_canonical_and_linked"):
            blockers.append("canonical_metric_payloads_unlinked_or_not_recomputed")
    else:
        blockers.append("canonical_metric_payloads_unavailable")

    if (
        final_audit is None
        or manifest_rows is None
        or artifact_validation is None
        or "manifest_sha256" not in artifact_validation
    ):
        blockers.append("final_audit_missing")
    else:
        try:
            validate_final_audit(
                final_audit,
                manifest_rows,
                manifest_sha256=artifact_validation["manifest_sha256"],
                audit_payload=final_audit_payload,
            )
            if final_audit_payload is None:
                raise ValueError("actual final audit payload is required")
        except (TypeError, ValueError) as exc:
            blockers.append("final_audit_chain_invalid")

    # These are recomputed from linked payloads, never imported from preparation_result gate booleans.
    if metric_validation.get("payloads_canonical_and_linked"):
        if metric_validation["raw_turkish_fraction"] < 0.95:
            blockers.append("raw_turkish_lid_threshold_failed")
        if metric_validation["raw_unknown_lid_count"] != 0:
            blockers.append("raw_lid_unknown_or_unresolved")
        if metric_validation["retained_quality_rate"] < 0.50:
            blockers.append("retained_quality_threshold_failed")
        if metric_validation["retained_pii_count"] != 0:
            blockers.append("retained_pii_nonzero")
        if metric_validation["retained_quality_bad_count"] != 0:
            blockers.append("retained_quality_status_inconsistent")
        if metric_validation["tier3_contamination_count"] != 0:
            blockers.append("tier3_contamination_nonzero")
        if metric_validation["retained_count"] and metric_validation["tier2_retained_count"] / metric_validation["retained_count"] > 0.01:
            blockers.append("tier2_contamination_threshold_failed")
        if metric_validation["exact_duplicate_rate"] > 0.10:
            blockers.append("exact_dedup_threshold_failed")
        recomputed_near_rate = metric_validation.get("near_dedup_affected_record_rate")
        if not isinstance(recomputed_near_rate, (int, float)) or isinstance(recomputed_near_rate, bool):
            blockers.append("near_dedup_rate_not_recomputed")
        elif recomputed_near_rate > 0.05:
            blockers.append("near_dedup_threshold_failed")
        if metric_validation["benchmark_overlap_count"] != 0:
            blockers.append("benchmark_overlap_nonzero")
        if not metric_validation["split_document_disjoint"]:
            blockers.append("document_disjoint_split_failed")

    unique_blockers = sorted(set(blockers))
    conditional = sorted(set(str(reason) for reason in conditional_reasons if str(reason)))
    status = "BLOCKED" if unique_blockers else ("CONDITIONAL" if conditional else "PASS")
    return {
        "status": status,
        "final_decision": status,
        "blockers": unique_blockers,
        "conditional_reasons": conditional,
        "record_manifest": manifest_validation,
        "request_ledger": request_validation,
        "request_ledger_aggregate": request_aggregate,
        "request_response_bindings": response_bindings,
        "evidence_relationships": relationships,
        "sampling_validation": sampling_validation,
        "source_evidence": source_validation,
        "metric_validation": metric_validation,
        "artifact_validation": artifact_validation,
        "source_evidence_present": isinstance(source_evidence, Mapping),
        "output_artifact_manifest_present": manifest_rows is not None,
        "final_audit_present": final_audit is not None,
    }
