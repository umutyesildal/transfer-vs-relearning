from __future__ import annotations

import json
import resource
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable

from transfer_vs_relearning.corpora.config import ensure_corpus_dirs, load_corpus_config, stage_dirs
from transfer_vs_relearning.corpora.contamination import ContaminationScanner, build_contamination_inventory
from transfer_vs_relearning.corpora.dedup import exact_deduplicate_stream
from transfer_vs_relearning.corpora.document import CorpusDocument
from transfer_vs_relearning.corpora.dump import download_dump, load_official_dump_metadata, resolve_dump_metadata, verify_dump
from transfer_vs_relearning.corpora.extract import extract_stage
from transfer_vs_relearning.corpora.filtering import AuditSummary, audit_document
from transfer_vs_relearning.corpora.io import iter_documents, write_documents, write_jsonl
from transfer_vs_relearning.corpora.manifest import write_corpus_manifest
from transfer_vs_relearning.corpora.normalize import normalize_document
from transfer_vs_relearning.corpora.split import assign_split
from transfer_vs_relearning.corpora.state import stage_run
from transfer_vs_relearning.utils.io import write_json


def run_stage(config_path: Path, stage: str, force: bool = False, fetch_metadata: bool = False) -> Path | dict[str, Any]:
    config = load_corpus_config(config_path)
    ensure_corpus_dirs(config)
    if stage == "resolve":
        if not fetch_metadata:
            result = resolve_dump_metadata(config, fetch=False)
            write_json(stage_dirs(config)["manifests"] / "resolve_configured_state.json", {
                "stage": "resolve",
                "status": "configured_only",
                "resolution_mode": "configured_only",
                "output_artifact_path": str(stage_dirs(config)["manifests"] / "configured_dump_metadata.json"),
            })
            return result.__dict__
        with stage_run(config, stage, force=force) as state:
            if state.get("reused"):
                return state
            result = resolve_dump_metadata(config, fetch=fetch_metadata)
            state["resolution_mode"] = "official"
            state["output_artifact_path"] = str(stage_dirs(config)["manifests"] / "dump_metadata.json")
            return result.__dict__
    if stage == "download":
        with stage_run(config, stage, force=force) as state:
            if state.get("reused"):
                return state
            metadata = load_official_dump_metadata(config)
            result = download_dump(config, metadata, force=force)
            state["download_status"] = "downloaded_unverified"
            state["output_artifact_path"] = str(result)
            state["output_artifact_map"] = {
                "download_artifact": str(result),
                "download_manifest": str(stage_dirs(config)["manifests"] / "download_manifest.json"),
            }
            return result
    if stage == "verify":
        metadata_path = stage_dirs(config)["manifests"] / "dump_metadata.json"
        metadata = load_official_dump_metadata(config)
        download_manifest = _read_json(stage_dirs(config)["manifests"] / "download_manifest.json")
        input_path = Path(download_manifest["artifact_path"])
        with stage_run(config, stage, force=force, input_path=input_path) as state:
            if state.get("reused"):
                return state
            result = verify_dump(config, metadata.expected_checksum or "")
            state["output_artifact_path"] = str(result)
            state["output_artifact_map"] = {
                "verified_dump": str(result),
                "verify_manifest": str(stage_dirs(config)["manifests"] / "verify_manifest.json"),
            }
            return result
    if stage == "extract":
        with stage_run(config, stage, force=force, input_path=stage_dirs(config)["raw"] / config["dump_filename"]) as state:
            if state.get("reused"):
                return state
            result = extract_stage(config)
            manifest = _read_json(stage_dirs(config)["manifests"] / "extraction_manifest.json")
            state["document_counters"] = {"documents": manifest.get("document_count", 0), "failures": manifest.get("failure_count", 0)}
            state["output_artifact_path"] = str(result)
            return result
    if stage == "normalize":
        input_path = stage_dirs(config)["extracted"] / "documents.jsonl"
        result = stage_dirs(config)["normalized"] / "documents.jsonl"
        with stage_run(config, stage, force=force, input_path=input_path) as state:
            if state.get("reused"):
                return state
            count = write_documents(result, (normalize_document(doc) for doc in iter_documents(input_path)))
            state["document_counters"] = {"documents": count}
            state["output_artifact_path"] = str(result)
            return result
    if stage == "audit":
        input_path = stage_dirs(config)["normalized"] / "documents.jsonl"
        result = stage_dirs(config)["audited"] / "documents.jsonl"
        summary = AuditSummary()

        def audited_docs() -> Iterable[CorpusDocument]:
            for doc in iter_documents(input_path):
                audited = audit_document(doc, config)
                summary.add(audited)
                yield audited

        with stage_run(config, stage, force=force, input_path=input_path) as state:
            if state.get("reused"):
                return state
            count = write_documents(result, audited_docs())
            write_json(stage_dirs(config)["reports"] / "audit_report.json", summary.to_json())
            state["document_counters"] = {"documents": count}
            state["output_artifact_path"] = str(result)
            return result
    if stage == "filter":
        input_path = stage_dirs(config)["audited"] / "documents.jsonl"
        result = stage_dirs(config)["filtered"] / "documents.jsonl"
        with stage_run(config, stage, force=force, input_path=input_path) as state:
            if state.get("reused"):
                return state
            count = write_documents(result, _filter_documents(iter_documents(input_path), config))
            state["document_counters"] = {"documents": count}
            state["output_artifact_path"] = str(result)
            return result
    if stage == "deduplicate":
        input_path = stage_dirs(config)["filtered"] / "documents.jsonl"
        result = stage_dirs(config)["deduplicated"] / "documents.jsonl"
        with stage_run(config, stage, force=force, input_path=input_path) as state:
            if state.get("reused"):
                return state
            summary = exact_deduplicate_stream(
                iter_documents(input_path),
                result,
                stage_dirs(config)["deduplicated"] / "duplicates.jsonl",
                stage_dirs(config)["deduplicated"] / "exact_dedup.sqlite",
            )
            write_json(stage_dirs(config)["reports"] / "deduplication_report.json", summary)
            state["document_counters"] = summary
            state["output_artifact_path"] = str(result)
            return summary
    if stage == "scan-contamination":
        input_path = stage_dirs(config)["deduplicated"] / "documents.jsonl"
        with stage_run(config, stage, force=force, input_path=input_path) as state:
            if state.get("reused"):
                return state
            summary = _scan_contamination_stream(config, input_path)
            write_json(stage_dirs(config)["reports"] / "contamination_report.json", summary)
            state["document_counters"] = summary
            state["output_artifact_path"] = str(stage_dirs(config)["contamination"] / "clean_documents.jsonl")
            state["output_artifact_map"] = {
                "clean_documents": str(stage_dirs(config)["contamination"] / "clean_documents.jsonl"),
                "removed_documents": str(stage_dirs(config)["contamination"] / "removed_documents.jsonl"),
                "matches": str(stage_dirs(config)["contamination"] / "matches.jsonl"),
                "report": str(stage_dirs(config)["reports"] / "contamination_report.json"),
            }
            return summary
    if stage == "split":
        input_path = stage_dirs(config)["contamination"] / "clean_documents.jsonl"
        with stage_run(config, stage, force=force, input_path=input_path) as state:
            if state.get("reused"):
                return state
            summary = _split_stream(config, input_path)
            write_json(stage_dirs(config)["reports"] / "split_report.json", summary)
            state["document_counters"] = summary
            state["output_artifact_path"] = str(stage_dirs(config)["splits"])
            state["output_artifact_map"] = {
                "train_documents": str(stage_dirs(config)["splits"] / "train_documents.jsonl"),
                "validation_documents": str(stage_dirs(config)["splits"] / "validation_documents.jsonl"),
                "report": str(stage_dirs(config)["reports"] / "split_report.json"),
            }
            return summary
    if stage == "contamination-preflight":
        with stage_run(config, stage, force=force) as state:
            if state.get("reused"):
                return state
            result = contamination_preflight(config)
            state["document_counters"] = result
            state["output_artifact_path"] = str(stage_dirs(config)["reports"] / "contamination_preflight.json")
            return result
    if stage == "report":
        with stage_run(config, stage, force=force) as state:
            if state.get("reused"):
                return state
            result = write_corpus_manifest(config, "phase1_not_finalized")
            state["output_artifact_path"] = str(stage_dirs(config)["manifests"] / "corpus_manifest.json")
            return result
    raise ValueError(f"Unknown stage: {stage}")


def _filter_documents(documents: Iterable[CorpusDocument], config: dict[str, Any]) -> Iterable[CorpusDocument]:
    audit_only = config["filtering"].get("mode") == "audit_only"
    for doc in documents:
        if audit_only or not doc.filtering_reasons:
            doc.processing_stage = "filtered"
            yield doc


def _scan_contamination_stream(config: dict[str, Any], input_path: Path) -> dict[str, Any]:
    patterns, subject_objects = build_contamination_inventory(Path(config["contamination"]["synthetic_dataset_dir"]))
    scanner = ContaminationScanner(patterns, subject_objects, int(config["contamination"].get("max_context_chars", 80)))
    clean_path = stage_dirs(config)["contamination"] / "clean_documents.jsonl"
    removed_path = stage_dirs(config)["contamination"] / "removed_documents.jsonl"
    matches_path = stage_dirs(config)["contamination"] / "matches.jsonl"
    id_index = sqlite3.connect(stage_dirs(config)["contamination"] / "document_ids.sqlite")
    id_index.execute("CREATE TABLE IF NOT EXISTS seen (document_id TEXT PRIMARY KEY, branch TEXT NOT NULL)")
    counts = {"document_count": 0, "clean_document_count": 0, "removed_document_count": 0, "flagged_only_document_count": 0, "match_count": 0}
    clean_tmp = clean_path.with_suffix(clean_path.suffix + ".tmp")
    removed_tmp = removed_path.with_suffix(removed_path.suffix + ".tmp")
    matches_tmp = matches_path.with_suffix(matches_path.suffix + ".tmp")
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    with clean_tmp.open("w", encoding="utf-8") as clean_handle, removed_tmp.open("w", encoding="utf-8") as removed_handle, matches_tmp.open("w", encoding="utf-8") as matches_handle:
        for doc in iter_documents(input_path):
            counts["document_count"] += 1
            result = scanner.scan(doc.to_json())
            doc.contamination_status = result["contamination_status"]
            for match in result["matches"]:
                matches_handle.write(json.dumps(match, ensure_ascii=False, sort_keys=True) + "\n")
                counts["match_count"] += 1
            if result["contamination_status"] == "contaminated":
                _record_document_branch(id_index, doc.document_id, "removed")
                counts["removed_document_count"] += 1
                remove_rule_ids = sorted({match["rule_id"] for match in result["matches"] if match["automatic_decision"] == "remove"})
                removed_handle.write(json.dumps({"document": doc.to_json(), "removal_rule_ids": remove_rule_ids, "matches": result["matches"]}, ensure_ascii=False, sort_keys=True) + "\n")
            else:
                if result["contamination_status"] == "flagged_only":
                    counts["flagged_only_document_count"] += 1
                _record_document_branch(id_index, doc.document_id, "clean")
                counts["clean_document_count"] += 1
                clean_handle.write(json.dumps(doc.to_json(), ensure_ascii=False, sort_keys=True) + "\n")
    clean_tmp.replace(clean_path)
    removed_tmp.replace(removed_path)
    matches_tmp.replace(matches_path)
    id_index.commit()
    id_index.close()
    counts["matcher"] = "aho_corasick"
    counts["complexity"] = "O(total_text_length + total_pattern_length + matches) after one-time matcher construction"
    counts["pattern_counts"] = scanner.pattern_counts
    counts["automaton_state_counts"] = scanner.automaton_state_counts
    counts["target_retained_verified_full_name_matches"] = 0
    return counts


def contamination_preflight(config: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    patterns, subject_objects = build_contamination_inventory(Path(config["contamination"]["synthetic_dataset_dir"]))
    inventory_time = time.perf_counter() - start
    matcher_start = time.perf_counter()
    scanner = ContaminationScanner(patterns, subject_objects, int(config["contamination"].get("max_context_chars", 80)))
    matcher_time = time.perf_counter() - matcher_start
    by_rule: dict[str, int] = {}
    by_channel: dict[str, int] = {}
    for pattern in patterns:
        by_rule[pattern.rule_id] = by_rule.get(pattern.rule_id, 0) + 1
        by_channel[pattern.channel] = by_channel.get(pattern.channel, 0) + 1
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result = {
        "pattern_count": len(patterns),
        "pattern_count_by_rule": dict(sorted(by_rule.items())),
        "pattern_count_by_channel": dict(sorted(by_channel.items())),
        "automaton_state_count_by_channel": scanner.automaton_state_counts,
        "inventory_build_seconds": inventory_time,
        "matcher_build_seconds": matcher_time,
        "peak_rss": rss,
        "peak_rss_unit": "kilobytes_on_linux_bytes_on_macos_platform_dependent",
        "total_pattern_text_characters": sum(len(pattern.text) for pattern in patterns),
    }
    write_json(stage_dirs(config)["reports"] / "contamination_preflight.json", result)
    return result


def _record_document_branch(conn: sqlite3.Connection, document_id: str, branch: str) -> None:
    existing = conn.execute("SELECT branch FROM seen WHERE document_id = ?", (document_id,)).fetchone()
    if existing is not None:
        raise ValueError(f"Duplicate document_id in contamination scan: {document_id}")
    conn.execute("INSERT INTO seen VALUES (?, ?)", (document_id, branch))


def _split_stream(config: dict[str, Any], input_path: Path) -> dict[str, Any]:
    train_path = stage_dirs(config)["splits"] / "train_documents.jsonl"
    validation_path = stage_dirs(config)["splits"] / "validation_documents.jsonl"
    train_tmp = train_path.with_suffix(train_path.suffix + ".tmp")
    validation_tmp = validation_path.with_suffix(validation_path.suffix + ".tmp")
    counts = {"train_documents": 0, "validation_documents": 0}
    train_path.parent.mkdir(parents=True, exist_ok=True)
    with train_tmp.open("w", encoding="utf-8") as train_handle, validation_tmp.open("w", encoding="utf-8") as validation_handle:
        for doc in iter_documents(input_path):
            if doc.contamination_status == "contaminated":
                raise ValueError(f"Contaminated document cannot enter split: {doc.document_id}")
            doc.split = assign_split(doc, config)
            doc.processing_stage = "split"
            row = json.dumps(doc.to_json(), ensure_ascii=False, sort_keys=True) + "\n"
            if doc.split == "validation":
                validation_handle.write(row)
                counts["validation_documents"] += 1
            else:
                train_handle.write(row)
                counts["train_documents"] += 1
    train_tmp.replace(train_path)
    validation_tmp.replace(validation_path)
    return counts


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
