from __future__ import annotations

import hashlib
import heapq
import json
from pathlib import Path
from typing import Any, Iterator

from transfer_vs_relearning.utils.io import write_json


REVIEW_BUCKETS = ("removed", "flagged_only", "clean")


def generate_contamination_review_sample(corpus_root: Path, seed: int = 42, sample_size: int = 20) -> dict[str, Any]:
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    contamination = corpus_root / "contamination"
    manifests = corpus_root / "manifests"
    reports = corpus_root / "reports"
    clean_path = contamination / "clean_documents.jsonl"
    removed_path = contamination / "removed_documents.jsonl"
    matches_path = contamination / "matches.jsonl"
    scan_state_path = manifests / "scan-contamination_state.json"
    for path in (clean_path, removed_path, matches_path, scan_state_path):
        if not path.is_file():
            raise ValueError(f"Review source artifact is missing: {path}")

    heaps: dict[str, list[tuple[int, str, dict[str, Any]]]] = {bucket: [] for bucket in REVIEW_BUCKETS}
    observed = {bucket: 0 for bucket in REVIEW_BUCKETS}
    for row in _iter_jsonl(removed_path):
        document = row.get("document") or {}
        observed["removed"] += 1
        _offer(heaps["removed"], "removed", document, row, seed, sample_size)
    for document in _iter_jsonl(clean_path):
        bucket = "flagged_only" if document.get("contamination_status") == "flagged_only" else "clean"
        observed[bucket] += 1
        _offer(heaps[bucket], bucket, document, {"document": document}, seed, sample_size)

    selected_ids = {
        entry[1]
        for bucket in ("removed", "flagged_only")
        for entry in heaps[bucket]
    }
    match_details: dict[str, dict[str, Any]] = {
        document_id: {"total": 0, "matches": []}
        for document_id in selected_ids
    }
    for match in _iter_jsonl(matches_path):
        details = match_details.get(str(match.get("document_id")))
        if details is None:
            continue
        details["total"] += 1
        if len(details["matches"]) < 25:
            details["matches"].append(_compact_match(match))

    samples = {}
    for bucket in REVIEW_BUCKETS:
        ordered = sorted(
            ((-negative_score, document_id, row) for negative_score, document_id, row in heaps[bucket]),
            key=lambda item: (item[0], item[1]),
        )
        samples[bucket] = [
            _compact_sample(bucket, score, document_id, row, match_details.get(document_id))
            for score, document_id, row in ordered
        ]

    scan_state = json.loads(scan_state_path.read_text(encoding="utf-8"))
    source_hashes = {
        key: value.get("sha256")
        for key, value in (scan_state.get("output_artifacts") or {}).items()
        if key in {"clean_documents", "removed_documents", "matches"}
    }
    payload = {
        "review_status": "pending_manual_review",
        "seed": seed,
        "sample_size_per_bucket": sample_size,
        "selection_policy": "lowest_sha256(seed|bucket|document_id), tie_break_document_id",
        "match_detail_policy": "first_25_in_frozen_match_stream_with_total_count",
        "source_scan_processing_git_commit": scan_state.get("processing_git_commit"),
        "source_artifact_sha256": source_hashes,
        "observed_bucket_counts": observed,
        "samples": samples,
    }
    output = reports / f"contamination_review_sample_seed{seed}.json"
    write_json(output, payload)
    return payload


def _offer(
    heap: list[tuple[int, str, dict[str, Any]]],
    bucket: str,
    document: dict[str, Any],
    row: dict[str, Any],
    seed: int,
    sample_size: int,
) -> None:
    document_id = str(document.get("document_id") or "")
    if not document_id:
        raise ValueError(f"{bucket} review row has no document_id")
    score = int(hashlib.sha256(f"{seed}|{bucket}|{document_id}".encode("utf-8")).hexdigest(), 16)
    entry = (-score, document_id, row)
    if len(heap) < sample_size:
        heapq.heappush(heap, entry)
    elif score < -heap[0][0]:
        heapq.heapreplace(heap, entry)


def _compact_sample(
    bucket: str,
    score: int,
    document_id: str,
    row: dict[str, Any],
    match_details: dict[str, Any] | None,
) -> dict[str, Any]:
    document = row.get("document") or {}
    output = {
        "bucket": bucket,
        "selection_sha256": f"{score:064x}",
        "document_id": document_id,
        "title": document.get("title"),
        "text_excerpt": _excerpt(str(document.get("text") or "")),
        "contamination_status": document.get("contamination_status"),
        "filtering_reasons": document.get("filtering_reasons") or [],
    }
    if bucket == "removed":
        output["removal_rule_ids"] = row.get("removal_rule_ids") or []
    if match_details is not None:
        output["match_count"] = match_details["total"]
        output["matches"] = match_details["matches"]
    return output


def _compact_match(match: dict[str, Any]) -> dict[str, Any]:
    associated = list(match.get("associated_subject_ids") or [])
    return {
        "matched_pattern_id": match.get("matched_pattern_id"),
        "match_channel": match.get("match_channel"),
        "rule_id": match.get("rule_id"),
        "automatic_decision": match.get("automatic_decision"),
        "context": match.get("context"),
        "associated_subject_id_count": len(associated),
        "associated_subject_ids_first_25": associated[:25],
    }


def _excerpt(text: str, limit: int = 1000) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[:limit] + "…"


def _iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL row") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            yield row
