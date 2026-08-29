"""Execution-disabled OSCAR Phase-2 validation and three-tokenizer accounting."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .d0_audit import D0Document, EXPECTED_MODELS, MODEL_ROLES, TokenizerAdapter
from .d0_bundle import write_d0_failure, write_d0_phase2_evidence
from .d0_review import read_jsonl_rows, review_packet_sha256, validate_review_decisions
from .materialization import SourceObjectV3
from .metadata import canonical_json_sha256
from .parquet_loader_v3 import load_verified_parquet_documents_v3


_PROBES = (
    "Türkçe dil uyarlaması için kısa ve açık bir deneme cümlesidir.",
    "İstanbul'da bilim, eğitim ve kültür üzerine çalışan araştırmacılar buluştu.",
)


def _quantiles(values: list[int]) -> dict[str, int]:
    if not values:
        raise ValueError("token-count quantiles require a non-empty population")
    ordered = sorted(values)
    return {
        label: ordered[round((len(ordered) - 1) * fraction)]
        for label, fraction in (
            ("p0", 0.0),
            ("p50", 0.50),
            ("p95", 0.95),
            ("p99", 0.99),
            ("p100", 1.0),
        )
    }


def tokenizer_compatibility(adapter: TokenizerAdapter) -> dict[str, Any]:
    """Validate one exact tokenizer without loading or inspecting model weights."""

    if adapter.role not in EXPECTED_MODELS:
        raise ValueError("unknown tokenizer role")
    if (adapter.model_id, adapter.revision) != EXPECTED_MODELS[adapter.role]:
        raise ValueError(f"{adapter.role}: tokenizer model/revision drift")
    tokenizer = getattr(adapter, "tokenizer", None)
    vocabulary_size = len(tokenizer) if tokenizer is not None and hasattr(tokenizer, "__len__") else None
    if not isinstance(vocabulary_size, int) or vocabulary_size <= 2:
        raise ValueError(f"{adapter.role}: tokenizer vocabulary is invalid")
    probe_counts = []
    for probe in _PROBES:
        first = adapter.encode(probe, add_special_tokens=False)
        second = adapter.encode(probe, add_special_tokens=False)
        if (
            not isinstance(first, Sequence)
            or isinstance(first, (str, bytes))
            or list(first) != list(second)
            or not first
            or any(not isinstance(token, int) or token < 0 for token in first)
        ):
            raise ValueError(f"{adapter.role}: Turkish probe encoding is empty or nondeterministic")
        probe_counts.append(len(first))
    return {
        "schema_version": 1,
        "status": "TOKENIZER_COMPATIBILITY_PASS",
        "role": adapter.role,
        "model_id": adapter.model_id,
        "revision": adapter.revision,
        "snapshot_manifest_sha256": adapter.manifest_sha256,
        "tokenizer_asset_manifest_sha256": adapter.asset_sha256,
        "vocabulary_size": vocabulary_size,
        "probe_count": len(_PROBES),
        "probe_token_counts": probe_counts,
        "add_special_tokens": False,
        "model_weight_access": False,
        "ready_to_train": False,
    }


def _account_split(
    rows: list[D0Document], adapter: TokenizerAdapter, *, split_name: str
) -> dict[str, Any]:
    counts: list[int] = []
    digest = hashlib.sha256()
    total_bytes = 0
    exception_count = 0
    zero_count = 0
    for row in sorted(rows, key=lambda value: value.stable_document_id):
        total_bytes += len(row.text.encode("utf-8"))
        try:
            encoded = adapter.encode(row.text, add_special_tokens=False)
            if not isinstance(encoded, Sequence) or isinstance(encoded, (str, bytes)):
                raise TypeError("tokenizer output is not an integer sequence")
            count = len(encoded)
        except Exception:
            exception_count += 1
            continue
        if count == 0:
            zero_count += 1
        counts.append(count)
        digest.update(f"{row.stable_document_id}\t{count}\n".encode("utf-8"))
    total_tokens = sum(counts)
    blocked = bool(exception_count or zero_count or len(counts) != len(rows))
    return {
        "schema_version": 1,
        "status": "BLOCKED" if blocked else "ACCOUNTING_COMPLETE",
        "role": adapter.role,
        "split": split_name,
        "model_id": adapter.model_id,
        "revision": adapter.revision,
        "snapshot_manifest_sha256": adapter.manifest_sha256,
        "tokenizer_asset_manifest_sha256": adapter.asset_sha256,
        "document_count": len(rows),
        "document_ids_sha256": canonical_json_sha256(
            sorted(row.stable_document_id for row in rows)
        ),
        "utf8_bytes": total_bytes,
        "token_count": total_tokens,
        "tokens_per_utf8_byte": total_tokens / total_bytes if total_bytes else None,
        "tokens_per_document": total_tokens / len(rows),
        "token_count_quantiles": _quantiles(counts) if counts else None,
        "zero_token_documents": zero_count,
        "exception_documents": exception_count,
        "token_count_pairs_sha256": digest.hexdigest(),
        "token_count_pair_hash_semantics": "sorted_stable_document_id_tab_decimal_count_lf",
        "add_special_tokens": False,
        "truncation": False,
        "padding": False,
        "token_ids_persisted": False,
        "corpus_text_persisted": False,
        "ready_to_train": False,
    }


def split_tokenizer_accounting(
    documents: Iterable[D0Document],
    *,
    train_ids: set[str],
    heldout_ids: set[str],
    tokenizers: Iterable[TokenizerAdapter] | Callable[[], Iterable[TokenizerAdapter]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, dict[str, Any]]]]:
    """Return compatibility and train/held-out counts for all three frozen roles."""

    rows = list(documents)
    adapters_list = list(tokenizers)
    adapters = {adapter.role: adapter for adapter in adapters_list}
    if len(adapters_list) != 3 or set(adapters) != set(MODEL_ROLES):
        raise ValueError("exactly OLMo, Qwen and SmolLM tokenizer adapters are required")
    by_id = {row.stable_document_id: row for row in rows}
    if len(by_id) != len(rows) or set(by_id) != train_ids | heldout_ids or train_ids & heldout_ids:
        raise ValueError("token-accounting population does not equal the frozen split")
    train = [by_id[value] for value in sorted(train_ids)]
    heldout = [by_id[value] for value in sorted(heldout_ids)]
    compatibility: dict[str, dict[str, Any]] = {}
    accounting: dict[str, dict[str, dict[str, Any]]] = {}
    for role in MODEL_ROLES:
        compatibility[role] = tokenizer_compatibility(adapters[role])
        accounting[role] = {
            "train": _account_split(train, adapters[role], split_name="train"),
            "heldout": _account_split(heldout, adapters[role], split_name="heldout"),
        }
    return compatibility, accounting


def run_oscar_phase2_evidence(
    source_root: str | Path,
    split_root: str | Path,
    coverage_root: str | Path,
    output_root: str | Path,
    objects: Iterable[SourceObjectV3],
    *,
    decisions: Iterable[Mapping[str, Any]],
    tokenizers: Iterable[TokenizerAdapter],
    expected_document_count: int = 354_482,
    expected_utf8_bytes: int = 1_553_923_133,
    execution_enabled: bool = False,
    document_loader: Callable[..., list[D0Document]] = load_verified_parquet_documents_v3,
) -> dict[str, Any]:
    """Revalidate frozen evidence and persist compact Phase-2 tokenizer accounting."""

    if not execution_enabled:
        raise ValueError("OSCAR Phase-2 execution is disabled")
    destination = Path(output_root)
    if destination.exists():
        raise ValueError("OSCAR Phase-2 output root must be fresh and absent")
    try:
        split_path = Path(split_root)
        coverage_path = Path(coverage_root)
        split_state = json.loads((split_path / "control/phase1_state.json").read_text(encoding="utf-8"))
        coverage_state = json.loads((coverage_path / "control/coverage_state.json").read_text(encoding="utf-8"))
        coverage_final = json.loads((coverage_path / "control/final_audit.json").read_text(encoding="utf-8"))
        inventory = json.loads(
            (coverage_path / "reports/quartile_population_inventory.json").read_text(encoding="utf-8")
        )
        if (
            split_state.get("status") != "AWAITING_HUMAN_REVIEW"
            or coverage_state.get("status") != "AWAITING_HUMAN_REVIEW"
            or coverage_final.get("coverage_validated") is not True
            or coverage_final.get("split_rewritten") is not False
        ):
            raise ValueError("Phase-2 predecessor state is incomplete")
        packet = read_jsonl_rows(coverage_path / "reports/human_review_packet.jsonl")
        if review_packet_sha256(packet) != coverage_state.get("review_packet_sha256"):
            raise ValueError("authoritative review packet drift")
        reviewed = validate_review_decisions(packet, decisions)
        verdicts = Counter(row["verdict"] for row in reviewed)
        if verdicts != {"usable": len(packet)}:
            raise ValueError("human review contains unresolved, unusable or unsafe evidence")

        train_ids = {
            row["stable_document_id"]
            for row in read_jsonl_rows(split_path / "splits/train_document_ids.jsonl")
        }
        heldout_ids = {
            row["stable_document_id"]
            for row in read_jsonl_rows(split_path / "splits/heldout_document_ids.jsonl")
        }
        split = {
            "schema_version": 1,
            "namespace": split_state["split_namespace"],
            "seed": split_state["split_seed"],
            "selection_rule": "ascending_sha256_namespace_seed_stable_document_id",
            "heldout_count": len(heldout_ids),
            "train_count": len(train_ids),
            "heldout_document_ids": sorted(heldout_ids),
            "train_document_ids": sorted(train_ids),
            "document_disjoint": not bool(train_ids & heldout_ids),
            "trwiki_training_rows": 0,
            "input_document_ids_sha256": split_state["document_ids_sha256"],
        }
        if canonical_json_sha256(split) != split_state.get("split_sha256"):
            raise ValueError("frozen split SHA drift")

        registry = tuple(objects)
        documents = document_loader(source_root, registry, execution_enabled=True)
        selected = [row for row in documents if row.corpus == "oscar"]
        selected_ids = {row.stable_document_id for row in selected}
        selected_bytes = sum(len(row.text.encode("utf-8")) for row in selected)
        strata = {row["stratum"]: row for row in inventory.get("strata", [])}
        if (
            len(selected) != expected_document_count
            or len(selected) != split_state.get("document_count")
            or canonical_json_sha256(sorted(selected_ids)) != split_state.get("document_ids_sha256")
            or selected_ids != train_ids | heldout_ids
            or selected_bytes != expected_utf8_bytes
            or inventory.get("nonempty_strata") != 1
            or strata.get("q0", {}).get("documents") != len(selected)
            or any(strata.get(f"q{index}", {}).get("documents") != 0 for index in (1, 2, 3))
        ):
            raise ValueError("OSCAR population, byte total, split union or coverage inventory drift")

        tokenizer_adapters = tokenizers() if callable(tokenizers) else tokenizers
        compatibility, accounting = split_tokenizer_accounting(
            selected,
            train_ids=train_ids,
            heldout_ids=heldout_ids,
            tokenizers=tokenizer_adapters,
        )
        if any(
            report["status"] != "ACCOUNTING_COMPLETE"
            for role in accounting.values()
            for report in role.values()
        ):
            raise ValueError("one or more tokenizer accounting reports blocked Phase 2")
        population = {
            "schema_version": 1,
            "status": "POPULATION_SPLIT_VALIDATION_PASS",
            "document_count": len(selected),
            "utf8_bytes": selected_bytes,
            "document_ids_sha256": split_state["document_ids_sha256"],
            "split_sha256": split_state["split_sha256"],
            "train_documents": len(train_ids),
            "heldout_documents": len(heldout_ids),
            "overlap_documents": 0,
            "trwiki_training_rows": 0,
            "split_rewritten": False,
            "ready_to_train": False,
        }
        review = {
            "schema_version": 1,
            "status": "HUMAN_REVIEW_PASS",
            "review_packet_sha256": coverage_state["review_packet_sha256"],
            "reviewed_documents": len(reviewed),
            "verdicts": dict(sorted(verdicts.items())),
            "unique_reviewers": len({row["reviewer"] for row in reviewed}),
            "decisions_persisted_in_bundle": False,
            "ready_to_train": False,
        }
        state = {
            "schema_version": 1,
            "status": "D0_EVIDENCE_COMPLETE",
            "source_root": str(Path(source_root)),
            "source_object_count": len(registry),
            "split_root": str(split_path),
            "coverage_root": str(coverage_path),
            "document_count": len(selected),
            "split_sha256": split_state["split_sha256"],
            "review_packet_sha256": coverage_state["review_packet_sha256"],
            "human_review_status": "HUMAN_REVIEW_PASS",
            "tokenizer_roles": list(MODEL_ROLES),
            "tokenizer_accounting_complete": True,
            "model_weight_access": False,
            "tokenized_corpus_persisted": False,
            "training_opened": False,
            "m2_training_contract_frozen": False,
            "ready_to_train": False,
        }
        final = write_d0_phase2_evidence(
            destination,
            state=state,
            population=population,
            review=review,
            compatibility=compatibility,
            accounting=accounting,
        )
        return {**state, "population": population, "human_review": review, "compatibility": compatibility, "accounting": accounting, "final_audit": final}
    except Exception as exc:
        write_d0_failure(destination, phase="oscar_phase2_evidence", error=exc)
        raise
