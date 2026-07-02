from __future__ import annotations

import bz2
import hashlib
import json
from pathlib import Path

import pytest

from transfer_vs_relearning.corpora import pipeline
from transfer_vs_relearning.corpora.config import load_corpus_config
from transfer_vs_relearning.corpora.config import config_hash
from transfer_vs_relearning.corpora.contamination import ContaminationScanner, Pattern, scan_document, turkish_lower
from transfer_vs_relearning.corpora.dedup import exact_deduplicate, exact_deduplicate_stream
from transfer_vs_relearning.corpora.document import CorpusDocument
from transfer_vs_relearning.corpora.dump import DumpMetadata, download_dump, load_official_dump_metadata, parse_checksum_line, sha1_file, status_is_complete
from transfer_vs_relearning.corpora.extract import _iter_real_dump, extract_from_xml_text, parse_wikitext
from transfer_vs_relearning.corpora.filtering import audit_document
from transfer_vs_relearning.corpora.io import iter_documents, write_documents
from transfer_vs_relearning.corpora.manifest import write_corpus_manifest
from transfer_vs_relearning.corpora.normalize import normalize_document, normalize_text
from transfer_vs_relearning.corpora.state import stage_run, stage_state_path
from transfer_vs_relearning.corpora.split import split_documents
from transfer_vs_relearning.utils.io import write_json


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
        "download": {"minimum_free_bytes": 1},
        "extraction": {
            "mwxml_version": "0.3.8",
            "mwparserfromhell_version": "0.7.2",
            "namespace": 0,
            "skip_redirects": True,
            "filter_disambiguation_pages": False,
            "allow_stdlib_fixture_parser": True,
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


def test_production_parser_smoke_with_pinned_dependencies(tmp_path: Path) -> None:
    mwxml = pytest.importorskip("mwxml", reason="mwxml==0.3.8 is not installed")
    mwparserfromhell = pytest.importorskip("mwparserfromhell", reason="mwparserfromhell==0.7.2 is not installed")
    from importlib.metadata import version

    if version("mwxml") != "0.3.8":
        pytest.skip(f"mwxml==0.3.8 required, observed {version('mwxml')}")
    if version("mwparserfromhell") != "0.7.2":
        pytest.skip(f"mwparserfromhell==0.7.2 required, observed {version('mwparserfromhell')}")
    cfg = config(tmp_path)
    cfg["extraction"].pop("allow_stdlib_fixture_parser", None)
    raw = tmp_path / "tiny.xml.bz2"
    xml = """<mediawiki>
      <page><title>Ankara</title><ns>0</ns><id>10</id><revision><id>99</id><text>'''Ankara''' [[Türkiye|Türkiye'nin]] başkentidir.</text></revision></page>
      <page><title>Redirect</title><ns>0</ns><id>11</id><redirect title="X"/><revision><id>100</id><text>#REDIRECT [[X]]</text></revision></page>
      <page><title>Talk</title><ns>1</ns><id>12</id><revision><id>101</id><text>skip</text></revision></page>
    </mediawiki>"""
    raw.write_bytes(bz2.compress(xml.encode("utf-8")))
    docs = [doc for doc, failure in _iter_real_dump(raw, cfg) if doc is not None]
    assert len(docs) == 1
    assert docs[0].page_id == "10"
    assert docs[0].revision_id == "99"
    assert "Ankara" in docs[0].text


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
    assert [item.document_id for item in kept] == ["d2", "d3"]
    assert duplicates[0]["duplicate_document_id"] == "d1"
    assert summary["duplicate_documents"] == 1
    assert summary["keeper_policy"] == "first_document_in_stable_stream_order"


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
    assert object_only["contamination_status"] == "flagged_only"
    assert contaminated["contamination_status"] == "contaminated"
    assert any(match["rule_id"] == "subject_object_cooccurrence" for match in contaminated["matches"])


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


def test_streaming_writer_accepts_single_pass_generator(tmp_path: Path) -> None:
    consumed = False

    def once():
        nonlocal consumed
        if consumed:
            raise AssertionError("generator was iterated twice")
        consumed = True
        yield doc("d1", "metin")

    path = tmp_path / "documents.jsonl"
    assert write_documents(path, once()) == 1
    assert [item.document_id for item in iter_documents(path)] == ["d1"]


def test_disk_backed_deduplication_streams_to_sqlite(tmp_path: Path) -> None:
    docs = (normalize_document(item) for item in [doc("d1", "aynı"), doc("d2", "aynı"), doc("d3", "farklı")])
    summary = exact_deduplicate_stream(docs, tmp_path / "kept.jsonl", tmp_path / "dups.jsonl", tmp_path / "dedup.sqlite")
    assert summary["storage"] == "sqlite"
    assert summary["kept_documents"] == 2
    assert (tmp_path / "dedup.sqlite").exists()


def test_matcher_built_once_for_multiple_documents() -> None:
    before = ContaminationScanner.constructions
    scanner = ContaminationScanner([Pattern("p", "S00001", "subject_id", "synthetic_subject_id", "canonical", "S00001")], {})
    for index in range(3):
        scanner.scan({"document_id": f"d{index}", "title": "x", "text": "S00001"})
    assert ContaminationScanner.constructions == before + 1


def test_contamination_preflight_schema_without_scanning(monkeypatch, tmp_path: Path) -> None:
    cfg = config(tmp_path)
    cfg_path = _write_config(tmp_path, cfg)
    patterns = [Pattern("p", "S00001", "subject_id", "synthetic_subject_id", "canonical", "S00001")]
    monkeypatch.setattr(pipeline, "build_contamination_inventory", lambda dataset_dir: (patterns, {}))
    result = pipeline.run_stage(cfg_path, "contamination-preflight")
    assert result["pattern_count"] == 1
    assert result["pattern_count_by_rule"] == {"synthetic_subject_id": 1}
    assert "exact_nfc" in result["automaton_state_count_by_channel"]
    report = Path(cfg["artifact_root"]) / cfg["corpus_id"] / "reports" / "contamination_preflight.json"
    assert report.exists()


def test_shared_object_subject_associations_are_preserved() -> None:
    patterns = [
        Pattern("o1", "San Diego", "canonical_object", "object_only_flag", "canonical", "S1", ("S1",)),
        Pattern("o2", "San Diego", "canonical_object", "object_only_flag", "canonical", "S2", ("S2",)),
    ]
    result = ContaminationScanner(patterns, {"S1": {"San Diego"}, "S2": {"San Diego"}}).scan(
        {"document_id": "d", "title": "x", "text": "San Diego"}
    )
    subject_ids = sorted({sid for match in result["matches"] for sid in match["associated_subject_ids"]})
    assert subject_ids == ["S1", "S2"]


class FakeResponse:
    def __init__(self, body: bytes, status: int = 200, headers: dict[str, str] | None = None):
        self.body = body
        self.status = status
        self.headers = headers or {}
        self._offset = 0

    def getcode(self) -> int:
        return self.status

    def read(self, size: int = -1) -> bytes:
        if size == -1:
            size = len(self.body) - self._offset
        chunk = self.body[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def metadata(cfg: dict) -> DumpMetadata:
    return DumpMetadata(
        cfg["corpus_id"],
        cfg["project"],
        cfg["dump_date"],
        cfg["dump_base_url"] + cfg["dump_filename"],
        cfg["dump_base_url"] + cfg["checksum_filename"],
        "sha1",
        None,
        True,
        "now",
        cfg["dump_filename"],
        "official",
        cfg["dump_base_url"] + "dumpstatus.json",
    )


def test_download_new_and_valid_206_resume(monkeypatch, tmp_path: Path) -> None:
    cfg = config(tmp_path)
    calls = []

    def fake_urlopen(request):
        calls.append(dict(request.header_items()))
        if len(calls) == 1:
            return FakeResponse(b"abc", 200, {"Content-Length": "3"})
        return FakeResponse(b"def", 206, {"Content-Range": "bytes 3-5/6", "Content-Length": "3"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    first = download_dump(cfg, metadata(cfg))
    assert first.read_bytes() == b"abc"
    second = download_dump(cfg, metadata(cfg))
    assert second.read_bytes() == b"abcdef"


def test_download_rejects_server_ignoring_range_and_bad_content_range(monkeypatch, tmp_path: Path) -> None:
    cfg = config(tmp_path)
    partial = Path(cfg["artifact_root"]) / cfg["corpus_id"] / "raw" / (cfg["dump_filename"] + ".partial")
    partial.parent.mkdir(parents=True)
    partial.write_bytes(b"abc")
    monkeypatch.setattr("urllib.request.urlopen", lambda request: FakeResponse(b"full", 200, {}))
    with pytest.raises(ValueError, match="ignored Range"):
        download_dump(cfg, metadata(cfg))
    monkeypatch.setattr("urllib.request.urlopen", lambda request: FakeResponse(b"def", 206, {"Content-Range": "bytes 2-4/5"}))
    with pytest.raises(ValueError, match="Content-Range"):
        download_dump(cfg, metadata(cfg))


def test_existing_unverified_target_is_rejected(tmp_path: Path) -> None:
    cfg = config(tmp_path)
    target = Path(cfg["artifact_root"]) / cfg["corpus_id"] / "raw" / cfg["dump_filename"]
    target.parent.mkdir(parents=True)
    target.write_bytes(b"unverified")
    with pytest.raises(ValueError, match="unverified"):
        download_dump(cfg, metadata(cfg))


def test_offline_resolve_then_official_resolve_and_download_prerequisite(monkeypatch, tmp_path: Path) -> None:
    cfg = config(tmp_path)
    cfg_path = _write_config(tmp_path, cfg)
    pipeline.run_stage(cfg_path, "resolve")
    assert (Path(cfg["artifact_root"]) / cfg["corpus_id"] / "manifests" / "configured_dump_metadata.json").exists()
    with pytest.raises(ValueError, match="official metadata"):
        pipeline.run_stage(cfg_path, "download")
    checksum = "b" * 40
    responses = {
        cfg["dump_base_url"] + "dumpstatus.json": '{"status": "done"}',
        cfg["dump_base_url"] + cfg["checksum_filename"]: f"{checksum}  {cfg['dump_filename']}\n",
    }
    monkeypatch.setattr("transfer_vs_relearning.corpora.dump._read_url", lambda url: responses[url])
    official = pipeline.run_stage(cfg_path, "resolve", fetch_metadata=True)
    assert official["resolution_mode"] == "official"
    assert load_official_dump_metadata(cfg).expected_checksum == checksum
    reused = pipeline.run_stage(cfg_path, "resolve", fetch_metadata=True)
    assert reused["reused"] is True


def test_official_metadata_missing_checksum_and_mismatch(tmp_path: Path) -> None:
    cfg = config(tmp_path)
    manifests = Path(cfg["artifact_root"]) / cfg["corpus_id"] / "manifests"
    manifests.mkdir(parents=True)
    payload = metadata(cfg).__dict__
    payload["expected_checksum"] = None
    write_json(manifests / "dump_metadata.json", payload)
    with pytest.raises(ValueError, match="expected_checksum"):
        load_official_dump_metadata(cfg)
    payload["expected_checksum"] = "a" * 40
    payload["dump_filename"] = "wrong.xml.bz2"
    write_json(manifests / "dump_metadata.json", payload)
    with pytest.raises(ValueError, match="dump_filename"):
        load_official_dump_metadata(cfg)


def test_official_download_verify_lifecycle_preserves_checksum(monkeypatch, tmp_path: Path) -> None:
    cfg = config(tmp_path)
    cfg_path = _write_config(tmp_path, cfg)
    payload = b"tiny"
    checksum = hashlib.sha1(payload).hexdigest()
    manifests = Path(cfg["artifact_root"]) / cfg["corpus_id"] / "manifests"
    manifests.mkdir(parents=True)
    official = metadata(cfg).__dict__
    official["dump_url"] = cfg["dump_base_url"] + cfg["dump_filename"]
    official["checksum_url"] = cfg["dump_base_url"] + cfg["checksum_filename"]
    official["status_url"] = cfg["dump_base_url"] + "dumpstatus.json"
    official["expected_checksum"] = checksum
    write_json(manifests / "dump_metadata.json", official)
    write_json(stage_state_path(cfg, "resolve"), {"stage": "resolve", "status": "completed", "config_hash": config_hash(cfg), "resolution_mode": "official", "output_artifacts": {"metadata": {"path": str(manifests / "dump_metadata.json"), "kind": "file", "sha256": sha1_file.__globals__["hashlib"].sha256((manifests / "dump_metadata.json").read_bytes()).hexdigest()}}})
    monkeypatch.setattr("urllib.request.urlopen", lambda request: FakeResponse(payload, 200, {"Content-Length": str(len(payload))}))
    pipeline.run_stage(cfg_path, "download")
    assert json.loads((manifests / "dump_metadata.json").read_text())["expected_checksum"] == checksum
    pipeline.run_stage(cfg_path, "verify")
    assert json.loads((manifests / "dump_metadata.json").read_text())["expected_checksum"] == checksum


def test_stage_failed_state_prerequisite_and_config_mismatch(tmp_path: Path) -> None:
    cfg = config(tmp_path)
    with pytest.raises(ValueError, match="requires completed prerequisite"):
        pipeline.run_stage(_write_config(tmp_path, cfg), "normalize")
    with pytest.raises(RuntimeError):
        with stage_run(cfg, "resolve"):
            raise RuntimeError("boom")
    assert json.loads(stage_state_path(cfg, "resolve").read_text())["status"] == "failed"
    write_json(stage_state_path(cfg, "resolve"), {"stage": "resolve", "status": "completed", "config_hash": "wrong", "output_artifacts": {}})
    with pytest.raises(ValueError, match="different config"):
        with stage_run(cfg, "resolve"):
            pass


def test_stage_reuse_checks_input_output_and_force(tmp_path: Path) -> None:
    cfg = config(tmp_path)
    input_path = tmp_path / "input.txt"
    output_path = tmp_path / "output.txt"
    input_path.write_text("input", encoding="utf-8")
    with stage_run(cfg, "resolve", input_path=input_path) as state:
        output_path.write_text("output", encoding="utf-8")
        state["output_artifact_path"] = str(output_path)
    with stage_run(cfg, "resolve", input_path=input_path) as state:
        assert state["reused"] is True
    input_path.write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="input artifact changed"):
        with stage_run(cfg, "resolve", input_path=input_path):
            pass
    with stage_run(cfg, "resolve", force=True, input_path=input_path) as state:
        output_path.write_text("rerun", encoding="utf-8")
        state["output_artifact_path"] = str(output_path)
    output_path.write_text("modified", encoding="utf-8")
    with pytest.raises(ValueError, match="output artifacts"):
        with stage_run(cfg, "resolve", input_path=input_path):
            pass
    output_path.unlink()
    with pytest.raises(ValueError, match="output artifacts"):
        with stage_run(cfg, "resolve", input_path=input_path):
            pass


def test_tiny_end_to_end_phase1_pipeline_excludes_contaminated_documents(tmp_path: Path, monkeypatch) -> None:
    cfg = config(tmp_path)
    cfg_path = _write_config(tmp_path, cfg)
    raw = Path(cfg["artifact_root"]) / cfg["corpus_id"] / "raw" / cfg["dump_filename"]
    raw.parent.mkdir(parents=True)
    xml = """<mediawiki>
      <page><title>Temiz</title><ns>0</ns><id>1</id><revision><id>11</id><text>Temiz Türkçe madde metni burada yer alır.</text></revision></page>
      <page><title>Kirli</title><ns>0</ns><id>2</id><revision><id>22</id><text>Süreyya Çinpolat San Diego hakkında yazdı.</text></revision></page>
    </mediawiki>"""
    raw.write_bytes(bz2.compress(xml.encode("utf-8")))
    write_json(Path(cfg["artifact_root"]) / cfg["corpus_id"] / "manifests" / "verify_manifest.json", {"status": "verified", "path": str(raw), "sha1": "fixture", "dump_filename": cfg["dump_filename"], "dump_date": cfg["dump_date"]})
    write_json(stage_state_path(cfg, "verify"), {"stage": "verify", "status": "completed", "config_hash": config_hash(cfg)})
    patterns = [
        Pattern("s", "Süreyya Çinpolat", "exact_nfc_full_name", "exact_full_synthetic_name", "canonical", "S1"),
        Pattern("o", "San Diego", "canonical_object", "object_only_flag", "canonical", "S1", ("S1",)),
    ]
    monkeypatch.setattr(pipeline, "build_contamination_inventory", lambda dataset_dir: (patterns, {"S1": {"San Diego"}}))
    for stage in ("extract", "normalize", "audit", "filter", "deduplicate", "scan-contamination", "split", "report"):
        pipeline.run_stage(cfg_path, stage)
    root = Path(cfg["artifact_root"]) / cfg["corpus_id"]
    train_text = (root / "splits" / "train_documents.jsonl").read_text(encoding="utf-8")
    validation_text = (root / "splits" / "validation_documents.jsonl").read_text(encoding="utf-8")
    assert "Kirli" not in train_text + validation_text
    assert "Kirli" in (root / "contamination" / "removed_documents.jsonl").read_text(encoding="utf-8")
    report = json.loads((root / "reports" / "contamination_report.json").read_text(encoding="utf-8"))
    assert report["removed_document_count"] == 1


def test_manifest_schema_and_config_loading(tmp_path: Path) -> None:
    cfg_path = Path("configs/corpora/trwiki_gpt2_calibration.yaml")
    cfg = load_corpus_config(cfg_path)
    assert cfg["corpus_id"] == "trwiki_20260601"
    manifest = write_corpus_manifest(config(tmp_path), "phase1_not_finalized", warnings=["thresholds_unreviewed"])
    assert manifest["completion_status"] == "phase1_not_finalized"
    assert manifest["finalized"] is False
    assert manifest["extraction_tool_versions"] == {"mwxml": "0.3.8", "mwparserfromhell": "0.7.2"}


def _write_config(tmp_path: Path, cfg: dict) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path
