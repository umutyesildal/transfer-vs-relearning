from __future__ import annotations

import copy
import hashlib
import io
import json
import urllib.error
from pathlib import Path
from time import perf_counter

import pytest

from transfer_vs_relearning.corpora.vngrs.contamination import ContaminationPattern, normalized_text_sha256
from transfer_vs_relearning.corpora.vngrs.dedup import character_ngrams, exact_jaccard, minhash_signature, near_duplicate_pairs, near_duplicate_summary
from transfer_vs_relearning.corpora.vngrs.manifest import (
    RECORD_MANIFEST_FIELDS,
    REQUEST_LEDGER_FIELDS,
    serialize_request_ledger,
    validate_record_manifest,
    validate_request_ledger,
    validate_request_ledger_aggregate,
)
from transfer_vs_relearning.corpora.vngrs.metadata import (
    METADATA_FOOTER_CONTRACT_SHA256,
    METADATA_FOOTER_FOOTER_RANGE_TEMPLATE,
    METADATA_FOOTER_OUTPUT_PATHS,
    METADATA_FOOTER_RANGE_HEADER,
    METADATA_FOOTER_ROUTE_KIND,
    METADATA_FOOTER_SCRATCH_ROOT,
    METADATA_FOOTER_TRAILER_RANGE_HEADER,
    VNGRS_REPOSITORY,
    VNGRS_REVISION,
    build_metadata_footer_feasibility_projection,
    build_sampling_schedule,
    build_selection_evidence,
    build_shard_paths,
    canonical_json_sha256,
    dataset_license_resolve_url,
    metadata_coverage,
    parse_parquet_footer,
    parse_parquet_trailer,
    parquet_resolve_url,
    serialize_metadata_footer_artifact_manifest,
    select_systematic_shards,
    validate_final_source_evidence,
    validate_metadata_footer_feasibility,
    validate_metadata_footer_output_paths,
    validate_sampling_schedule,
)
from transfer_vs_relearning.corpora.vngrs import metadata_executor as metadata_executor_module
from transfer_vs_relearning.corpora.vngrs.metadata_executor import (
    AttemptResult,
    BoundedClient,
    ExecutionBlocked,
    independent_writer_self_check,
)
from transfer_vs_relearning.corpora.vngrs.pipeline import (
    FailClosedLidAdapter,
    LidResult,
    VngrsPreparationConfig,
    evaluate_final_contract,
    prepare_records,
)
from transfer_vs_relearning.corpora.vngrs.outputs import (
    build_final_audit,
    build_output_artifact_manifest,
    canonical_json_bytes,
    validate_final_audit,
)
from transfer_vs_relearning.corpora.vngrs.quality import QualityConfig, detect_pii, evaluate_quality, redact_pii
from transfer_vs_relearning.corpora.vngrs.records import (
    VngrsRecordError,
    normalize_text,
    read_parquet_metadata,
    serialized_record_bytes,
    source_identity_key,
    stable_record_id,
    stream_parquet_records,
)
from transfer_vs_relearning.corpora.vngrs.sampling import largest_remainder_allocation, midpoint_systematic_positions, sampling_weights
from transfer_vs_relearning.corpora.vngrs.split import assign_document_disjoint, assert_document_disjoint


def record(original_id: object, text: str, *, corpus: str = "source-a", shard_path: str = "data/train-00004-of-00284.parquet") -> dict[str, object]:
    return {"original_id": original_id, "corpus": corpus, "text": text, "shard_path": shard_path}


class StubLid:
    def classify(self, text: str) -> LidResult:
        if "Türkçe" in text and "English" in text:
            return LidResult("verified", "tur", 0.80, True, "test-lid", "a" * 64)
        if "English" in text:
            return LidResult("verified", "eng", 0.99, False, "test-lid", "a" * 64)
        return LidResult("verified", "tur", 0.99, "\n" in text, "test-lid", "a" * 64)


def test_systematic_selection_is_exact_and_not_first_prefix() -> None:
    ordinals = select_systematic_shards(284, 32)
    assert len(ordinals) == 32
    assert ordinals == tuple(sorted(ordinals))
    assert ordinals != tuple(range(32))
    assert ordinals[0] > 0
    assert ordinals[-1] < 284
    evidence = build_selection_evidence()
    assert evidence["selected_ordinals"] == list(ordinals)
    assert len(evidence["selected_paths"]) == 32
    assert all(row["row_count"] is None for row in evidence["registry_rows"])
    assert canonical_json_sha256(evidence) == canonical_json_sha256(build_selection_evidence())


def test_official_shard_path_registry_has_284_entries() -> None:
    paths = build_shard_paths()
    assert len(paths) == 284
    assert paths[0] == "data/train-00000-of-00284.parquet"
    assert paths[-1] == "data/train-00283-of-00284.parquet"


def test_metadata_coverage_does_not_turn_missing_values_into_zero() -> None:
    evidence = build_selection_evidence()
    from transfer_vs_relearning.corpora.vngrs.metadata import ShardMetadata

    summary = metadata_coverage(
        ShardMetadata(path=row["path"], ordinal=row["ordinal"], shard_count=284)
        for row in evidence["registry_rows"]
    )
    assert summary["field_coverage"]["path"]["status"] == "verified"
    assert summary["field_coverage"]["row_count"]["status"] == "unresolved"


def test_normalization_preserves_turkish_and_removes_control() -> None:
    raw = "I\u0307stanbul\r\nTürkçe\tmetin\x00  burada."
    normalized = normalize_text(raw)
    assert "İstanbul" in normalized.text
    assert "Türkçe" in normalized.text
    assert normalized.control_chars_removed == 1
    assert len(normalized.sha256) == 64
    assert len(raw) != len(normalized.text)


def test_stable_identity_prefers_native_id_and_falls_back_deterministically() -> None:
    first = stable_record_id(
        record("row-1", "metin"),
        source_revision=VNGRS_REVISION,
        shard_path="data/train-00004-of-00284.parquet",
        row_group_index=1,
        row_index=3,
    )
    second = stable_record_id(
        record(0, "zero"),
        source_revision=VNGRS_REVISION,
        shard_path="data/train-00004-of-00284.parquet",
        row_group_index=1,
        row_index=3,
    )
    assert first.startswith("vngrs:")
    assert second.startswith("vngrs:")
    assert second == stable_record_id(
        record(0, "zero"),
        source_revision=VNGRS_REVISION,
        shard_path="data/train-00004-of-00284.parquet",
        row_group_index=1,
        row_index=3,
    )
    assert source_identity_key(record(0, "zero")) == ("source-a", "0")
    assert stable_record_id(record("row-1", "metin", corpus="source-b"), source_revision=VNGRS_REVISION, shard_path="", row_group_index=0, row_index=0) != first


def test_parquet_metadata_and_streaming_are_local_and_schema_checked(tmp_path: Path) -> None:
    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")
    path = tmp_path / "tiny.parquet"
    table = pa.table(
        {
            "text": ["Türkçe ilk metin", "Türkçe ikinci metin"],
            "corpus": ["source-a", "source-b"],
            "original_id": ["a", "b"],
        }
    )
    pq.write_table(table, path)
    metadata = read_parquet_metadata(path)
    assert metadata.row_count == 2
    assert metadata.schema == ("text", "corpus", "original_id")
    assert list(stream_parquet_records(path)) == [
        {"text": "Türkçe ilk metin", "corpus": "source-a", "original_id": "a"},
        {"text": "Türkçe ikinci metin", "corpus": "source-b", "original_id": "b"},
    ]


def test_malformed_parquet_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "malformed.parquet"
    path.write_bytes(b"not parquet")
    with pytest.raises(VngrsRecordError):
        read_parquet_metadata(path)


def test_quality_spam_code_adult_and_pii_diagnostics() -> None:
    quality = evaluate_quality(
        "porno " * 10 + "https://example.invalid " * 10 + "def x(): { return 1; }",
        QualityConfig(min_chars=1, max_url_ratio=0.01, max_code_coverage=0.01),
    )
    assert not quality.accepted
    assert {"adult_flag", "url_heavy", "code_heavy"}.issubset(quality.reasons)
    assert detect_pii("contact test@example.invalid or +90 555 123 4567") == ("email", "phone")
    redacted, kinds = redact_pii("contact test@example.invalid")
    assert kinds == ("email",)
    assert "test@example.invalid" not in redacted


def test_exact_and_cap_free_near_deduplication() -> None:
    text = "Bu Türkçe metin benzersiz bir örnektir."
    features = character_ngrams(text, 5)
    assert len(features) > 5
    assert len(minhash_signature(features, num_perm=128)) == 128
    pairs = near_duplicate_pairs(
        [
            {"record_id": "b", "normalized_text": text},
            {"record_id": "a", "normalized_text": text},
        ],
        threshold=0.95,
    )
    assert pairs[0]["first_record_id"] == "a"
    assert pairs[0]["second_record_id"] == "b"


def test_contamination_alias_template_and_benchmark_overlap_channels() -> None:
    patterns = [
        ContaminationPattern("alias-1", "alias", "Örnek Kişi", "alias_surface"),
        ContaminationPattern("template-1", "template", "{{örnek şablon}}", "template_surface"),
    ]
    text = "Örnek Kişi için {{örnek şablon}} kullanıldı."
    result = prepare_records(
        [record("row-1", text)],
        config=VngrsPreparationConfig(source_revision=VNGRS_REVISION),
        lid_adapter=StubLid(),
        contamination_patterns=patterns,
        benchmark_item_hashes=[normalized_text_sha256(text)],
    )
    assert result["raw_denominator"] == 1
    assert result["retained_denominator"] == 0
    assert len(result["benchmark_overlaps"]["raw_sampled"]) == 1
    assert len(result["benchmark_overlaps"]["retained"]) == 0
    clean_text = "Bu temiz ve yeterince uzun bir Türkçe örnek metindir."
    clean_result = prepare_records(
        [record("row-clean", clean_text)],
        config=VngrsPreparationConfig(source_revision=VNGRS_REVISION),
        lid_adapter=StubLid(),
        benchmark_item_hashes=[normalized_text_sha256(clean_text)],
    )
    assert clean_result["retained_denominator"] == 1
    assert len(clean_result["benchmark_overlaps"]["raw_sampled"]) == 1
    assert len(clean_result["benchmark_overlaps"]["retained"]) == 1


def test_non_turkish_and_mixed_line_lid_are_recorded_without_fabrication() -> None:
    result = prepare_records(
        [
            record("tr", "Bu Türkçe bir örnek metindir."),
            record("en", "English example text."),
            record("mixed", "Bu Türkçe satırdır.\nEnglish line here."),
        ],
        config=VngrsPreparationConfig(source_revision=VNGRS_REVISION),
        lid_adapter=StubLid(),
    )
    statuses = {row["original_id"]: row for row in result["records"]}
    assert result["raw_denominator"] == 3
    assert statuses["tr"]["lid_top1_language"] == "tur"
    assert statuses["en"]["lid_top1_language"] == "eng"
    assert statuses["mixed"]["strict_mixed_line_flag"] is True
    retained_ids = {row["original_id"] for row in result["retained_records"]}
    assert "tr" in retained_ids
    assert "mixed" in retained_ids
    assert "en" not in retained_ids
    english_raw = next(row for row in result["raw_manifest"] if row["original_id"] == "en")
    assert "lid_non_turkish_or_unaccepted_label" in english_raw["rejection_reason_codes"]


def test_duplicate_ids_empty_and_over_limit_fail_closed() -> None:
    cfg = VngrsPreparationConfig(source_revision=VNGRS_REVISION, max_records=1)
    with pytest.raises(ValueError, match="duplicate composite"):
        prepare_records(
            [
                record("same", "ilk metin yeterince uzundur.", shard_path="data/train-00004-of-00284.parquet"),
                record("same", "ikinci metin yeterince uzundur.", shard_path="data/train-00279-of-00284.parquet"),
            ],
            config=VngrsPreparationConfig(source_revision=VNGRS_REVISION),
            lid_adapter=StubLid(),
        )
    with pytest.raises(ValueError, match="exceeds"):
        prepare_records([record("a", "ilk metin yeterince uzundur."), record("b", "ikinci metin yeterince uzundur.")], config=cfg, lid_adapter=StubLid())
    empty = prepare_records([], config=VngrsPreparationConfig(source_revision=VNGRS_REVISION))
    assert empty["raw_denominator"] == 0
    assert empty["status"] == "DIAGNOSTIC_ONLY"
    incomplete = prepare_records(
        [record("one", "Bu örnek metin yeterince uzundur.")],
        config=VngrsPreparationConfig(source_revision=VNGRS_REVISION, enforce_exact_sample=True),
        lid_adapter=StubLid(),
    )
    assert incomplete["status"] == "BLOCKED"
    assert "incomplete_exact_raw_sample" in incomplete["gate"]["blocking_reasons"]


def test_composite_key_allows_same_id_across_corpora_but_rejects_true_duplicate() -> None:
    text_a = "Bu birinci corpus için yeterince uzun Türkçe metindir."
    text_b = "Bu ikinci corpus için yeterince uzun Türkçe metindir."
    result = prepare_records(
        [record(0, text_a, corpus="corpus-a"), record(0, text_b, corpus="corpus-b")],
        config=VngrsPreparationConfig(source_revision=VNGRS_REVISION),
        lid_adapter=StubLid(),
    )
    assert result["raw_denominator"] == 2
    assert result["retained_denominator"] == 2
    assert {row["source_identity_key"]["corpus"] for row in result["raw_manifest"]} == {"corpus-a", "corpus-b"}
    assert validate_record_manifest(result["raw_manifest"])["source_identity_unique"] is True
    with pytest.raises(ValueError, match="duplicate composite"):
        prepare_records(
            [record(0, text_a, corpus="corpus-a"), record(0, text_b, corpus="corpus-a")],
            config=VngrsPreparationConfig(source_revision=VNGRS_REVISION),
            lid_adapter=StubLid(),
        )


def test_document_disjoint_split_is_order_independent() -> None:
    rows = [{"record_id": "b"}, {"record_id": "a"}]
    first = assign_document_disjoint(rows, seed=42, validation_fraction=0.5)
    second = assign_document_disjoint(list(reversed(rows)), seed=42, validation_fraction=0.5)
    assert first == second
    assert_document_disjoint(first)


def test_record_bytes_are_not_http_response_bytes() -> None:
    payload = serialized_record_bytes({"text": "örnek", "original_id": "r1"})
    assert payload.startswith(b"{")
    assert len(payload) > 0


def test_prepared_record_carries_record_payload_bytes_only() -> None:
    result = prepare_records(
        [record("row-1", "Bu payload byte hesabı için yeterli bir metindir.")],
        config=VngrsPreparationConfig(source_revision=VNGRS_REVISION),
        lid_adapter=StubLid(),
    )
    assert result["records"][0]["exact_serialized_record_payload_bytes"] > 0
    assert "response_transferred_bytes" not in result["records"][0]


def test_row_count_weighted_largest_remainder_and_positions() -> None:
    counts = {"shard-a": 3, "shard-b": 7, "shard-c": 10}
    allocation = largest_remainder_allocation(counts, 10)
    assert allocation == {"shard-a": 2, "shard-b": 3, "shard-c": 5}
    assert sum(allocation.values()) == 10
    assert midpoint_systematic_positions(10, 3) == (1, 5, 8)
    weights = sampling_weights(counts, allocation)
    assert weights["shard-c"]["population_weight"] == 0.5
    assert weights["shard-c"]["sample_weight"] == 0.5


def test_output_manifest_and_final_audit_are_self_reference_free() -> None:
    artifacts = {
        name: {"path": name, "bytes": index + 1, "sha256": "a" * 64}
        for index, name in enumerate(
            [
                "selection_plan.json",
                "request_ledger.jsonl",
                "record_manifest.jsonl",
                "raw_population_metrics.json",
                "retained_population_metrics.json",
                "dedup_metrics.json",
                "contamination_overlap_metrics.json",
            ]
        )
    }
    manifest = build_output_artifact_manifest(artifacts)
    audit = build_final_audit(manifest, manifest_sha256="b" * 64)
    assert len(manifest) == 7
    assert all(row["path"] not in {"output_artifact_manifest.jsonl", "calibration_audit.json"} for row in manifest)
    assert audit["self_reference"] is False
    assert audit["write_order"][-2:] == ["output_artifact_manifest.jsonl", "calibration_audit.json"]


def test_lsh_near_dedup_is_bounded_and_scales_without_all_pairs() -> None:
    records = [
        {
            "record_id": f"r-{index:04d}",
            "normalized_text": hashlib.sha256(f"record-{index}".encode()).hexdigest() * 3,
        }
        for index in range(2_000)
    ]
    started = perf_counter()
    summary = near_duplicate_summary(records, max_candidate_pairs=200_000, max_output_pairs=20_000)
    elapsed = perf_counter() - started
    assert elapsed < 30.0
    assert summary["protocol"] == "minhash_lsh_universal_v1"
    assert summary["candidate_pair_count"] < (2_000 * 1_999) // 2
    assert summary["denominator"] == 2_000


def test_minhash_estimator_is_calibrated_against_exact_jaccard_across_ranges() -> None:
    cases = [
        (set(range(100)), set(range(10, 110))),
        (set(range(100)), set(range(10, 110)) | set(range(100, 111))),
        (set(range(100)), set(range(20))),
    ]
    for first, second in cases:
        exact = exact_jaccard(first, second)
        estimate = sum(
            a == b
            for a, b in zip(
                minhash_signature(map(str, first), seed=42),
                minhash_signature(map(str, second), seed=42),
                strict=True,
            )
        ) / 128
        assert abs(estimate - exact) <= 0.15
    assert exact_jaccard(set(range(100)), set(range(100))) == 1.0
    assert exact_jaccard(set(range(100)), set(range(100, 200))) == 0.0
    high = set(range(100))
    high_near = set(range(5, 105))
    assert exact_jaccard(high, high_near) > 0.80


def test_record_manifest_requires_schema_cardinality_identity_and_no_text() -> None:
    result = prepare_records(
        [record("row-1", "Bu manifest şeması için yeterince uzun Türkçe metindir.")],
        config=VngrsPreparationConfig(source_revision=VNGRS_REVISION),
        lid_adapter=StubLid(),
    )
    row = result["raw_manifest"][0]
    assert set(row) == set(RECORD_MANIFEST_FIELDS)
    assert "normalized_text" not in row
    assert result["manifest_validation"]["complete"] is False
    broken = dict(row)
    broken["normalized_text"] = "forbidden"
    assert validate_record_manifest([broken])["complete"] is False


def test_request_ledger_keeps_response_bytes_at_request_grain() -> None:
    row = {
        "request_id": "req-1",
        "attempt_id": "attempt-1",
        "attempt_ordinal": 0,
        "retry_ordinal": 0,
        "source_repo": "vngrs-ai/vngrs-web-corpus",
        "immutable_revision": VNGRS_REVISION,
        "route": "/rows",
        "shard_path": "data/train-00004-of-00284.parquet",
        "row_range_or_metadata_target": "offset=0,length=100",
        "request_start_utc": "2026-08-08T00:00:00Z",
        "response_end_utc": "2026-08-08T00:00:01Z",
        "http_status": 200,
        "response_transferred_bytes": 1234,
        "response_evidence_artifact": "responses/req-1.json",
        "content_encoding": "identity",
        "content_type": "application/json",
        "redirect_chain": [],
        "response_sha256": "b" * 64,
        "request_outcome": "success",
    }
    assert set(row) == set(REQUEST_LEDGER_FIELDS)
    assert validate_request_ledger([row])["complete"] is True
    aggregate = validate_request_ledger_aggregate([row])
    assert aggregate["complete"] is True
    assert aggregate["successful_row_request_count"] == 1
    assert "response_transferred_bytes" in serialize_request_ledger([row])


def test_scientific_gate_fails_closed_for_unresolved_lid_even_with_retained_fixture() -> None:
    class AdversarialLid:
        def classify(self, text: str) -> LidResult:
            if "unresolved" in text:
                return FailClosedLidAdapter().classify(text)
            return LidResult("verified", "tur", 0.99, False, "test-lid", "a" * 64)

    result = prepare_records(
        [
            record("row-1", "Bu unresolved kayıt bilimsel kapı için yeterince uzun Türkçe metindir."),
            record("row-2", "Bu geçerli kayıt bilimsel kapı için yeterince uzun Türkçe metindir."),
        ],
        config=VngrsPreparationConfig(
            source_revision=VNGRS_REVISION,
            scientific_profile=True,
            sample_target_records=2,
            source_integrity_verified=True,
        ),
        lid_adapter=AdversarialLid(),
    )
    assert result["retained_denominator"] == 1
    assert result["status"] == "BLOCKED"
    assert "lid_status_unresolved" in result["gate"]["blocking_reasons"]
    assert "lid_evaluator_identity_unresolved_in_raw_manifest" in result["gate"]["blocking_reasons"]
    assert result["status"] != "PASS"


def test_near_dedup_realistic_cluster_and_candidate_explosion_fail_closed() -> None:
    base = "Türkçe web sayfası başlığı ve açıklaması. " * 2250
    assert 90_000 <= len(base) < 100_000
    records = [
        {"record_id": "a", "normalized_text": base},
        {"record_id": "b", "normalized_text": base + " Ek açıklama."},
        {"record_id": "c", "normalized_text": base + " Başka bir ek."},
    ]
    summary = near_duplicate_summary(records, threshold=0.80, max_candidate_pairs=100)
    assert summary["candidate_pair_count"] > 0
    assert summary["near_duplicate_pair_count"] > 0
    with pytest.raises(ValueError, match="candidate bound"):
        near_duplicate_summary(records, threshold=0.0, max_candidate_pairs=1)


def test_largest_remainder_uses_integer_ties_and_large_counts() -> None:
    counts = {"b": 10**18 + 1, "a": 10**18}
    assert largest_remainder_allocation(counts, 3) == {"a": 1, "b": 2}
    assert largest_remainder_allocation({"b": 1, "a": 1}, 1) == {"a": 1, "b": 0}


def test_output_chain_rejects_uppercase_hash_and_unknown_or_reordered_artifacts() -> None:
    names = [
        "selection_plan.json", "request_ledger.jsonl", "record_manifest.jsonl",
        "raw_population_metrics.json", "retained_population_metrics.json", "dedup_metrics.json",
        "contamination_overlap_metrics.json",
    ]
    artifacts = {name: {"path": name, "bytes": 1, "sha256": "a" * 64} for name in names}
    manifest = build_output_artifact_manifest(artifacts)
    broken_hash = [dict(row) for row in manifest]
    broken_hash[0]["sha256"] = "A" * 64
    with pytest.raises(ValueError, match="64 lowercase"):
        build_final_audit(broken_hash, manifest_sha256="b" * 64)
    broken_order = [dict(row) for row in manifest]
    broken_order[0], broken_order[1] = broken_order[1], broken_order[0]
    with pytest.raises(ValueError, match="order"):
        build_final_audit(broken_order, manifest_sha256="b" * 64)


def test_final_audit_requires_exact_path_hash_order_and_no_self_reference() -> None:
    names = [
        "selection_plan.json", "request_ledger.jsonl", "record_manifest.jsonl",
        "raw_population_metrics.json", "retained_population_metrics.json", "dedup_metrics.json",
        "contamination_overlap_metrics.json",
    ]
    artifacts = {name: {"path": name, "bytes": 1, "sha256": "a" * 64} for name in names}
    manifest = build_output_artifact_manifest(artifacts)
    audit = build_final_audit(manifest, manifest_sha256="b" * 64)
    assert validate_final_audit(audit, manifest, manifest_sha256="b" * 64)["complete"] is True
    for key, value in (("final_audit_path", "other.json"), ("manifest_sha256", "c" * 64)):
        broken = dict(audit)
        broken[key] = value
        with pytest.raises(ValueError):
            validate_final_audit(broken, manifest, manifest_sha256="b" * 64)
    broken = dict(audit)
    broken["self_reference"] = True
    with pytest.raises(ValueError):
        validate_final_audit(broken, manifest, manifest_sha256="b" * 64)
    broken = dict(audit)
    broken["artifacts"] = list(reversed(manifest))
    with pytest.raises(ValueError):
        validate_final_audit(broken, manifest, manifest_sha256="b" * 64)


def test_prepare_stage_is_never_a_final_pass_and_final_runner_blocks_missing_evidence() -> None:
    result = prepare_records(
        [record("row-1", "Bu aşama yalnızca tanı amaçlı yeterince uzun Türkçe metindir.")],
        config=VngrsPreparationConfig(source_revision=VNGRS_REVISION),
        lid_adapter=StubLid(),
    )
    assert result["status"] == "DIAGNOSTIC_ONLY"
    final = evaluate_final_contract(
        result,
        request_ledger=[],
        source_evidence=None,
        output_artifact_manifest=None,
        output_artifact_manifest_sha256=None,
        final_audit=None,
    )
    assert final["status"] == "BLOCKED"
    assert "strict_source_evidence_invalid" in final["blockers"]


def _valid_final_evidence_graph() -> dict[str, object]:
    """Build a fully linked synthetic positive control for the frozen 151ak final profile."""

    selection = build_selection_evidence()
    paths = list(selection["selected_paths"])
    source_shards = [
        {
            "path": path,
            "ordinal": ordinal,
            "shard_count": 284,
            "row_count": 1000 + ordinal,
            "compressed_bytes": 100_000 + ordinal,
            "uncompressed_bytes": 200_000 + ordinal,
            "object_id": f"object-{ordinal:05d}",
            "sha256": "a" * 64,
            "footer_sha256": "b" * 64,
            "license_bytes_sha256": "c" * 64,
            "object_evidence_artifact": f"source/object-{ordinal:05d}.json",
            "footer_evidence_artifact": f"source/footer-{ordinal:05d}.json",
            "license_evidence_artifact": f"source/license-{ordinal:05d}.txt",
        }
        for path, ordinal in zip(paths, selection["selected_ordinals"], strict=True)
    ]
    route_mapping = [
        {
            "path": path,
            "route": f"https://example.invalid/rows/{ordinal}",
            "route_kind": "/rows",
            "immutable_revision": VNGRS_REVISION,
            "status": "verified",
            "route_evidence_sha256": "d" * 64,
            "route_evidence_artifact": f"source/route-{ordinal:05d}.json",
        }
        for path, ordinal in zip(paths, selection["selected_ordinals"], strict=True)
    ]
    source_evidence: dict[str, object] = {
        "status": "verified",
        "source_repository": VNGRS_REPOSITORY,
        "immutable_revision": VNGRS_REVISION,
        "split": "train",
        "schema": ["text", "corpus", "original_id"],
        "source_license": "cc-by-nc-sa-4.0",
        "selection_version": selection["selection_version"],
        "selection_formula": selection["selection_formula"],
        "total_shards": 284,
        "selected_shards": 32,
        "selected_ordinals": selection["selected_ordinals"],
        "selected_paths": paths,
        "selection_payload": selection,
        "selection_payload_sha256": canonical_json_sha256(selection),
        "selected_shard_evidence": source_shards,
        "route_mapping": route_mapping,
        "sampling_schedule": build_sampling_schedule(source_shards),
        "evidence_class": "STRUCTURAL_SYNTHETIC_CONTROL",
    }
    source_evidence_artifact_payloads: dict[str, bytes] = {}
    for shard in source_shards:
        for field, artifact_field in (
            ("sha256", "object_evidence_artifact"),
            ("footer_sha256", "footer_evidence_artifact"),
            ("license_bytes_sha256", "license_evidence_artifact"),
        ):
            payload = f"{shard[artifact_field]}\n".encode()
            source_evidence_artifact_payloads[shard[artifact_field]] = payload
            shard[field] = hashlib.sha256(payload).hexdigest()
    for route in route_mapping:
        payload = f"{route['route']}\n{route['immutable_revision']}\n".encode()
        source_evidence_artifact_payloads[route["route_evidence_artifact"]] = payload
        route["route_evidence_sha256"] = hashlib.sha256(payload).hexdigest()
    source_evidence["evidence_sha256"] = canonical_json_sha256(source_evidence)

    records: list[dict[str, object]] = []
    requests: list[dict[str, object]] = []
    for request_index in range(100):
        request_id = f"logical-{request_index:03d}"
        shard_path = paths[request_index % len(paths)]
        requests.append(
            {
                "request_id": request_id,
                "attempt_id": f"attempt-{request_index:03d}-0",
                "attempt_ordinal": 0,
                "retry_ordinal": 0,
                "source_repo": VNGRS_REPOSITORY,
                "immutable_revision": VNGRS_REVISION,
                "route": "/rows",
                "shard_path": shard_path,
                "row_range_or_metadata_target": f"offset={request_index * 100},length=100",
                "request_start_utc": "2026-08-08T00:00:00Z",
                "response_end_utc": "2026-08-08T00:00:01Z",
                "http_status": 200,
                "response_transferred_bytes": 1000,
                "response_evidence_artifact": f"responses/{request_id}.json",
                "content_encoding": "identity",
                "content_type": "application/json",
                "redirect_chain": [],
                "response_sha256": hashlib.sha256(f"response-{request_id}\n".encode()).hexdigest(),
                "request_outcome": "success",
            }
        )
        for record_index in range(100):
            sample_index = request_index * 100 + record_index
            normalized_sha = hashlib.sha256(f"normalized-{sample_index}".encode()).hexdigest()
            original_id = f"original-{sample_index}"
            records.append(
                {
                    "request_id": request_id,
                    "record_index_within_response": record_index,
                    "source_repo": VNGRS_REPOSITORY,
                    "immutable_revision": VNGRS_REVISION,
                    "corpus": "vngrs",
                    "shard_path": shard_path,
                    "stable_source_row_document_id": f"stable-{sample_index}",
                    "original_id": original_id,
                    "source_identity_key": {"corpus": "vngrs", "original_id": original_id},
                    "sample_index": sample_index,
                    "exact_serialized_record_payload_bytes": 100 + sample_index,
                    "normalized_text_sha256": normalized_sha,
                    "retrieved_at_utc": "2026-08-08T00:00:01Z",
                    "raw_text_character_count": 250,
                    "normalized_text_character_count": 240,
                    "normalization_version": "nfc_control_whitespace_v1",
                    "lid_evaluator_id": "frozen-test-lid-v1",
                    "lid_evaluator_sha256": "f" * 64,
                    "lid_status": "verified",
                    "lid_top1_language": "tur",
                    "lid_confidence": 0.99,
                    "strict_mixed_line_flag": False,
                    "quality_status": "accepted",
                    "quality_reason_codes": [],
                    "pii_status": "clean",
                    "pii_reason_codes": [],
                    "exact_dedup_key": normalized_sha,
                    "near_dedup_version": "near-dedup-v1",
                    "synthetic_contamination_status": "clean",
                    "synthetic_contamination_tiers": [],
                    "benchmark_overlap_status": "clean",
                    "split": "held_out" if sample_index % 100 == 0 else "train",
                    "retention_status": "retained",
                    "rejection_reason_codes": [],
                }
            )

    record_payload = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in records
    ).encode()
    request_payload = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in requests
    ).encode()
    retained_input = canonical_json_sha256([
        {"stable_source_row_document_id": row["stable_source_row_document_id"], "normalized_text_sha256": row["normalized_text_sha256"]}
        for row in records
    ])
    overlap_input = canonical_json_sha256([
        {
            "stable_source_row_document_id": row["stable_source_row_document_id"],
            "normalized_text_sha256": row["normalized_text_sha256"],
            "benchmark_overlap_status": row["benchmark_overlap_status"],
        }
        for row in records
    ])
    split_input = canonical_json_sha256([
        {"stable_source_row_document_id": row["stable_source_row_document_id"], "split": row["split"]}
        for row in records
    ])
    record_sha = hashlib.sha256(record_payload).hexdigest()
    request_sha = hashlib.sha256(request_payload).hexdigest()
    request_response_payloads = {
        row["response_evidence_artifact"]: f"response-{row['request_id']}\n".encode()
        for row in requests
    }
    artifacts_payloads: dict[str, bytes] = {
        "selection_plan.json": canonical_json_bytes(
            {
                "source_evidence_sha256": source_evidence["evidence_sha256"],
                "selection_payload_sha256": source_evidence["selection_payload_sha256"],
                "immutable_revision": VNGRS_REVISION,
                "selected_paths": paths,
            }
        ),
        "request_ledger.jsonl": request_payload,
        "record_manifest.jsonl": record_payload,
        "raw_population_metrics.json": canonical_json_bytes(
            {
                "record_manifest_sha256": record_sha,
                "request_ledger_sha256": request_sha,
                "source_repository": VNGRS_REPOSITORY,
                "immutable_revision": VNGRS_REVISION,
                "raw_count": 10_000,
                "sample_index_count": 10_000,
                "sample_index_min": 0,
                "sample_index_max": 9_999,
                "source_identity_unique": True,
                "raw_turkish_count": 10_000,
                "raw_turkish_fraction": 1.0,
                "raw_unknown_lid_count": 0,
            }
        ),
        "retained_population_metrics.json": canonical_json_bytes(
            {
                "record_manifest_sha256": record_sha,
                "raw_count": 10_000,
                "retained_count": 10_000,
                "retained_quality_rate": 1.0,
                "retained_pii_count": 0,
                "retained_quality_bad_count": 0,
                "tier3_contamination_count": 0,
            }
        ),
        "dedup_metrics.json": canonical_json_bytes(
            {
                "record_manifest_sha256": record_sha,
                "raw_count": 10_000,
                "exact_duplicate_count": 0,
                "exact_duplicate_rate": 0.0,
                "near_dedup_input_sha256": retained_input,
                "near_dedup_feature_cap": None,
                "near_dedup_version": "near-dedup-v1",
                "near_dedup_evidence_class": "hash_bound_execution_evidence",
                "near_dedup_affected_record_ids": [],
                "near_dedup_pairs": [],
                "near_dedup_affected_record_count": 0,
                "near_dedup_affected_record_rate": 0.0,
            }
        ),
        "contamination_overlap_metrics.json": canonical_json_bytes(
            {
                "record_manifest_sha256": record_sha,
                "request_ledger_sha256": request_sha,
                "benchmark_overlap_input_sha256": overlap_input,
                "split_input_sha256": split_input,
                "benchmark_overlap_count": 0,
                "synthetic_contamination_count": 0,
                "tier2_retained_count": 0,
                "tier3_contamination_count": 0,
                "split_document_disjoint": True,
                "split_namespace": "vngrs_primary_in_domain_heldout_v2",
                "split_seed": 42,
            }
        ),
    }
    artifact_rows = build_output_artifact_manifest(
        {
            path: {"path": path, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
            for path, payload in artifacts_payloads.items()
        }
    )
    output_manifest_payload = b"".join(canonical_json_bytes(row) + b"\n" for row in artifact_rows)
    output_manifest_sha = hashlib.sha256(output_manifest_payload).hexdigest()
    final_audit = build_final_audit(artifact_rows, manifest_sha256=output_manifest_sha)
    return {
        "preparation_result": {
            "raw_manifest": records,
            "sample_target_records": 10_000,
            "gate": {"gate_results": {"raw_count_exact": False}},
        },
        "request_ledger": requests,
        "source_evidence": source_evidence,
        "output_artifact_manifest": artifact_rows,
        "output_artifact_manifest_sha256": output_manifest_sha,
        "output_artifact_manifest_payload": output_manifest_payload,
        "artifact_payloads": artifacts_payloads,
        "source_evidence_artifact_payloads": source_evidence_artifact_payloads,
        "request_response_payloads": request_response_payloads,
        "final_audit": final_audit,
        "final_audit_payload": canonical_json_bytes(final_audit),
    }


def _run_final_graph(graph: dict[str, object]) -> dict[str, object]:
    return evaluate_final_contract(
        graph["preparation_result"],
        request_ledger=graph["request_ledger"],
        source_evidence=graph["source_evidence"],
        output_artifact_manifest=graph["output_artifact_manifest"],
        output_artifact_manifest_sha256=graph["output_artifact_manifest_sha256"],
        output_artifact_manifest_payload=graph["output_artifact_manifest_payload"],
        artifact_payloads=graph["artifact_payloads"],
        source_evidence_artifact_payloads=graph["source_evidence_artifact_payloads"],
        request_response_payloads=graph["request_response_payloads"],
        final_audit=graph["final_audit"],
        final_audit_payload=graph["final_audit_payload"],
    )


def test_structural_synthetic_control_and_one_at_a_time_fail_closed_mutations() -> None:
    graph = _valid_final_evidence_graph()
    baseline = _run_final_graph(graph)
    assert baseline["status"] == "BLOCKED"
    assert "structural_synthetic_control_not_source_evidence" in baseline["blockers"]
    assert "sampling_schedule_or_source_windows_invalid" in baseline["blockers"]
    mutations = {
        "caller_target_1": lambda item: item["preparation_result"].update({"sample_target_records": 1}),
        "missing_record_9999": lambda item: item["preparation_result"]["raw_manifest"].pop(),
        "wrong_shard": lambda item: item["preparation_result"]["raw_manifest"][0].update({"shard_path": "data/train-00013-of-00284.parquet"}),
        "duplicate_sample_index": lambda item: item["preparation_result"]["raw_manifest"][1].update({"sample_index": 0}),
        "orphan_request": lambda item: item["preparation_result"]["raw_manifest"][0].update({"request_id": "orphan"}),
        "response_length_101": lambda item: item["request_ledger"][0].update({"row_range_or_metadata_target": "offset=0,length=101"}),
        "failed_http_marked_success": lambda item: item["request_ledger"][0].update({"http_status": 500}),
        "broken_retry_chain": lambda item: item["request_ledger"][0].update({"attempt_ordinal": 1, "retry_ordinal": 1}),
        "fake_source_hash": lambda item: item["source_evidence"]["selected_shard_evidence"][0].update({"sha256": "0" * 64}),
        "fake_response_hash_binding": lambda item: item["request_response_payloads"].update({"responses/logical-000.json": b"tampered\n"}),
        "overlapping_source_window": lambda item: item["request_ledger"][1].update({"row_range_or_metadata_target": "offset=50,length=100"}),
        "schedule_mismatch": lambda item: item["source_evidence"]["sampling_schedule"]["shards"][0]["sampled_positions"].__setitem__(0, 999),
        "tampered_near_dedup_count_rate": lambda item: item["artifact_payloads"].update({
            "dedup_metrics.json": canonical_json_bytes({
                **json.loads(item["artifact_payloads"]["dedup_metrics.json"]),
                "near_dedup_affected_record_count": 1,
                "near_dedup_affected_record_rate": 0.0001,
            })
        }),
        "fake_artifact_bytes": lambda item: item["artifact_payloads"].update({"raw_population_metrics.json": b"{}"}),
        "unlinked_metric_artifact": lambda item: item["artifact_payloads"].update({
            "dedup_metrics.json": canonical_json_bytes({**json.loads(item["artifact_payloads"]["dedup_metrics.json"]), "record_manifest_sha256": "0" * 64})
        }),
        "altered_final_audit": lambda item: item["final_audit"].update({"self_reference": True}),
    }
    for label, mutate in mutations.items():
        candidate = copy.deepcopy(graph)
        mutate(candidate)
        result = _run_final_graph(candidate)
        assert result["status"] == "BLOCKED", label


def test_sampling_schedule_is_deterministic_and_records_request_feasibility() -> None:
    graph = _valid_final_evidence_graph()
    source_rows = graph["source_evidence"]["selected_shard_evidence"]
    schedule = build_sampling_schedule(source_rows)
    validation = validate_sampling_schedule(schedule, source_rows)
    assert schedule["target_records"] == 10_000
    assert schedule["schedule_sha256"] == canonical_json_sha256({key: value for key, value in schedule.items() if key != "schedule_sha256"})
    assert validation["minimum_contiguous_windows"] > 100
    assert validation["complete"] is False
    assert any("cannot fit" in error for error in validation["errors"])


def test_parent_hash_recomputation_cannot_bind_fake_child_source_evidence() -> None:
    graph = _valid_final_evidence_graph()
    source = copy.deepcopy(graph["source_evidence"])
    source["selected_shard_evidence"][0]["sha256"] = "0" * 64
    source["evidence_sha256"] = canonical_json_sha256({key: value for key, value in source.items() if key != "evidence_sha256"})
    validation = validate_final_source_evidence(
        source,
        artifact_payloads=graph["source_evidence_artifact_payloads"],
    )
    assert validation["complete"] is False
    assert any("artifact hash mismatch" in error for error in validation["errors"])


def _compact_varint(value: int) -> bytes:
    if value < 0:
        raise ValueError("fixture varint requires non-negative value")
    result = bytearray()
    while value >= 0x80:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)


def _compact_zigzag(value: int) -> bytes:
    return _compact_varint((value << 1) ^ (value >> 63))


def _compact_field(field_id: int, type_code: int, payload: bytes, previous_field_id: int) -> tuple[bytes, int]:
    delta = field_id - previous_field_id
    if 1 <= delta <= 15:
        return bytes([(delta << 4) | type_code]) + payload, field_id
    return bytes([type_code]) + _compact_zigzag(field_id) + payload, field_id


def _compact_struct(fields: list[tuple[int, int, bytes]]) -> bytes:
    result = bytearray()
    previous = 0
    for field_id, type_code, payload in fields:
        encoded, previous = _compact_field(field_id, type_code, payload, previous)
        result.extend(encoded)
    result.append(0)
    return bytes(result)


def _compact_binary(value: bytes) -> bytes:
    return _compact_varint(len(value)) + value


def _compact_list(element_type: int, values: list[bytes]) -> bytes:
    size = len(values)
    header = bytes([(size << 4) | element_type]) if size < 15 else bytes([0xF0 | element_type]) + _compact_varint(size)
    return header + b"".join(values)


def _minimal_parquet_footer(row_count: int, compressed_bytes: int, uncompressed_bytes: int) -> bytes:
    schema_element = _compact_struct(
        [
            (1, 5, _compact_zigzag(6)),
            (4, 8, _compact_binary(b"text")),
        ]
    )
    column_metadata = _compact_struct(
        [
            (1, 5, _compact_zigzag(6)),
            (2, 9, _compact_list(5, [])),
            (3, 9, _compact_list(8, [_compact_binary(b"text")])),
            (4, 5, _compact_zigzag(0)),
            (5, 6, _compact_zigzag(row_count)),
            (6, 6, _compact_zigzag(uncompressed_bytes)),
            (7, 6, _compact_zigzag(compressed_bytes)),
            (9, 6, _compact_zigzag(100)),
        ]
    )
    column_chunk = _compact_struct(
        [
            (2, 6, _compact_zigzag(100)),
            (3, 12, column_metadata),
        ]
    )
    row_group = _compact_struct(
        [
            (1, 9, _compact_list(12, [column_chunk])),
            (2, 6, _compact_zigzag(uncompressed_bytes)),
            (3, 6, _compact_zigzag(row_count)),
            (5, 6, _compact_zigzag(100)),
            (6, 6, _compact_zigzag(compressed_bytes)),
        ]
    )
    metadata = _compact_struct(
        [
            (1, 5, _compact_zigzag(1)),
            (2, 9, _compact_list(12, [schema_element])),
            (3, 6, _compact_zigzag(row_count)),
            (4, 9, _compact_list(12, [row_group])),
        ]
    )
    return metadata + len(metadata).to_bytes(4, "little") + b"PAR1"


def _valid_metadata_footer_package() -> tuple[dict[str, object], dict[str, bytes], bytes, bytes]:
    """Build a local positive control for the non-executed 151an feasibility validator."""

    selection = build_selection_evidence()
    paths = list(selection["selected_paths"])
    ordinals = list(selection["selected_ordinals"])
    artifact_payloads: dict[str, bytes] = {}
    shard_rows: list[dict[str, object]] = []
    route_rows: list[dict[str, object]] = []
    request_rows: list[dict[str, object]] = []

    license_artifact = "evidence/license/README.md"
    license_payload = b"CC BY-NC-SA 4.0\n"
    artifact_payloads[license_artifact] = license_payload
    license_sha = hashlib.sha256(license_payload).hexdigest()

    for index, (path, ordinal) in enumerate(zip(paths, ordinals, strict=True)):
        row_count = 1_000 + index
        compressed_bytes = 20 + index
        uncompressed_bytes = 30 + index
        object_id = f"sha256-{ordinal:05d}"
        object_size_bytes = 1_000_000 + ordinal
        object_metadata_artifact = f"evidence/head/{ordinal:05d}.json"
        route_artifact = object_metadata_artifact
        trailer_artifact = f"evidence/footer_trailer/{ordinal:05d}.bin"
        footer_artifact = f"evidence/footer/{ordinal:05d}.bin"
        header_payload = canonical_json_bytes(
            {
                "path": path,
                "immutable_revision": VNGRS_REVISION,
                "object_id": object_id,
                "object_size_bytes": object_size_bytes,
                "request_url": parquet_resolve_url(path),
                "final_url": parquet_resolve_url(path),
                "redirect_chain": [],
                "http_status": 200,
                "content_length": object_size_bytes,
                "etag": f'"etag-{ordinal:05d}"',
                "lfs_oid": object_id,
                "content_type": "application/vnd.apache.parquet",
                "content_encoding": "identity",
            }
        )
        footer_payload = _minimal_parquet_footer(row_count, compressed_bytes, uncompressed_bytes)
        trailer_payload = footer_payload[-8:]
        artifact_payloads[object_metadata_artifact] = header_payload
        artifact_payloads[trailer_artifact] = trailer_payload
        artifact_payloads[footer_artifact] = footer_payload
        parsed_footer = parse_parquet_footer(footer_payload)
        shard_rows.append(
            {
                "path": path,
                "ordinal": ordinal,
                "shard_count": 284,
                "immutable_revision": VNGRS_REVISION,
                "row_count": parsed_footer["row_count"],
                "row_group_count": parsed_footer["row_group_count"],
                "row_group_layout": parsed_footer["row_group_layout"],
                "compressed_bytes": parsed_footer["compressed_bytes"],
                "uncompressed_bytes": parsed_footer["uncompressed_bytes"],
                "object_id": object_id,
                "object_id_kind": "lfs_oid",
                "object_size_bytes": object_size_bytes,
                "object_sha256": None,
                "object_sha256_status": "unverified_footer_only",
                "etag": f'"etag-{ordinal:05d}"',
                "content_type": "application/vnd.apache.parquet",
                "content_encoding": "identity",
                "object_metadata_evidence_artifact": object_metadata_artifact,
                "object_metadata_evidence_sha256": hashlib.sha256(header_payload).hexdigest(),
                "footer_trailer_evidence_artifact": trailer_artifact,
                "footer_trailer_sha256": hashlib.sha256(trailer_payload).hexdigest(),
                "footer_metadata_length": parsed_footer["metadata_length"],
                "footer_evidence_artifact": footer_artifact,
                "footer_sha256": hashlib.sha256(footer_payload).hexdigest(),
                "license_evidence_artifact": license_artifact,
                "license_bytes_sha256": license_sha,
            }
        )
        route_rows.append(
            {
                "path": path,
                "route_kind": METADATA_FOOTER_ROUTE_KIND,
                "request_url": parquet_resolve_url(path),
                "immutable_revision": VNGRS_REVISION,
                "split": "train",
                "http_method": "GET",
                "range_header": METADATA_FOOTER_TRAILER_RANGE_HEADER,
                "footer_range_header_template": METADATA_FOOTER_FOOTER_RANGE_TEMPLATE,
                "status": "verified",
                "final_url": parquet_resolve_url(path),
                "redirect_chain": [],
                "http_status": 200,
                "content_length": object_size_bytes,
                "etag": f'"etag-{ordinal:05d}"',
                "lfs_oid": object_id,
                "content_type": "application/vnd.apache.parquet",
                "content_encoding": "identity",
                "route_evidence_artifact": route_artifact,
                "route_evidence_sha256": hashlib.sha256(header_payload).hexdigest(),
            }
        )
        for role, method, status, range_header, artifact, payload, response_bytes in (
            (
                "head_metadata_route",
                "HEAD",
                200,
                None,
                object_metadata_artifact,
                header_payload,
                len(header_payload),
            ),
            (
                "footer_trailer",
                "GET",
                206,
                METADATA_FOOTER_TRAILER_RANGE_HEADER,
                trailer_artifact,
                trailer_payload,
                len(trailer_payload),
            ),
            (
                "footer_bytes",
                "GET",
                206,
                f"bytes={object_size_bytes - len(footer_payload)}-",
                footer_artifact,
                footer_payload,
                len(footer_payload),
            ),
        ):
            if role == "head_metadata_route":
                content_range = None
            elif role == "footer_trailer":
                content_range = f"bytes={object_size_bytes - 8}-{object_size_bytes - 1}/{object_size_bytes}"
            else:
                content_range = f"bytes={object_size_bytes - len(payload)}-{object_size_bytes - 1}/{object_size_bytes}"
            request_rows.append(
                {
                    "request_id": f"{role}-{index:05d}",
                    "attempt_id": f"attempt-{role}-{index:05d}-0",
                    "attempt_ordinal": 0,
                    "retry_ordinal": 0,
                    "evidence_role": role,
                    "path": path,
                    "request_url": parquet_resolve_url(path),
                    "final_url": parquet_resolve_url(path),
                    "redirect_chain": [],
                    "route_kind": METADATA_FOOTER_ROUTE_KIND,
                    "immutable_revision": VNGRS_REVISION,
                    "split": "train",
                    "http_method": method,
                    "range_header": range_header,
                    "http_status": status,
                    "response_content_length": len(payload),
                    "content_range": content_range,
                    "etag": f'"etag-{ordinal:05d}"',
                    "lfs_oid": object_id,
                    "content_type": "application/vnd.apache.parquet",
                    "content_encoding": "identity",
                    "response_transferred_bytes": response_bytes,
                    "response_evidence_artifact": artifact,
                    "response_sha256": hashlib.sha256(payload).hexdigest(),
                    "request_outcome": "metadata_success",
                    "failure_class": "none",
                    "retryable_error": None,
                    "response_present": True,
                }
            )

    request_rows.append(
        {
            "request_id": "license-00000",
            "attempt_id": "attempt-license-00000-0",
            "attempt_ordinal": 0,
            "retry_ordinal": 0,
            "evidence_role": "license_attribution",
            "path": "README.md",
            "request_url": dataset_license_resolve_url(),
            "final_url": dataset_license_resolve_url(),
            "redirect_chain": [],
            "route_kind": METADATA_FOOTER_ROUTE_KIND,
            "immutable_revision": VNGRS_REVISION,
            "split": "train",
            "http_method": "GET",
            "range_header": None,
            "http_status": 200,
            "response_content_length": len(license_payload),
            "content_range": None,
            "etag": '"license-etag"',
            "lfs_oid": None,
            "content_type": "text/plain",
            "content_encoding": "identity",
            "response_transferred_bytes": len(license_payload),
            "response_evidence_artifact": license_artifact,
            "response_sha256": license_sha,
            "request_outcome": "metadata_success",
            "failure_class": "none",
            "retryable_error": None,
            "response_present": True,
        }
    )

    artifact_rows = [
        {
            "relative_path": name,
            "artifact_kind": (
                "head_metadata_route"
                if "/head/" in name
                else "parquet_footer_trailer"
                if "/footer_trailer/" in name
                else "parquet_footer_bytes"
                if "/footer/" in name
                else "license_attribution_bytes"
            ),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "contains_corpus_rows": False,
        }
        for name, payload in sorted(artifact_payloads.items())
    ]
    artifact_manifest_payload = serialize_metadata_footer_artifact_manifest(artifact_rows)
    schedule = build_sampling_schedule(shard_rows)
    projection = build_metadata_footer_feasibility_projection(
        shard_rows, request_rows, evidence_artifact_count=len(artifact_rows)
    )
    projection["projected_evidence_artifact_count"] = len(artifact_rows)
    audit = {
        "final_path": "metadata_footer_audit.json",
        "manifest_path": "evidence_artifact_manifest.jsonl",
        "scratch_root": METADATA_FOOTER_SCRATCH_ROOT,
        "self_reference": False,
        "artifact_paths": [row["relative_path"] for row in artifact_rows],
        "artifact_count": len(artifact_rows),
        "artifact_total_bytes": sum(row["bytes"] for row in artifact_rows),
        "request_count": len(request_rows),
        "retry_count": 0,
        "logical_request_attempt_count": len(request_rows),
        "http_hop_count": len(request_rows),
        "redirect_hop_count": 0,
        "max_logical_request_attempts": 121,
        "max_http_hops": 242,
        "redirect_hop_retry_separation": True,
        "total_response_bytes": sum(row["response_transferred_bytes"] for row in request_rows),
        "max_response_bytes": max(row["response_transferred_bytes"] for row in request_rows),
        "output_file_count": len(artifact_rows) + len(METADATA_FOOTER_OUTPUT_PATHS),
        "new_inode_count": len(artifact_rows) + len(METADATA_FOOTER_OUTPUT_PATHS),
        "write_order": list(METADATA_FOOTER_OUTPUT_PATHS),
        "contract_sha256": METADATA_FOOTER_CONTRACT_SHA256,
        "manifest_sha256": hashlib.sha256(artifact_manifest_payload).hexdigest(),
        "route_kind": METADATA_FOOTER_ROUTE_KIND,
        "corpus_rows_retrieved": 0,
    }
    audit_payload = canonical_json_bytes(audit)
    return {
        "source_repository": VNGRS_REPOSITORY,
        "immutable_revision": VNGRS_REVISION,
        "split": "train",
        "schema": ["text", "corpus", "original_id"],
        "selected_paths": paths,
        "selected_ordinals": ordinals,
        "selection_payload": selection,
        "selection_payload_sha256": canonical_json_sha256(selection),
        "shard_metadata": shard_rows,
        "route_ledger": route_rows,
        "request_ledger": request_rows,
        "artifact_manifest": artifact_rows,
        "artifact_manifest_sha256": hashlib.sha256(artifact_manifest_payload).hexdigest(),
        "sampling_schedule": schedule,
        "feasibility_projection": projection,
        "scratch_root": METADATA_FOOTER_SCRATCH_ROOT,
        "metadata_footer_audit": audit,
        "metadata_footer_audit_sha256": hashlib.sha256(audit_payload).hexdigest(),
        "output_paths": list(METADATA_FOOTER_OUTPUT_PATHS),
    }, artifact_payloads, artifact_manifest_payload, audit_payload


def _append_retry_attempts(
    package: dict[str, object],
    payloads: dict[str, bytes],
    *,
    count: int,
    response_bearing: bool = True,
) -> tuple[bytes, bytes]:
    """Add bounded retry attempts to one logical HEAD chain and rebuild all bindings."""

    request_rows = package["request_ledger"]
    terminal = next(row for row in request_rows if row["request_id"] == "head_metadata_route-00000")
    terminal["attempt_ordinal"] = count
    terminal["retry_ordinal"] = count
    for ordinal in range(count):
        artifact = f"evidence/retry/head-00000-{ordinal:02d}.bin" if response_bearing else None
        payload = f"retry-response-{ordinal:02d}".encode("ascii") if response_bearing else None
        if artifact is not None and payload is not None:
            payloads[artifact] = payload
        request_rows.append(
            {
                "request_id": terminal["request_id"],
                "attempt_id": f"attempt-head-00000-{ordinal + 1}",
                "attempt_ordinal": ordinal,
                "retry_ordinal": ordinal,
                "evidence_role": "head_metadata_route",
                "path": terminal["path"],
                "request_url": terminal["request_url"],
                "final_url": terminal["request_url"] if response_bearing else None,
                "redirect_chain": [],
                "route_kind": terminal["route_kind"],
                "immutable_revision": terminal["immutable_revision"],
                "split": terminal["split"],
                "http_method": terminal["http_method"],
                "range_header": terminal["range_header"],
                "http_status": 429 if response_bearing else None,
                "response_content_length": len(payload) if payload is not None else None,
                "content_range": None,
                "etag": None,
                "lfs_oid": None,
                "content_type": "text/plain" if response_bearing else None,
                "content_encoding": "identity" if response_bearing else None,
                "response_transferred_bytes": len(payload) if payload is not None else 0,
                "response_evidence_artifact": artifact,
                "response_sha256": hashlib.sha256(payload).hexdigest() if payload is not None else None,
                "request_outcome": "retryable_failure",
                "failure_class": "http_retryable" if response_bearing else "transport_no_response",
                "retryable_error": "http_429" if response_bearing else "transport_timeout",
                "response_present": response_bearing,
            }
        )

    artifact_rows = [dict(row) for row in package["artifact_manifest"]]
    if response_bearing:
        for name, payload in sorted(payloads.items()):
            if name not in {row["relative_path"] for row in artifact_rows}:
                artifact_rows.append(
                    {
                        "relative_path": name,
                        "artifact_kind": "retry_response",
                        "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "contains_corpus_rows": False,
                    }
                )
    package["artifact_manifest"] = artifact_rows
    manifest_payload = serialize_metadata_footer_artifact_manifest(artifact_rows)
    package["artifact_manifest_sha256"] = hashlib.sha256(manifest_payload).hexdigest()
    package["feasibility_projection"] = build_metadata_footer_feasibility_projection(
        package["shard_metadata"], request_rows, evidence_artifact_count=len(artifact_rows)
    )
    audit = dict(package["metadata_footer_audit"])
    audit.update(
        {
            "artifact_paths": [row["relative_path"] for row in artifact_rows],
            "artifact_count": len(artifact_rows),
            "artifact_total_bytes": sum(row["bytes"] for row in artifact_rows),
            "request_count": len(request_rows),
            "retry_count": count,
            "logical_request_attempt_count": len(request_rows),
            "http_hop_count": len(request_rows),
            "redirect_hop_count": 0,
            "max_logical_request_attempts": 121,
            "max_http_hops": 242,
            "redirect_hop_retry_separation": True,
            "total_response_bytes": sum(row["response_transferred_bytes"] for row in request_rows),
            "max_response_bytes": max(row["response_transferred_bytes"] for row in request_rows),
            "output_file_count": len(artifact_rows) + len(METADATA_FOOTER_OUTPUT_PATHS),
            "new_inode_count": len(artifact_rows) + len(METADATA_FOOTER_OUTPUT_PATHS),
            "manifest_sha256": package["artifact_manifest_sha256"],
        }
    )
    package["metadata_footer_audit"] = audit
    audit_payload = canonical_json_bytes(audit)
    package["metadata_footer_audit_sha256"] = hashlib.sha256(audit_payload).hexdigest()
    return manifest_payload, audit_payload


def test_metadata_footer_validator_binds_object_metadata_separately_from_full_object_hash() -> None:
    package, payloads, manifest_payload, audit_payload = _valid_metadata_footer_package()
    validation = validate_metadata_footer_feasibility(
        package,
        artifact_payloads=payloads,
        artifact_manifest_payload=manifest_payload,
        metadata_footer_audit_payload=audit_payload,
    )
    assert validation["complete"] is True
    assert validation["selected_shard_count"] == 32
    assert validation["request_count"] == 97
    assert validation["total_response_bytes"] > 0
    assert all(row["object_sha256"] is None for row in package["shard_metadata"])
    assert all(row["object_metadata_evidence_sha256"] != row["footer_sha256"] for row in package["shard_metadata"])


def test_metadata_footer_validator_accepts_real_retryable_http_failure_then_terminal_success() -> None:
    package, payloads, _, _ = _valid_metadata_footer_package()
    manifest_payload, audit_payload = _append_retry_attempts(package, payloads, count=1)
    validation = validate_metadata_footer_feasibility(
        package,
        artifact_payloads=payloads,
        artifact_manifest_payload=manifest_payload,
        metadata_footer_audit_payload=audit_payload,
    )
    assert validation["complete"] is True
    assert validation["retry_count"] == 1
    assert validation["request_count"] == 98
    assert package["feasibility_projection"]["projected_regular_file_count"] == 105


def test_metadata_footer_validator_accepts_no_response_transport_retry() -> None:
    package, payloads, _, _ = _valid_metadata_footer_package()
    manifest_payload, audit_payload = _append_retry_attempts(
        package, payloads, count=1, response_bearing=False
    )
    validation = validate_metadata_footer_feasibility(
        package,
        artifact_payloads=payloads,
        artifact_manifest_payload=manifest_payload,
        metadata_footer_audit_payload=audit_payload,
    )
    assert validation["complete"] is True
    assert validation["retry_count"] == 1
    assert validation["request_count"] == 98
    assert validation["total_response_bytes"] == package["metadata_footer_audit"]["total_response_bytes"]


def test_metadata_footer_validator_freezes_retry_and_file_inode_boundary_at_24() -> None:
    boundary_package, boundary_payloads, _, _ = _valid_metadata_footer_package()
    boundary_manifest, boundary_audit = _append_retry_attempts(
        boundary_package, boundary_payloads, count=24
    )
    boundary_validation = validate_metadata_footer_feasibility(
        boundary_package,
        artifact_payloads=boundary_payloads,
        artifact_manifest_payload=boundary_manifest,
        metadata_footer_audit_payload=boundary_audit,
    )
    assert boundary_validation["complete"] is True
    assert boundary_validation["retry_count"] == 24
    assert boundary_package["feasibility_projection"]["projected_regular_file_count"] == 128
    assert boundary_package["feasibility_projection"]["projected_new_inode_count"] == 128

    over_package, over_payloads, _, _ = _valid_metadata_footer_package()
    over_manifest, over_audit = _append_retry_attempts(over_package, over_payloads, count=25)
    over_validation = validate_metadata_footer_feasibility(
        over_package,
        artifact_payloads=over_payloads,
        artifact_manifest_payload=over_manifest,
        metadata_footer_audit_payload=over_audit,
    )
    assert over_validation["complete"] is False
    assert any("retry bound" in error or "output file" in error for error in over_validation["errors"])


def test_metadata_footer_validator_rejects_relabelled_success_as_retryable_failure() -> None:
    package, payloads, manifest_payload, audit_payload = _valid_metadata_footer_package()
    broken = copy.deepcopy(package)
    success = broken["request_ledger"][0]
    success["request_outcome"] = "retryable_failure"
    success["failure_class"] = "http_retryable"
    success["retryable_error"] = "http_503"
    validation = validate_metadata_footer_feasibility(
        broken,
        artifact_payloads=payloads,
        artifact_manifest_payload=manifest_payload,
        metadata_footer_audit_payload=audit_payload,
    )
    assert validation["complete"] is False
    assert any("relabelled" in error or "429 or 503" in error for error in validation["errors"])


def test_metadata_footer_validator_rejects_rows_route_and_full_object_artifact() -> None:
    package, payloads, manifest_payload, audit_payload = _valid_metadata_footer_package()
    broken = copy.deepcopy(package)
    broken["route_ledger"][0]["route_kind"] = "rows"
    broken["route_ledger"][0]["request_url"] = "https://datasets-server.huggingface.co/rows?offset=0&length=1"
    broken["artifact_manifest"][0]["artifact_kind"] = "full_shard"
    validation = validate_metadata_footer_feasibility(
        broken,
        artifact_payloads=payloads,
        artifact_manifest_payload=manifest_payload,
        metadata_footer_audit_payload=audit_payload,
    )
    assert validation["complete"] is False
    assert any("route_kind" in error or "Dataset Viewer" in error or "forbidden" in error for error in validation["errors"])


def test_metadata_footer_validator_rejects_footer_hash_and_forbidden_row_payload() -> None:
    package, payloads, manifest_payload, audit_payload = _valid_metadata_footer_package()
    broken = copy.deepcopy(package)
    footer_name = broken["shard_metadata"][0]["footer_evidence_artifact"]
    payloads[footer_name] = b'{"text":"forbidden corpus row"}'
    broken["shard_metadata"][0]["footer_sha256"] = hashlib.sha256(payloads[footer_name]).hexdigest()
    broken["artifact_manifest"] = [dict(row) for row in broken["artifact_manifest"]]
    for row in broken["artifact_manifest"]:
        if row["relative_path"] == footer_name:
            row["bytes"] = len(payloads[footer_name])
            row["sha256"] = hashlib.sha256(payloads[footer_name]).hexdigest()
    validation = validate_metadata_footer_feasibility(
        broken,
        artifact_payloads=payloads,
        artifact_manifest_payload=manifest_payload,
        metadata_footer_audit_payload=audit_payload,
    )
    assert validation["complete"] is False
    assert any("footer" in error or "corpus" in error for error in validation["errors"])


def test_metadata_footer_validator_freezes_root_outputs_and_fixture_only_window_count() -> None:
    package, payloads, manifest_payload, audit_payload = _valid_metadata_footer_package()
    projection = package["feasibility_projection"]
    assert projection["sampling_schedule_status"] == "computed_pre_row_retrieval"
    assert projection["corpus_rows_retrieved"] == 0
    assert projection["sample_manifest_created"] is False
    assert validate_metadata_footer_output_paths(
        package["output_paths"], scratch_root=package["scratch_root"]
    )["complete"] is True
    assert validate_metadata_footer_output_paths(
        package["output_paths"], scratch_root="/tmp/wrong-root"
    )["complete"] is False
    assert package["feasibility_projection"]["minimum_contiguous_windows"] > 100
    validation = validate_metadata_footer_feasibility(
        package,
        artifact_payloads=payloads,
        artifact_manifest_payload=manifest_payload,
        metadata_footer_audit_payload=audit_payload,
    )
    assert validation["complete"] is True


def _validate_metadata_footer_fixture(
    package: dict[str, object],
    payloads: dict[str, bytes],
    manifest_payload: bytes,
    audit_payload: bytes,
) -> dict[str, object]:
    return validate_metadata_footer_feasibility(
        package,
        artifact_payloads=payloads,
        artifact_manifest_payload=manifest_payload,
        metadata_footer_audit_payload=audit_payload,
    )


def test_parquet_footer_parser_rejects_framing_and_metadata_length_attacks() -> None:
    footer = _minimal_parquet_footer(1_000, 20, 30)
    parsed = parse_parquet_footer(footer)
    assert parsed["row_count"] == 1_000
    assert parse_parquet_trailer(footer[-8:])["metadata_length"] == parsed["metadata_length"]

    with pytest.raises(ValueError, match="truncated|exactly eight|magic"):
        parse_parquet_footer(footer[:-1])
    with pytest.raises(ValueError, match="magic"):
        parse_parquet_footer(footer[:-4] + b"NOPE")
    with pytest.raises(ValueError, match="complete declared metadata"):
        parse_parquet_footer(
            footer[:-8]
            + (parsed["metadata_length"] + 1).to_bytes(4, "little")
            + b"PAR1"
        )


def test_parquet_footer_parser_compatibility_with_independent_writer() -> None:
    pyarrow = pytest.importorskip(
        "pyarrow",
        reason="independent Parquet-writer compatibility preflight unavailable locally; rerun before source access",
    )
    import pyarrow.parquet as parquet

    table = pyarrow.table({"text": ["a", "b", "c"]})
    sink = pyarrow.BufferOutputStream()
    parquet.write_table(table, sink, compression="snappy")
    payload = sink.getvalue().to_pybytes()
    trailer = parse_parquet_trailer(payload[-8:])
    footer = payload[-(trailer["metadata_length"] + 8) :]
    parsed = parse_parquet_footer(footer)
    assert parsed["row_count"] == 3
    assert parsed["row_group_count"] >= 1


def test_metadata_footer_executor_independent_writer_preflight_is_explicit() -> None:
    result = independent_writer_self_check()
    assert result["status"] in {"PASS", "BLOCKED"}
    if result["status"] == "BLOCKED":
        assert result["reason"] in {
            "pyarrow_unavailable",
            "independent_writer_bad_magic",
            "independent_writer_parser_mismatch",
            "independent_writer_parser_failure",
        }


class _FakeResponse:
    def __init__(self, status: int, payload: bytes, *, headers: dict[str, str] | None = None, url: str) -> None:
        self.status = status
        self.code = status
        self.headers = headers or {}
        self._payload = payload
        self._url = url
        self.read_limits: list[int] = []

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def geturl(self) -> str:
        return self._url

    def read(self, limit: int = -1) -> bytes:
        self.read_limits.append(limit)
        if limit >= 0:
            return self._payload[:limit]
        return self._payload


class _FakeOpener:
    def __init__(self, responses: list[object]) -> None:
        self.responses = list(responses)

    def open(self, request: object, timeout: int) -> object:
        del request, timeout
        if not self.responses:
            raise AssertionError("fake opener exhausted")
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


class _RecordingOpener(_FakeOpener):
    def __init__(self, responses: list[object]) -> None:
        super().__init__(responses)
        self.requests: list[object] = []

    def open(self, request: object, timeout: int) -> object:
        self.requests.append(request)
        return super().open(request, timeout)


def _fake_response(status: int, payload: bytes = b"x", *, url: str = "https://example.test/route") -> _FakeResponse:
    return _FakeResponse(status, payload, headers={"Content-Type": "application/octet-stream"}, url=url)


def test_metadata_executor_accepts_24_retries_before_terminal_success() -> None:
    responses = [_fake_response(429) for _ in range(24)] + [_fake_response(200, b"ok")]
    client = BoundedClient(_FakeOpener(responses))  # type: ignore[arg-type]

    result, payload = client.request_with_retries(
        request_id="retry-boundary",
        role="license_attribution",
        path="README.md",
        url="https://example.test/route",
        method="GET",
        range_header=None,
        expected_status=200,
        artifact_name="evidence/license/README.md",
    )

    assert result.status == 200
    assert payload == b"ok"
    assert client.attempt_count == 25
    assert client.retry_count == 24
    assert len(client.request_rows) == 25
    assert len(client.artifact_payloads) == 25
    assert client.total_response_bytes == 26


def test_metadata_executor_rejects_the_25th_retry_before_retaining_artifact() -> None:
    client = BoundedClient(_FakeOpener([_fake_response(429) for _ in range(25)]))  # type: ignore[arg-type]

    with pytest.raises(ExecutionBlocked, match="24-retry") as caught:
        client.request_with_retries(
            request_id="retry-over-bound",
            role="license_attribution",
            path="README.md",
            url="https://example.test/route",
            method="GET",
            range_header=None,
            expected_status=200,
            artifact_name="evidence/license/README.md",
        )

    assert caught.value.context["phase"] == "retry_bound"
    assert caught.value.context["attempt_count"] == 25
    assert caught.value.context["retry_count"] == 24
    assert len(client.request_rows) == 24
    assert len(client.artifact_payloads) == 24


def test_metadata_executor_fails_before_retaining_cumulative_response_overflow() -> None:
    client = BoundedClient(_FakeOpener([_fake_response(200, b"xx")]))  # type: ignore[arg-type]
    client.total_response_bytes = metadata_executor_module.METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES - 1

    with pytest.raises(ExecutionBlocked, match="cumulative 64 MiB") as caught:
        client.request_with_retries(
            request_id="response-byte-overflow",
            role="license_attribution",
            path="README.md",
            url="https://example.test/route",
            method="GET",
            range_header=None,
            expected_status=200,
            artifact_name="evidence/license/README.md",
        )

    assert caught.value.context["phase"] == "response_byte_bound"
    assert not client.artifact_payloads
    assert not client.request_rows


def test_metadata_executor_caps_unknown_normal_body_by_remaining_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(metadata_executor_module, "METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES", 10)
    response = _fake_response(200, b"x" * 100)
    client = BoundedClient(_FakeOpener([response]))  # type: ignore[arg-type]
    client.total_response_bytes = 9

    with pytest.raises(ExecutionBlocked) as caught:
        client.request_with_retries(
            request_id="normal-read-budget",
            role="license_attribution",
            path="README.md",
            url="https://example.test/route",
            method="GET",
            range_header=None,
            expected_status=200,
            artifact_name="evidence/license/README.md",
        )

    assert response.read_limits == [2]
    assert caught.value.context["phase"] == "response_byte_bound"
    assert caught.value.context["read_limit"] == 2
    assert not client.artifact_payloads
    assert not client.request_rows


def test_metadata_executor_rejects_declared_length_before_body_read(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(metadata_executor_module, "METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES", 10)
    response = _FakeResponse(
        200,
        b"x" * 100,
        headers={"Content-Length": "2", "Content-Type": "application/octet-stream"},
        url="https://example.test/route",
    )
    client = BoundedClient(_FakeOpener([response]))  # type: ignore[arg-type]
    client.total_response_bytes = 9

    with pytest.raises(ExecutionBlocked) as caught:
        client.request_with_retries(
            request_id="declared-length-read-budget",
            role="license_attribution",
            path="README.md",
            url="https://example.test/route",
            method="GET",
            range_header=None,
            expected_status=200,
            artifact_name="evidence/license/README.md",
        )

    assert response.read_limits == []
    assert caught.value.context["phase"] == "response_byte_bound"
    assert not client.artifact_payloads
    assert not client.request_rows


class _RecordingBytesIO(io.BytesIO):
    def __init__(self, payload: bytes) -> None:
        super().__init__(payload)
        self.read_limits: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.read_limits.append(size)
        return super().read(size)


def test_metadata_executor_caps_unknown_http_error_body_by_remaining_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(metadata_executor_module, "METADATA_FOOTER_MAX_TOTAL_RESPONSE_BYTES", 10)
    url = "https://example.test/route"
    stream = _RecordingBytesIO(b"x" * 100)
    retry = urllib.error.HTTPError(url, 429, "retry", {}, stream)
    client = BoundedClient(_FakeOpener([retry]))  # type: ignore[arg-type]
    client.total_response_bytes = 9

    with pytest.raises(ExecutionBlocked) as caught:
        client.request_with_retries(
            request_id="http-error-read-budget",
            role="license_attribution",
            path="README.md",
            url=url,
            method="GET",
            range_header=None,
            expected_status=200,
            artifact_name="evidence/license/README.md",
        )

    assert stream.read_limits == [2]
    assert caught.value.context["phase"] == "response_byte_bound"
    assert caught.value.context["read_limit"] == 2
    assert not client.artifact_payloads
    assert not client.request_rows


def test_metadata_executor_checks_artifact_slot_before_retry_insert() -> None:
    client = BoundedClient(_FakeOpener([_fake_response(429)]))  # type: ignore[arg-type]
    response_artifact_capacity = metadata_executor_module.METADATA_FOOTER_MAX_OUTPUT_FILES - len(
        metadata_executor_module.METADATA_FOOTER_OUTPUT_PATHS
    )
    client.artifact_payloads = {f"evidence/retry/seed-{index:03d}.bin": b"" for index in range(response_artifact_capacity)}

    with pytest.raises(ExecutionBlocked, match="artifact/file/inode") as caught:
        client.request_with_retries(
            request_id="artifact-slot-overflow",
            role="license_attribution",
            path="README.md",
            url="https://example.test/route",
            method="GET",
            range_header=None,
            expected_status=200,
            artifact_name="evidence/license/README.md",
        )

    assert caught.value.context["phase"] == "artifact_slot_bound"
    assert len(client.artifact_payloads) == response_artifact_capacity


def test_metadata_executor_preserves_3xx_failure_context() -> None:
    url = "https://example.test/route"
    redirect = urllib.error.HTTPError(
        url,
        302,
        "redirect",
        {"Location": "https://example.test/target"},
        io.BytesIO(),
    )
    client = BoundedClient(_FakeOpener([redirect]))  # type: ignore[arg-type]

    with pytest.raises(ExecutionBlocked, match="official Hugging Face CDN allowlist") as caught:
        client.request_with_retries(
            request_id="redirect-block",
            role="license_attribution",
            path="README.md",
            url=url,
            method="GET",
            range_header=None,
            expected_status=200,
            artifact_name="evidence/license/README.md",
        )

    assert caught.value.context["phase"] == "redirect_integrity"
    assert caught.value.context["location_sha256"] == hashlib.sha256(
        b"https://example.test/target"
    ).hexdigest()
    assert "location" not in caught.value.context


@pytest.mark.parametrize("target_host", ["cas-server.xethub.hf.co", "us.aws.cdn.hf.co"])
def test_metadata_executor_follows_one_secret_safe_cdn_hop_preserving_method_and_range(target_host: str) -> None:
    source_url = "https://huggingface.co/datasets/example/repo/resolve/abc/file.parquet"
    target_url = (
        f"https://{target_host}/xet/file.parquet"
        "?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Signature=super-secret"
    )
    redirect = urllib.error.HTTPError(
        source_url,
        302,
        "redirect",
        {"Location": target_url},
        io.BytesIO(),
    )
    opener = _RecordingOpener([redirect, _fake_response(206, b"ok", url=target_url)])
    client = BoundedClient(opener)  # type: ignore[arg-type]

    result, payload = client.request_with_retries(
        request_id="redirect-one-hop",
        role="footer_bytes",
        path="train-00004-of-00284.parquet",
        url=source_url,
        method="GET",
        range_header="bytes=10-",
        expected_status=206,
        artifact_name="evidence/footer/00000.bin",
    )

    assert payload == b"ok"
    assert result.final_url == source_url
    assert result.terminal_url == target_url
    assert client.attempt_count == 1
    assert client.http_hop_count == 2
    assert client.redirect_hop_count == 1
    assert len(client.request_rows) == 1
    row = client.request_rows[0]
    assert row["final_url"] == source_url
    assert len(row["redirect_chain"]) == 1
    assert "super-secret" not in json.dumps(row, sort_keys=True)
    assert opener.requests[1].get_header("Range") == "bytes=10-"
    assert opener.requests[1].get_header("Authorization") is None
    assert opener.requests[1].get_header("Cookie") is None


@pytest.mark.parametrize(
    "location",
    [
        "/relative-target",
        "http://cdn.hf.co/object",
        "https://user:password@cdn.hf.co/object",
        "https://cdn.hf.co/object#fragment",
        "https://cdn.hf.co:443/object",
        "https://evilcdn.hf.co/object",
    ],
)
def test_metadata_executor_rejects_unsafe_cdn_redirect_targets(location: str) -> None:
    source_url = "https://huggingface.co/datasets/example/repo/resolve/abc/file.parquet"
    redirect = urllib.error.HTTPError(
        source_url,
        302,
        "redirect",
        {"Location": location},
        io.BytesIO(),
    )
    client = BoundedClient(_FakeOpener([redirect]))  # type: ignore[arg-type]

    with pytest.raises(ExecutionBlocked, match="official Hugging Face CDN allowlist|absolute Location|redirect"):
        client._attempt(method="GET", url=source_url, range_header="bytes=10-")


def test_metadata_executor_rejects_a_second_cdn_redirect() -> None:
    source_url = "https://huggingface.co/datasets/example/repo/resolve/abc/file.parquet"
    first = urllib.error.HTTPError(
        source_url,
        302,
        "redirect",
        {"Location": "https://cdn.hf.co/first?signature=one"},
        io.BytesIO(),
    )
    second = urllib.error.HTTPError(
        "https://cdn.hf.co/first?signature=one",
        302,
        "redirect",
        {"Location": "https://xethub.hf.co/second?signature=two"},
        io.BytesIO(),
    )
    client = BoundedClient(_FakeOpener([first, second]))  # type: ignore[arg-type]

    with pytest.raises(ExecutionBlocked, match="second HTTP 302"):
        client._attempt(method="GET", url=source_url, range_header=None)

    assert client.http_hop_count == 2
    assert client.redirect_hop_count == 1


class _RaisingBytesIO(io.BytesIO):
    def read(self, size: int = -1) -> bytes:
        del size
        raise RuntimeError("synthetic response read failure")


def test_metadata_executor_preserves_http_error_status_when_response_read_fails() -> None:
    url = "https://example.test/route"
    error = urllib.error.HTTPError(url, 503, "unavailable", {}, _RaisingBytesIO())
    client = BoundedClient(_FakeOpener([error]))  # type: ignore[arg-type]

    with pytest.raises(ExecutionBlocked, match="unable to read the bounded HTTPError response") as caught:
        client.request_with_retries(
            request_id="http-error-read-failure",
            role="license_attribution",
            path="README.md",
            url=url,
            method="GET",
            range_header=None,
            expected_status=200,
            artifact_name="evidence/license/README.md",
        )

    assert caught.value.context["phase"] == "response_read_failure"
    assert caught.value.context["http_status"] == 503
    assert caught.value.context["response_read_exception"] == "RuntimeError"


def _fake_storage_command(
    command: list[str],
    root: str,
    *,
    human: dict[str, object] | None = None,
    exact: dict[str, object] | None = None,
    df_h: dict[str, object] | None = None,
    df_i: dict[str, object] | None = None,
    resolved: str | None = None,
    large: dict[str, object] | None = None,
    timeout: int = 30,
) -> dict[str, object]:
    del timeout
    base = {"command": command, "returncode": 0, "stdout": "ok\n", "stderr": "", "timed_out": False}
    if command[0] == "du" and command[1] == "-xsh":
        return {**base, **(human or {"stdout": "14G\t/vol/fob-vol6/mi25/yesildau\n"})}
    if command[0] == "du" and command[1:4] == ["-x", "-B1", "-s"]:
        return {**base, **(exact or {"stdout": "14687617024\t/vol/fob-vol6/mi25/yesildau\n"})}
    if command[0] == "df" and command[1] == "-h":
        return {**base, **(df_h or {})}
    if command[0] == "df" and command[1] == "-i":
        return {**base, **(df_i or {})}
    if command[0] == "readlink":
        return {**base, "stdout": (resolved if resolved is not None else root) + "\n"}
    if command[0] == "find":
        return {**base, **(large or {"stdout": ""})}
    return base


def test_storage_preflight_allows_human_du_timeout_when_exact_byte_passes_below_limit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = str(tmp_path / "new-root")
    calls: list[tuple[list[str], int]] = []

    def fake_run(command: list[str], *, timeout: int = 30) -> dict[str, object]:
        calls.append((command, timeout))
        human = {"timed_out": True, "stdout": "", "stderr": "", "returncode": None}
        exact = {"stdout": "14687617024\t/vol/fob-vol6/mi25/yesildau\n"}
        return _fake_storage_command(command, root, human=human, exact=exact, timeout=timeout)

    monkeypatch.setattr(metadata_executor_module, "_run_command", fake_run)
    result = metadata_executor_module.storage_preflight(root)

    assert result["complete"]
    assert result["home_usage_bytes"] == 14687617024
    assert result["checks"]["human_du"]["timed_out"]
    assert (result["checks"]["exact_byte_du"]["command"][1:4]) == ["-x", "-B1", "-s"]
    assert any(command[1] == "-xsh" and timeout == 30 for command, timeout in calls)
    assert any(command[1:4] == ["-x", "-B1", "-s"] and timeout == 120 for command, timeout in calls)


def test_storage_preflight_blocks_exact_byte_du_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = str(tmp_path / "new-root")

    def fake_run(command: list[str], *, timeout: int = 30) -> dict[str, object]:
        exact = {"timed_out": True, "returncode": None, "stdout": "", "stderr": ""}
        return _fake_storage_command(command, root, exact=exact, timeout=timeout)

    monkeypatch.setattr(metadata_executor_module, "_run_command", fake_run)
    result = metadata_executor_module.storage_preflight(root)

    assert not result["complete"]
    assert result["home_usage_bytes"] is None
    assert "exact-byte home-usage du timed out" in result["errors"]


def test_storage_preflight_blocks_exact_byte_du_parse_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = str(tmp_path / "new-root")

    def fake_run(command: list[str], *, timeout: int = 30) -> dict[str, object]:
        exact = {"stdout": "not-an-exact-byte-value\n"}
        return _fake_storage_command(command, root, exact=exact, timeout=timeout)

    monkeypatch.setattr(metadata_executor_module, "_run_command", fake_run)
    result = metadata_executor_module.storage_preflight(root)

    assert not result["complete"]
    assert result["home_usage_bytes"] is None
    assert "exact-byte home-usage du output could not be parsed" in result["errors"]


def test_storage_preflight_blocks_exact_byte_du_at_home_limit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = str(tmp_path / "new-root")

    def fake_run(command: list[str], *, timeout: int = 30) -> dict[str, object]:
        exact = {"stdout": f"{30 * 1024**3}\t/vol/fob-vol6/mi25/yesildau\n"}
        return _fake_storage_command(command, root, exact=exact, timeout=timeout)

    monkeypatch.setattr(metadata_executor_module, "_run_command", fake_run)
    result = metadata_executor_module.storage_preflight(root)

    assert not result["complete"]
    assert result["home_usage_bytes"] == 30 * 1024**3
    assert "HU home usage is at or above the 30 GiB stop rule" in result["errors"]


@pytest.mark.parametrize(
    "failure_kwargs, expected_error",
    [
        ({"df_h": {"returncode": 1}}, "storage command failed"),
        ({"df_i": {"returncode": 1}}, "storage command failed"),
        ({"resolved": "/vol/tmp2/yesildau/another-root"}, "resolved root does not equal frozen root"),
    ],
)
def test_storage_preflight_blocks_capacity_inode_or_path_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    failure_kwargs: dict[str, object],
    expected_error: str,
) -> None:
    root = str(tmp_path / "new-root")

    def fake_run(command: list[str], *, timeout: int = 30) -> dict[str, object]:
        return _fake_storage_command(command, root, timeout=timeout, **failure_kwargs)

    monkeypatch.setattr(metadata_executor_module, "_run_command", fake_run)
    result = metadata_executor_module.storage_preflight(root)

    assert not result["complete"]
    assert expected_error in result["errors"]


@pytest.mark.parametrize(
    "large_result, expected_status",
    [
        ({"timed_out": True, "returncode": None, "stdout": "", "stderr": ""}, "INCOMPLETE"),
        ({"returncode": 1, "stdout": "", "stderr": "permission denied\n"}, "BLOCKED"),
        ({"returncode": 0, "stdout": "not-a-manifest\n"}, "INCOMPLETE"),
    ],
)
def test_large_home_file_audit_fails_closed_on_timeout_failure_or_parse(
    monkeypatch: pytest.MonkeyPatch,
    large_result: dict[str, object],
    expected_status: str,
) -> None:
    def fake_run(command: list[str], *, timeout: int = 30) -> dict[str, object]:
        del timeout
        if command[0] == "find":
            return {"command": command, "stderr": "", **large_result}
        return {"command": command, "returncode": 0, "stdout": "", "stderr": "", "timed_out": False}

    monkeypatch.setattr(metadata_executor_module, "_run_command", fake_run)
    result = metadata_executor_module._large_home_file_audit()

    assert result["status"] == expected_status


def test_large_home_file_manifest_reconciliation_fails_closed_without_both_manifests() -> None:
    result = metadata_executor_module._reconcile_large_home_file_manifests(None, {"status": "PASS", "manifest": []})
    assert result["status"] == "INCOMPLETE"


def test_storage_preflight_blocks_before_any_source_request(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = str(tmp_path / "new-root")
    monkeypatch.setattr(
        metadata_executor_module,
        "storage_preflight",
        lambda root: {"root": root, "complete": False, "errors": ["exact-byte timeout"]},
    )
    monkeypatch.setattr(
        metadata_executor_module,
        "_execute_metadata_footer_wave_uncaught",
        lambda **kwargs: pytest.fail("source stage must not run after preflight failure"),
    )

    result = metadata_executor_module.execute_metadata_footer_wave(root=root)

    assert result["status"] == "BLOCKED"
    assert result["phase"] == "preflight"
    assert result["source_requests_started"] == 0


def test_storage_preflight_blocks_existing_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root_path = tmp_path / "existing-root"
    root_path.mkdir()
    root = str(root_path)

    def fake_run(command: list[str], *, timeout: int = 30) -> dict[str, object]:
        return _fake_storage_command(command, root, timeout=timeout)

    monkeypatch.setattr(metadata_executor_module, "_run_command", fake_run)
    result = metadata_executor_module.storage_preflight(root)

    assert not result["complete"]
    assert "new scratch root already exists" in result["errors"]


def test_metadata_executor_writer_failure_precedes_source_requests(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = str(tmp_path / "new-root")
    monkeypatch.setattr(metadata_executor_module, "storage_preflight", lambda root: {"root": root, "complete": True})
    monkeypatch.setattr(
        metadata_executor_module,
        "independent_writer_self_check",
        lambda: {"status": "BLOCKED", "reason": "independent_writer_parser_failure"},
    )
    monkeypatch.setattr(
        metadata_executor_module,
        "_execute_metadata_footer_wave_uncaught",
        lambda **kwargs: pytest.fail("source stage must not run after writer failure"),
    )

    result = metadata_executor_module.execute_metadata_footer_wave(root=root)

    assert result["status"] == "BLOCKED"
    assert result["phase"] == "independent_writer_self_check"
    assert result["source_requests_started"] == 0


def test_metadata_executor_invokes_post_run_audit_on_pass(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = str(tmp_path / "new-root")
    audit = {"root": root, "file_count": 0, "total_bytes": 0}
    monkeypatch.setattr(metadata_executor_module, "storage_preflight", lambda root: {"root": root, "complete": True})
    monkeypatch.setattr(metadata_executor_module, "independent_writer_self_check", lambda: {"status": "PASS"})
    monkeypatch.setattr(metadata_executor_module, "_execute_metadata_footer_wave_uncaught", lambda **kwargs: {"status": "PASS"})
    monkeypatch.setattr(metadata_executor_module, "post_run_storage_audit", lambda root, **kwargs: audit)

    result = metadata_executor_module.execute_metadata_footer_wave(root=root)

    assert result["post_run_storage_audit"] == audit


def test_metadata_executor_invokes_post_run_audit_on_source_block(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = str(tmp_path / "new-root")
    audit = {"root": root, "file_count": 0, "total_bytes": 0}
    monkeypatch.setattr(metadata_executor_module, "storage_preflight", lambda root: {"root": root, "complete": True})
    monkeypatch.setattr(metadata_executor_module, "independent_writer_self_check", lambda: {"status": "PASS"})
    monkeypatch.setattr(
        metadata_executor_module.BoundedClient,
        "_attempt",
        lambda self, **kwargs: AttemptResult(
            status=302,
            headers={"location": "https://example.test/target"},
            payload=b"",
            final_url=kwargs["url"],
            redirect_chain=[],
            error="http_302",
        ),
    )
    monkeypatch.setattr(metadata_executor_module, "post_run_storage_audit", lambda root, **kwargs: audit)

    result = metadata_executor_module.execute_metadata_footer_wave(root=root)

    assert result["status"] == "BLOCKED"
    assert result["phase"] == "source_request"
    assert result["failure_context"]["http_status"] == 302
    assert result["failure_context"]["location_sha256"] == hashlib.sha256(
        b"https://example.test/target"
    ).hexdigest()
    assert "location" not in result["failure_context"]
    assert result["post_run_storage_audit"] == audit


def test_metadata_footer_validator_rejects_every_final_integrity_attack_class() -> None:
    package, payloads, manifest_payload, audit_payload = _valid_metadata_footer_package()

    fabricated_rows = copy.deepcopy(package)
    fabricated_rows["shard_metadata"][0]["row_count"] += 1
    fabricated_rows["sampling_schedule"] = build_sampling_schedule(fabricated_rows["shard_metadata"])
    fabricated_rows["feasibility_projection"] = build_metadata_footer_feasibility_projection(
        fabricated_rows["shard_metadata"], fabricated_rows["request_ledger"], evidence_artifact_count=len(payloads)
    )
    assert not _validate_metadata_footer_fixture(
        fabricated_rows, dict(payloads), manifest_payload, audit_payload
    )["complete"]

    invalid_retry = copy.deepcopy(package)
    invalid_retry["request_ledger"][0]["attempt_ordinal"] = -999
    assert not _validate_metadata_footer_fixture(
        invalid_retry, dict(payloads), manifest_payload, audit_payload
    )["complete"]

    byte_mismatch = copy.deepcopy(package)
    byte_mismatch["request_ledger"][0]["response_transferred_bytes"] += 1
    assert not _validate_metadata_footer_fixture(
        byte_mismatch, dict(payloads), manifest_payload, audit_payload
    )["complete"]

    malformed_headers = copy.deepcopy(package)
    malformed_payloads = dict(payloads)
    head_name = malformed_headers["shard_metadata"][0]["object_metadata_evidence_artifact"]
    malformed_payloads[head_name] = canonical_json_bytes({"unrelated": "header"})
    assert not _validate_metadata_footer_fixture(
        malformed_headers, malformed_payloads, manifest_payload, audit_payload
    )["complete"]

    unlinked_manifest = copy.deepcopy(package)
    unrelated_manifest = b'{"unrelated":"artifact"}\n'
    unlinked_manifest["artifact_manifest_sha256"] = hashlib.sha256(unrelated_manifest).hexdigest()
    assert not _validate_metadata_footer_fixture(
        unlinked_manifest, dict(payloads), unrelated_manifest, audit_payload
    )["complete"]

    unbound_audit = copy.deepcopy(package)
    audit = dict(unbound_audit["metadata_footer_audit"])
    audit["artifact_count"] += 1
    unbound_audit["metadata_footer_audit_sha256"] = hashlib.sha256(canonical_json_bytes(audit)).hexdigest()
    assert not _validate_metadata_footer_fixture(
        unbound_audit, dict(payloads), manifest_payload, canonical_json_bytes(audit)
    )["complete"]
