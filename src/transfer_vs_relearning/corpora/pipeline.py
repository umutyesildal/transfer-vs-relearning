from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from transfer_vs_relearning.corpora.config import ensure_corpus_dirs, load_corpus_config, stage_dirs
from transfer_vs_relearning.corpora.contamination import build_contamination_inventory, scan_document
from transfer_vs_relearning.corpora.dedup import exact_deduplicate
from transfer_vs_relearning.corpora.document import CorpusDocument
from transfer_vs_relearning.corpora.dump import download_dump, resolve_dump_metadata, verify_dump
from transfer_vs_relearning.corpora.extract import extract_stage
from transfer_vs_relearning.corpora.filtering import audit_document, summarize_audit
from transfer_vs_relearning.corpora.manifest import write_corpus_manifest
from transfer_vs_relearning.corpora.normalize import normalize_document
from transfer_vs_relearning.corpora.split import split_documents
from transfer_vs_relearning.utils.io import write_json


def run_stage(config_path: Path, stage: str, force: bool = False, fetch_metadata: bool = False) -> Path | dict[str, Any]:
    config = load_corpus_config(config_path)
    ensure_corpus_dirs(config)
    _write_state(config, stage, "running")
    if stage == "resolve":
        result = resolve_dump_metadata(config, fetch=fetch_metadata)
        _write_state(config, stage, "completed")
        return result.__dict__
    if stage == "download":
        metadata = resolve_dump_metadata(config, fetch=False)
        result = download_dump(config, metadata, force=force)
        _write_state(config, stage, "partial" if result.suffix.endswith("partial") else "completed")
        return result
    if stage == "verify":
        metadata_path = stage_dirs(config)["manifests"] / "dump_metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not metadata.get("expected_checksum"):
            raise ValueError("verify requires resolved metadata with expected_checksum")
        result = verify_dump(config, metadata["expected_checksum"])
        _write_state(config, stage, "completed")
        return result
    if stage == "extract":
        result = extract_stage(config)
        _write_state(config, stage, "completed")
        return result
    if stage == "normalize":
        docs = [normalize_document(doc) for doc in _read_docs(stage_dirs(config)["extracted"] / "documents.jsonl")]
        result = stage_dirs(config)["normalized"] / "documents.jsonl"
        _write_docs(result, docs)
        _write_state(config, stage, "completed")
        return result
    if stage == "audit":
        docs = [audit_document(doc, config) for doc in _read_docs(stage_dirs(config)["normalized"] / "documents.jsonl")]
        result = stage_dirs(config)["audited"] / "documents.jsonl"
        _write_docs(result, docs)
        write_json(stage_dirs(config)["reports"] / "audit_report.json", summarize_audit(docs))
        _write_state(config, stage, "completed")
        return result
    if stage == "filter":
        docs = _read_docs(stage_dirs(config)["audited"] / "documents.jsonl")
        result = stage_dirs(config)["filtered"] / "documents.jsonl"
        if config["filtering"].get("mode") == "audit_only":
            _write_docs(result, docs)
        else:
            _write_docs(result, [doc for doc in docs if not doc.filtering_reasons])
        _write_state(config, stage, "completed")
        return result
    if stage == "deduplicate":
        kept, duplicates, summary = exact_deduplicate(_read_docs(stage_dirs(config)["filtered"] / "documents.jsonl"))
        _write_docs(stage_dirs(config)["deduplicated"] / "documents.jsonl", kept)
        write_json(stage_dirs(config)["reports"] / "deduplication_report.json", summary)
        _write_jsonl(stage_dirs(config)["deduplicated"] / "duplicates.jsonl", duplicates)
        _write_state(config, stage, "completed")
        return summary
    if stage == "scan-contamination":
        patterns, subject_objects = build_contamination_inventory(Path(config["contamination"]["synthetic_dataset_dir"]))
        docs = [doc.to_json() for doc in _read_docs(stage_dirs(config)["deduplicated"] / "documents.jsonl")]
        results = [scan_document(doc, patterns, subject_objects, int(config["contamination"].get("max_context_chars", 80))) for doc in docs]
        _write_jsonl(stage_dirs(config)["contamination"] / "matches.jsonl", [match for result in results for match in result["matches"]])
        write_json(stage_dirs(config)["reports"] / "contamination_report.json", {
            "document_count": len(results),
            "contaminated_document_count": sum(result["contamination_status"] == "contaminated" for result in results),
            "matcher": "aho_corasick",
            "complexity": "O(total_text_length + total_pattern_length + matches)",
        })
        _write_state(config, stage, "completed")
        return stage_dirs(config)["contamination"] / "matches.jsonl"
    if stage == "split":
        docs = split_documents(_read_docs(stage_dirs(config)["deduplicated"] / "documents.jsonl"), config)
        result = stage_dirs(config)["splits"] / "documents.jsonl"
        _write_docs(result, docs)
        _write_state(config, stage, "completed")
        return result
    if stage == "report":
        result = write_corpus_manifest(config, "phase1_not_finalized")
        _write_state(config, stage, "completed")
        return result
    raise ValueError(f"Unknown stage: {stage}")


def _write_state(config: dict[str, Any], stage: str, status: str) -> None:
    write_json(stage_dirs(config)["manifests"] / f"{stage}_state.json", {"stage": stage, "status": status})


def _read_docs(path: Path) -> list[CorpusDocument]:
    docs = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                docs.append(CorpusDocument.from_json(json.loads(line)))
    return docs


def _write_docs(path: Path, docs: list[CorpusDocument]) -> None:
    _write_jsonl(path, [doc.to_json() for doc in docs])


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)
