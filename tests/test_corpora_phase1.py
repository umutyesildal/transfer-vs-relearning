from __future__ import annotations

import bz2
import hashlib
from pathlib import Path

from transfer_vs_relearning.corpora.config import load_corpus_config
from transfer_vs_relearning.corpora.contamination import Pattern, scan_document, turkish_lower
from transfer_vs_relearning.corpora.dedup import exact_deduplicate
from transfer_vs_relearning.corpora.document import CorpusDocument
from transfer_vs_relearning.corpora.dump import parse_checksum_line, sha1_file, status_is_complete
from transfer_vs_relearning.corpora.extract import extract_from_xml_text, parse_wikitext
from transfer_vs_relearning.corpora.filtering import audit_document
from transfer_vs_relearning.corpora.manifest import write_corpus_manifest
from transfer_vs_relearning.corpora.normalize import normalize_document, normalize_text
from transfer_vs_relearning.corpora.split import split_documents


def config(tmp_path: Path) -> dict:
    return {
        "corpus_id": "trwiki_20260601",
        "project": "trwiki",
        "dump_date": "20260601",
        "dump_filename": "trwiki-20260601-pages-articles.xml.bz2",
        "dump_base_url": "https://dumps.wikimedia.org/trwiki/20260601/",
        "checksum_algorithm": "sha1",
        "checksum_filename": "sha1sums.txt",
        "artifact_root": str(tmp_path / "artifacts" / "corpora"),
        "seed": 42,
        "extraction": {
            "mwxml_version": "0.3.8",
            "mwparserfromhell_version": "0.7.2",
            "namespace": 0,
            "skip_redirects": True,
            "filter_disambiguation_pages": False,
        },
        "filtering": {
            "mode": "audit_only",
            "min_chars": 20,
            "max_url_ratio": 0.05,
            "min_alphabetic_ratio": 0.35,
            "min_latin_ratio": 0.80,
            "max_symbol_ratio": 0.20,
            "max_markup_remnant_ratio": 0.05,
        },
        "language_id": {"enabled": False, "audit_only": True},
        "deduplication": {"mode": "exact_sha256"},
        "contamination": {"synthetic_dataset_dir": str(tmp_path / "synthetic_v1"), "matcher": "aho_corasick", "max_context_chars": 80},
        "split": {"train_fraction": 0.98, "validation_fraction": 0.02, "policy": "stable_document_id_sha256"},
    }


def doc(document_id: str, text: str, title: str = "Başlık") -> CorpusDocument:
    return CorpusDocument(
        document_id=document_id,
        page_id=document_id,
        revision_id="r1",
        title=title,
        namespace=0,
        dump_date="20260601",
        source_project="trwiki",
        text=text,
    )


def test_completed_and_incomplete_dump_metadata_parsing() -> None:
    assert status_is_complete('{"status": "done"}')
    assert status_is_complete("Dump complete")
    assert not status_is_complete('{"status": "running"}')


def test_sha1_checksum_parsing_and_validation(tmp_path: Path) -> None:
    filename = "trwiki-20260601-pages-articles.xml.bz2"
    digest = "a" * 40
    assert parse_checksum_line(f"{digest}  {filename}\n", filename) == digest
    partial = tmp_path / (filename + ".partial")
    payload = b"tiny dump"
    partial.write_bytes(payload)
    observed = hashlib.sha1(payload).hexdigest()
    assert sha1_file(partial) == observed
    assert partial.name.endswith(".partial")


def test_namespace_redirect_metadata_and_wikitext_extraction() -> None:
    xml = """<mediawiki>
      <page><title>Ankara</title><ns>0</ns><id>10</id><revision><id>99</id><text>'''Ankara''' [[Türkiye|Türkiye'nin]] başkentidir.</text></revision></page>
      <page><title>Redirect</title><ns>0</ns><id>11</id><redirect title="X"/><revision><id>100</id><text>#REDIRECT [[X]]</text></revision></page>
      <page><title>Talk</title><ns>1</ns><id>12</id><revision><id>101</id><text>skip</text></revision></page>
    </mediawiki>"""
    documents, failures = extract_from_xml_text(xml, config(Path("/tmp")))
    assert failures == []
    assert len(documents) == 1
    assert documents[0].page_id == "10"
    assert documents[0].revision_id == "99"
    assert documents[0].namespace == 0
    assert "Ankara" in documents[0].text
    assert documents[0].raw_wikitext_sha256


def test_wikitext_parsing_and_unresolved_artifacts() -> None:
    text, artifacts = parse_wikitext("{{kutu}} [[İstanbul|İstanbul'un]] tarihi <ref>kaynak</ref>")
    assert "İstanbul" in text
    assert set(artifacts) == {"template_markers", "link_markers", "html_ref_markers"}


def test_nfc_normalization_turkish_preservation_and_paragraphs() -> None:
    normalized, counts = normalize_text("I\u0307stanbul\r\n\r\nTürkçe\tmetin\x00  burada.")
    assert "İstanbul" in normalized
    assert "Türkçe" in normalized
    assert "\n" in normalized
    assert counts["control_chars_removed"] == 1


def test_audit_only_filtering_and_configured_reasons() -> None:
    audited = audit_document(doc("d1", "http://x " * 10), config(Path("/tmp")))
    assert audited.processing_stage == "audited"
    assert "high_url_ratio" in audited.filtering_reasons


def test_content_hashing_and_exact_deduplication() -> None:
    docs = [normalize_document(doc("d2", "aynı metin")), normalize_document(doc("d1", "aynı metin")), normalize_document(doc("d3", "başka"))]
    kept, duplicates, summary = exact_deduplicate(docs)
    assert [item.document_id for item in kept] == ["d1", "d3"]
    assert duplicates[0]["duplicate_document_id"] == "d2"
    assert summary["duplicate_documents"] == 1


def test_turkish_aware_name_normalization() -> None:
    assert turkish_lower("IŞIK İPEK") == "ışık ipek"


def test_contamination_full_name_channels_and_non_removal_cases() -> None:
    patterns = [
        Pattern("p1", "Süreyya Çinpolat", "exact_nfc_full_name", "synthetic_full_name", "canonical", "S1"),
        Pattern("p2", "süreyya çinpolat", "casefold_full_name", "synthetic_full_name_casefold", "canonical", "S1"),
        Pattern("p3", "süreyya çinpolat", "turkish_lower_full_name", "synthetic_full_name_turkish_lower", "canonical", "S1"),
        Pattern("p4", "San Diego", "canonical_object", "canonical_object_only", "canonical", "S1"),
    ]
    clean = scan_document({"document_id": "d1", "title": "x", "text": "Süreyya başka bir addır."}, patterns, {"S1": {"San Diego"}})
    object_only = scan_document({"document_id": "d2", "title": "x", "text": "San Diego güzel bir şehir."}, patterns, {"S1": {"San Diego"}})
    contaminated = scan_document({"document_id": "d3", "title": "x", "text": "SÜREYYA ÇİNPOLAT San Diego ile anıldı."}, patterns, {"S1": {"San Diego"}})
    assert clean["contamination_status"] == "clean"
    assert object_only["contamination_status"] == "clean"
    assert contaminated["contamination_status"] == "contaminated"
    assert any(match["rule_id"] == "synthetic_subject_object_pair" for match in contaminated["matches"])


def test_deterministic_multi_pattern_matching_order() -> None:
    patterns = [
        Pattern("id2", "S00001", "subject_id", "synthetic_subject_id", "canonical", "S00001"),
        Pattern("id1", "S00002", "subject_id", "synthetic_subject_id", "canonical", "S00002"),
    ]
    first = scan_document({"document_id": "d", "title": "x", "text": "S00001 S00002"}, patterns, {})
    second = scan_document({"document_id": "d", "title": "x", "text": "S00001 S00002"}, patterns, {})
    assert first == second
    assert first["contamination_status"] == "contaminated"


def test_deterministic_split_independent_of_input_order() -> None:
    cfg = config(Path("/tmp"))
    docs = [doc("b", "text"), doc("a", "text")]
    assert [item.document_id for item in split_documents(docs, cfg)] == ["a", "b"]
    assert split_documents(docs, cfg)[0].split in {"train", "validation"}


def test_manifest_schema_and_config_loading(tmp_path: Path) -> None:
    cfg_path = Path("configs/corpora/trwiki_gpt2_calibration.yaml")
    cfg = load_corpus_config(cfg_path)
    assert cfg["corpus_id"] == "trwiki_20260601"
    manifest = write_corpus_manifest(config(tmp_path), "phase1_not_finalized", warnings=["thresholds_unreviewed"])
    assert manifest["completion_status"] == "phase1_not_finalized"
    assert manifest["finalized"] is False
    assert manifest["extraction_tool_versions"] == {"mwxml": "0.3.8", "mwparserfromhell": "0.7.2"}
