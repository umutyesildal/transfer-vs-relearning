#!/usr/bin/env python3
"""Apply a bounded human-approved translation overlay without rewriting canonical source data."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from transfer_vs_relearning.data.qwen_pre_m2 import build_branch_b_fact_registry
from transfer_vs_relearning.utils.io import read_csv_rows, sha256_file, write_json


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"Blank JSONL row at line {line_number}: {path}")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row is not an object at line {line_number}: {path}")
        rows.append(value)
    return rows


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


def _selected_subject_ids(path: Path) -> set[str]:
    values = _json(path).get("selected_subject_ids")
    if not isinstance(values, list) or len(values) != 100 or len(set(values)) != 100:
        raise ValueError("Expected exact 100 unique selected subject IDs")
    return {str(value) for value in values}


def prepare(
    *,
    canonical_profiles: Path,
    selected_subjects: Path,
    prior_decisions: Path,
    prior_packet: Path,
    overlay_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError(f"Correction output root already exists: {output_root}")
    overlay = _json(overlay_path)
    if overlay.get("status") != "HUMAN_APPROVED_TRANSLATION_CORRECTION_OVERLAY":
        raise ValueError("Translation overlay is not human-approved")
    if sha256_file(prior_decisions) != overlay.get("base_review_decisions_sha256"):
        raise ValueError("Prior human decision ledger SHA-256 drift")
    if sha256_file(prior_packet) != "4ccbef107e74248a079885edb97209bf1341f11163ba38a288c7c636ad7210e2":
        raise ValueError("Prior 250-fact review packet SHA-256 drift")
    base_rows = build_branch_b_fact_registry(
        read_csv_rows(canonical_profiles),
        _selected_subject_ids(selected_subjects),
        expected_subjects=100,
        version="m2_oscar_relation_v2_100_subjects_v1",
    )
    output_root.mkdir(parents=True)
    base_path = output_root / "branch_b_turkish_facts_base_reproduction.jsonl"
    _write_jsonl(base_path, base_rows)
    if sha256_file(base_path) != overlay.get("base_registry_sha256"):
        raise ValueError("Local base registry does not reproduce the frozen HU registry")

    by_id = {str(row["fact_id"]): dict(row) for row in base_rows}
    corrections = overlay.get("corrections")
    accepted = overlay.get("accepted_unchanged")
    if not isinstance(corrections, list) or len(corrections) != 4:
        raise ValueError("Correction overlay must contain exactly four changed facts")
    if not isinstance(accepted, list) or len(accepted) != 3:
        raise ValueError("Correction overlay must contain exactly three accepted unchanged facts")
    corrected_ids: set[str] = set()
    for change in corrections:
        fact_id = str(change["fact_id"])
        row = by_id.get(fact_id)
        if row is None or fact_id in corrected_ids:
            raise ValueError(f"Missing or duplicate corrected fact: {fact_id}")
        if row.get("answer_tr") != change.get("old_answer_tr") or row.get("text") != change.get("old_text"):
            raise ValueError(f"Correction predecessor text drift: {fact_id}")
        row["answer_tr"] = str(change["corrected_answer_tr"])
        row["text"] = str(change["corrected_text"])
        row["template_id"] = str(row["template_id"]).replace("_tr_v1", "_tr_v2_human_corrected")
        corrected_ids.add(fact_id)
    accepted_ids = {str(row["fact_id"]) for row in accepted}
    if len(accepted_ids) != 3 or corrected_ids & accepted_ids:
        raise ValueError("Changed and accepted-unchanged fact sets must be disjoint")
    for item in accepted:
        fact_id = str(item["fact_id"])
        row = by_id.get(fact_id)
        if row is None or row.get("answer_tr") != item.get("answer_tr") or row.get("text") != item.get("text"):
            raise ValueError(f"Accepted-unchanged fact drift: {fact_id}")

    corrected_path = output_root / "branch_b_turkish_facts_corrected.jsonl"
    corrected_rows = [by_id[str(row["fact_id"])] for row in base_rows]
    _write_jsonl(corrected_path, corrected_rows)
    if len(corrected_rows) != 250 or len({row["fact_id"] for row in corrected_rows}) != 250:
        raise ValueError("Corrected fact registry cardinality drift")

    prior_packet_rows = _jsonl(prior_packet)
    if len(prior_packet_rows) != 250:
        raise ValueError("Prior review packet must contain exactly 250 rows")
    corrected_packet_rows: list[dict[str, Any]] = []
    for index, packet_row in enumerate(prior_packet_rows):
        fact_id = str(packet_row.get("fact_id", ""))
        source = by_id.get(fact_id)
        if source is None or packet_row.get("index") != index:
            raise ValueError("Prior review packet identity/order drift")
        corrected_packet_rows.append(
            {
                "fact_id": fact_id,
                "index": index,
                "relation": source["relation"],
                "text": source["text"],
            }
        )
    corrected_packet_path = output_root / "fact_review_packet_corrected.jsonl"
    _write_jsonl(corrected_packet_path, corrected_packet_rows)

    decisions = _jsonl(prior_decisions)
    decision_by_id = {str(row.get("fact_id", "")): dict(row) for row in decisions}
    issue_ids = {fact_id for fact_id, row in decision_by_id.items() if row.get("verdict") == "issue"}
    if issue_ids != corrected_ids | accepted_ids or len(decision_by_id) != 250:
        raise ValueError("Prior issue set does not equal the seven approved resolutions")
    corrected_registry_sha = sha256_file(corrected_path)
    resolution_by_id = {
        str(row["fact_id"]): f"human-approved translation correction: {row['old_answer_tr']} -> {row['corrected_answer_tr']}"
        for row in corrections
    }
    resolution_by_id.update(
        {str(row["fact_id"]): "human-approved unchanged Turkish term" for row in accepted}
    )
    resolved_decisions: list[dict[str, Any]] = []
    for source in decisions:
        fact_id = str(source["fact_id"])
        row = dict(source)
        row["fact_registry_sha256"] = corrected_registry_sha
        if fact_id in resolution_by_id:
            row["verdict"] = "usable"
            prior_note = str(row.get("notes") or "").strip()
            resolution = resolution_by_id[fact_id]
            row["notes"] = f"{prior_note} | RESOLVED: {resolution}" if prior_note else f"RESOLVED: {resolution}"
        resolved_decisions.append(row)
    verdicts = Counter(str(row.get("verdict")) for row in resolved_decisions)
    if verdicts != {"usable": 250}:
        raise ValueError(f"Corrected decision ledger is not 250/250 usable: {dict(verdicts)}")
    decisions_path = output_root / "human_review_decisions_corrected.jsonl"
    _write_jsonl(decisions_path, resolved_decisions)

    result = {
        "schema_version": 1,
        "status": "M2_FACT_REGISTRY_CORRECTION_PASS",
        "base_registry": {"path": str(base_path), "sha256": sha256_file(base_path), "rows": 250},
        "corrected_registry": {
            "path": str(corrected_path),
            "sha256": corrected_registry_sha,
            "rows": 250,
        },
        "prior_decisions_sha256": sha256_file(prior_decisions),
        "corrected_decisions": {
            "path": str(decisions_path),
            "sha256": sha256_file(decisions_path),
            "rows": 250,
            "verdicts": {"usable": 250},
        },
        "corrected_review_packet": {
            "path": str(corrected_packet_path),
            "sha256": sha256_file(corrected_packet_path),
            "rows": 250,
        },
        "overlay": {"path": str(overlay_path), "sha256": sha256_file(overlay_path)},
        "changed_fact_ids": sorted(corrected_ids),
        "accepted_unchanged_fact_ids": sorted(accepted_ids),
        "canonical_source_mutated": False,
        "old_registry_mutated": False,
        "blocks_repaired": False,
        "ready_to_train": False,
    }
    write_json(output_root / "correction_manifest.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-profiles", type=Path, required=True)
    parser.add_argument("--selected-subjects", type=Path, required=True)
    parser.add_argument("--prior-decisions", type=Path, required=True)
    parser.add_argument("--prior-packet", type=Path, required=True)
    parser.add_argument("--overlay", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(
        canonical_profiles=args.canonical_profiles.resolve(),
        selected_subjects=args.selected_subjects.resolve(),
        prior_decisions=args.prior_decisions.resolve(),
        prior_packet=args.prior_packet.resolve(),
        overlay_path=args.overlay.resolve(),
        output_root=args.output_root.resolve(),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
