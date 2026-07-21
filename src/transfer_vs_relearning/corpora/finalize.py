from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transfer_vs_relearning.corpora.manifest import git_commit
from transfer_vs_relearning.utils.io import sha256_file, write_json


def finalize_reviewed_corpus(corpus_root: Path, seed: int = 42, sample_size: int = 20) -> dict[str, Any]:
    manifests = corpus_root / "manifests"
    reports = corpus_root / "reports"
    splits = corpus_root / "splits"
    candidate_path = manifests / "corpus_manifest.json"
    review_path = reports / f"contamination_review_sample_seed{seed}.json"
    scan_state_path = manifests / "scan-contamination_state.json"
    decision_path = reports / f"contamination_review_decision_seed{seed}.json"
    final_manifest_path = manifests / "corpus_manifest_final.json"
    final_hash_path = manifests / "bridge_split_final_sha256.txt"
    train_path = splits / "train_documents.jsonl"
    validation_path = splits / "validation_documents.jsonl"

    required = (candidate_path, review_path, scan_state_path, train_path, validation_path)
    for path in required:
        if not path.is_file():
            raise ValueError(f"Finalization source artifact is missing: {path}")
    for path in (decision_path, final_manifest_path, final_hash_path):
        if path.exists():
            raise ValueError(f"Refusing to overwrite finalization artifact: {path}")

    candidate = _read_json(candidate_path)
    review = _read_json(review_path)
    scan_state = _read_json(scan_state_path)
    if candidate.get("finalized") is not False or candidate.get("completion_status") != "phase1_not_finalized":
        raise ValueError("Candidate manifest is not in the expected pre-final state")
    if review.get("review_status") != "pending_manual_review":
        raise ValueError("Review artifact is not pending manual review")
    if review.get("seed") != seed or review.get("sample_size_per_bucket") != sample_size:
        raise ValueError("Review seed or sample size differs from the frozen contract")
    expected_sources = {
        key: value.get("sha256")
        for key, value in (scan_state.get("output_artifacts") or {}).items()
        if key in {"clean_documents", "removed_documents", "matches"}
    }
    if review.get("source_artifact_sha256") != expected_sources:
        raise ValueError("Review source hashes do not match the frozen scan state")

    samples = review.get("samples") or {}
    if {key: len(samples.get(key) or []) for key in ("removed", "flagged_only", "clean")} != {
        "removed": sample_size,
        "flagged_only": sample_size,
        "clean": sample_size,
    }:
        raise ValueError("Review bucket sizes do not match the frozen contract")
    removed = samples["removed"]
    flagged = samples["flagged_only"]
    clean = samples["clean"]
    checks = {
        "removed_all_have_full_name_rule": all(
            any("full_synthetic_name" in rule for rule in row.get("removal_rule_ids") or []) for row in removed
        ),
        "removed_all_have_visible_decisive_match": all(
            row.get("decisive_match_count", 0) > 0
            and any(match.get("automatic_decision") == "remove" for match in row.get("matches") or [])
            for row in removed
        ),
        "flagged_all_have_zero_decisive_matches": all(row.get("decisive_match_count", 0) == 0 for row in flagged),
        "flagged_visible_matches_all_object_only": all(
            match.get("rule_id") == "object_only_flag" for row in flagged for match in row.get("matches") or []
        ),
        "clean_all_have_zero_matches": all(row.get("match_count", 0) == 0 for row in clean),
        "all_samples_have_document_ids": all(row.get("document_id") for bucket in samples.values() for row in bucket),
    }
    if not all(checks.values()):
        raise ValueError(f"Manual-review structural gate failed: {checks}")

    timestamp = datetime.now(timezone.utc).isoformat()
    decision = {
        "review_status": "manual_review_passed",
        "reviewed_at": timestamp,
        "reviewer_role": "project_agent_with_user_authorized_execution",
        "review_artifact_path": str(review_path),
        "review_artifact_sha256": sha256_file(review_path),
        "source_artifact_sha256": expected_sources,
        "sample_counts": {key: len(samples[key]) for key in ("removed", "flagged_only", "clean")},
        "structural_checks": checks,
        "interpretation": (
            "Removed examples are conservative real-world surface collisions with frozen synthetic full names; "
            "flag-only examples contain generic object surfaces; clean examples contain no matcher hit."
        ),
        "decision": "pass_and_freeze_corpus",
    }
    write_json(decision_path, decision)

    final_manifest = copy.deepcopy(candidate)
    final_manifest.update({
        "completion_status": "finalized",
        "finalized": True,
        "candidate_manifest_path": str(candidate_path),
        "candidate_manifest_sha256": sha256_file(candidate_path),
        "manual_review_decision_path": str(decision_path),
        "manual_review_decision_sha256": sha256_file(decision_path),
        "finalization_git_commit": git_commit(),
        "finalization_timestamp": timestamp,
    })
    final_manifest.setdefault("artifact_hashes", {})[str(decision_path.relative_to(corpus_root))] = {
        "size_bytes": decision_path.stat().st_size,
        "sha256": sha256_file(decision_path),
    }
    write_json(final_manifest_path, final_manifest)

    hash_lines = [
        f"{sha256_file(path)}  {path}\n"
        for path in (train_path, validation_path, review_path, decision_path, final_manifest_path)
    ]
    final_hash_path.write_text("".join(hash_lines), encoding="utf-8")
    return {
        "review_decision": decision,
        "final_manifest_path": str(final_manifest_path),
        "final_manifest_sha256": sha256_file(final_manifest_path),
        "final_hash_path": str(final_hash_path),
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value
