"""Deterministic, local-only audit/split/token accounting for vngrs M2 D0."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol, Sequence

from .metadata import FROZEN_SELECTED_SHARD_PATHS, canonical_json_sha256
from .sampling import largest_remainder_allocation


SPLIT_NAMESPACE = "vngrs_primary_in_domain_heldout_v2"
SPLIT_SEED = 42
HELDOUT_DOCUMENTS = 10_000
HUMAN_REVIEW_DOCUMENTS = 64
MODEL_ROLES = ("olmo", "qwen", "smollm")
EXPECTED_MODELS = {
    "olmo": ("allenai/OLMo-2-0425-1B", "a1847dff35000b4271fa70afc5db10fd29fedbdf"),
    "qwen": ("Qwen/Qwen2.5-1.5B", "8faed761d45a263340a0528343f099c05c9a4323"),
    "smollm": ("HuggingFaceTB/SmolLM2-1.7B", "effd688a12921b4cc83e3312b6feb579f70f9c71"),
}

_REGEX_GROUPS = {
    "invalid_encoding": re.compile("\ufffd"),
    "empty_or_very_short": re.compile(r"^\s*.{0,19}\s*$", re.DOTALL),
    "boilerplate": re.compile(r"\b(?:çerez|cookie|gizlilik politikası|tüm hakları saklıdır)\b", re.I),
    "seo_or_betting": re.compile(r"\b(?:seo|bahis|casino|casino bonus|canlı bahis)\b", re.I),
    "legal_or_jurisdiction": re.compile(r"\b(?:mahkeme|yargı yetkisi|uygulanacak hukuk|jurisdiction)\b", re.I),
}


class TokenizerAdapter(Protocol):
    role: str
    model_id: str
    revision: str
    manifest_sha256: str
    asset_sha256: str

    def encode(self, text: str, *, add_special_tokens: bool = False) -> Sequence[int]: ...


@dataclass(frozen=True)
class D0Document:
    stable_document_id: str
    shard_path: str
    corpus: str
    text: str


@dataclass(frozen=True)
class SyntheticFactSurface:
    subject_id: str
    subject: str
    fact_id: str
    relation: str
    answer: str


def _documents(rows: Iterable[D0Document]) -> list[D0Document]:
    documents = list(rows)
    ids = [row.stable_document_id for row in documents]
    if not documents or len(ids) != len(set(ids)):
        raise ValueError("documents must be non-empty with unique stable IDs")
    allowed = set(FROZEN_SELECTED_SHARD_PATHS)
    for row in documents:
        if not row.stable_document_id or row.shard_path not in allowed:
            raise ValueError("document identity or frozen shard binding is invalid")
        if not isinstance(row.text, str) or not str(row.corpus).strip():
            raise ValueError("document text/corpus is invalid")
    return documents


def _split_rank(document_id: str, *, namespace: str = SPLIT_NAMESPACE, seed: int = SPLIT_SEED) -> str:
    return hashlib.sha256(f"{namespace}|{seed}|{document_id}".encode("utf-8")).hexdigest()


def exact_heldout_split(
    rows: Iterable[D0Document], *, heldout_documents: int = HELDOUT_DOCUMENTS
) -> dict[str, Any]:
    documents = _documents(rows)
    if heldout_documents <= 0 or len(documents) <= heldout_documents:
        raise ValueError("training reservoir must remain non-empty after exact held-out selection")
    ordered = sorted(documents, key=lambda row: (_split_rank(row.stable_document_id), row.stable_document_id))
    heldout_ids = sorted(row.stable_document_id for row in ordered[:heldout_documents])
    train_ids = sorted(row.stable_document_id for row in ordered[heldout_documents:])
    if set(heldout_ids) & set(train_ids):
        raise AssertionError("train/held-out document IDs overlap")
    return {
        "schema_version": 1,
        "namespace": SPLIT_NAMESPACE,
        "seed": SPLIT_SEED,
        "selection_rule": "ascending_sha256_namespace_seed_stable_document_id",
        "heldout_count": len(heldout_ids),
        "train_count": len(train_ids),
        "heldout_document_ids": heldout_ids,
        "train_document_ids": train_ids,
        "document_disjoint": True,
        "trwiki_training_rows": 0,
        "input_document_ids_sha256": canonical_json_sha256(sorted(row.stable_document_id for row in documents)),
    }


def _quartile(path: str) -> int:
    return FROZEN_SELECTED_SHARD_PATHS.index(path) // 8


def human_review_sample(
    rows: Iterable[D0Document], *, sample_size: int = HUMAN_REVIEW_DOCUMENTS
) -> list[dict[str, Any]]:
    documents = _documents(rows)
    strata: dict[str, list[D0Document]] = defaultdict(list)
    for row in documents:
        strata[f"{row.corpus}|q{_quartile(row.shard_path)}"].append(row)
    allocation = largest_remainder_allocation(
        {key: len(value) for key, value in strata.items()}, sample_size
    )
    selected: list[dict[str, Any]] = []
    for key in sorted(strata):
        candidates = sorted(
            strata[key],
            key=lambda row: (
                hashlib.sha256(f"vngrs_d0_human_review_v1|42|{row.stable_document_id}".encode()).hexdigest(),
                row.stable_document_id,
            ),
        )
        for row in candidates[: allocation[key]]:
            selected.append(
                {
                    "schema_version": 1,
                    "stable_document_id": row.stable_document_id,
                    "corpus": row.corpus,
                    "shard_quartile": _quartile(row.shard_path),
                    "selection_stratum": key,
                    "review_status": "pending_human_review",
                }
            )
    selected.sort(key=lambda row: row["stable_document_id"])
    if len(selected) != sample_size:
        raise AssertionError("human-review sample cardinality drift")
    return selected


def human_review_stratum_inventory(rows: Iterable[D0Document]) -> dict[str, Any]:
    """Describe the exact corpus-by-selected-shard-quartile review population."""

    documents = _documents(rows)
    counts: dict[str, dict[str, int]] = {
        f"q{quartile}": {"documents": 0, "utf8_bytes": 0} for quartile in range(4)
    }
    for row in documents:
        key = f"q{_quartile(row.shard_path)}"
        counts[key]["documents"] += 1
        counts[key]["utf8_bytes"] += len(row.text.encode("utf-8"))
    return {
        "schema_version": 1,
        "status": "STRATUM_INVENTORY_COMPLETE",
        "document_count": len(documents),
        "strata": [{"stratum": key, **counts[key]} for key in sorted(counts)],
        "nonempty_strata": sum(counts[key]["documents"] > 0 for key in counts),
        "ready_to_train": False,
    }


def human_review_sample_with_stratum_floor(
    rows: Iterable[D0Document], *, sample_size: int = HUMAN_REVIEW_DOCUMENTS
) -> list[dict[str, Any]]:
    """Guarantee one row per non-empty quartile, then allocate remaining slots proportionally."""

    documents = _documents(rows)
    strata: dict[str, list[D0Document]] = defaultdict(list)
    for row in documents:
        strata[f"{row.corpus}|q{_quartile(row.shard_path)}"].append(row)
    if sample_size < len(strata):
        raise ValueError("review sample is smaller than the non-empty stratum floor")
    allocation = {key: 1 for key in strata}
    remaining = sample_size - len(strata)
    residual = {key: len(value) - 1 for key, value in strata.items() if len(value) > 1}
    if remaining:
        if not residual or remaining > sum(residual.values()):
            raise ValueError("review sample exceeds the population after stratum floors")
        extra = largest_remainder_allocation(residual, remaining)
        for key, value in extra.items():
            allocation[key] += value
    selected: list[dict[str, Any]] = []
    for key in sorted(strata):
        candidates = sorted(
            strata[key],
            key=lambda row: (
                hashlib.sha256(
                    f"vngrs_d0_human_review_coverage_floor_v1|42|{row.stable_document_id}".encode()
                ).hexdigest(),
                row.stable_document_id,
            ),
        )
        for row in candidates[: allocation[key]]:
            selected.append(
                {
                    "schema_version": 1,
                    "stable_document_id": row.stable_document_id,
                    "corpus": row.corpus,
                    "shard_quartile": _quartile(row.shard_path),
                    "selection_stratum": key,
                    "stratum_population_documents": len(strata[key]),
                    "stratum_allocated_documents": allocation[key],
                    "allocation_rule": "one_per_nonempty_stratum_then_largest_remainder",
                    "review_status": "pending_human_review",
                }
            )
    selected.sort(key=lambda row: row["stable_document_id"])
    if len(selected) != sample_size or len({row["stable_document_id"] for row in selected}) != sample_size:
        raise AssertionError("coverage-floor review sample cardinality drift")
    if {row["selection_stratum"] for row in selected} != set(strata):
        raise AssertionError("coverage-floor review sample omitted a non-empty stratum")
    return selected


def lightweight_audit(
    rows: Iterable[D0Document], *, synthetic_surfaces: Mapping[str, str]
) -> dict[str, Any]:
    documents = _documents(rows)
    if not synthetic_surfaces or any(not key or not value for key, value in synthetic_surfaces.items()):
        raise ValueError("synthetic subject/object/alias registry must be non-empty and exact")
    composition: dict[str, dict[str, int]] = defaultdict(lambda: {"documents": 0, "utf8_bytes": 0})
    regex_document_counts: Counter[str] = Counter()
    exact_hits: list[dict[str, str]] = []
    normalized_hits: list[dict[str, str]] = []
    normalized_hashes: Counter[str] = Counter()
    total_bytes = 0
    for row in documents:
        raw_bytes = len(row.text.encode("utf-8"))
        total_bytes += raw_bytes
        label = row.corpus.casefold()
        bucket = "oscar" if "oscar" in label else "mc4" if "mc4" in label else "other"
        composition[bucket]["documents"] += 1
        composition[bucket]["utf8_bytes"] += raw_bytes
        for group, pattern in _REGEX_GROUPS.items():
            if pattern.search(row.text):
                regex_document_counts[group] += 1
        normalized = unicodedata.normalize("NFC", row.text).casefold()
        normalized_hashes[hashlib.sha256(normalized.encode("utf-8")).hexdigest()] += 1
        for pattern_id, surface in sorted(synthetic_surfaces.items()):
            if surface in row.text:
                exact_hits.append({"stable_document_id": row.stable_document_id, "pattern_id": pattern_id})
            if unicodedata.normalize("NFC", surface).casefold() in normalized:
                normalized_hits.append({"stable_document_id": row.stable_document_id, "pattern_id": pattern_id})
    duplicate_groups = sum(count > 1 for count in normalized_hashes.values())
    duplicate_documents = sum(count for count in normalized_hashes.values() if count > 1)
    return {
        "schema_version": 1,
        "status": "BLOCKED" if exact_hits or normalized_hits or regex_document_counts["invalid_encoding"] else "AUDIT_COMPLETE",
        "document_count": len(documents),
        "utf8_bytes": total_bytes,
        "composition": {
            key: {
                **composition[key],
                "document_fraction": composition[key]["documents"] / len(documents),
                "utf8_byte_fraction": composition[key]["utf8_bytes"] / total_bytes if total_bytes else None,
            }
            for key in ("oscar", "mc4", "other")
        },
        "regex_document_counts": {key: regex_document_counts[key] for key in _REGEX_GROUPS},
        "synthetic_contamination": {
            "pattern_count": len(synthetic_surfaces),
            "exact_hits": exact_hits,
            "unicode_normalized_hits": normalized_hits,
        },
        "normalized_text_duplicate_groups": duplicate_groups,
        "normalized_text_duplicate_documents": duplicate_documents,
    }


def fact_pair_contamination_audit(
    rows: Iterable[D0Document],
    *,
    synthetic_facts: Iterable[SyntheticFactSurface],
    predecessor_atom_audit: Mapping[str, Any],
    predecessor_atom_audit_sha256: str,
    example_limit: int = 256,
) -> dict[str, Any]:
    """Gate only paired subject+answer co-occurrence; keep atom hits diagnostic.

    Relation V2 answers include ordinary cities, professions and industries. Their appearance
    without the corresponding synthetic subject is therefore not evidence of factual leakage.
    This audit retains each frozen fact's relation binding and blocks only when a document
    contains both that fact's subject and answer (exactly or after NFC+casefold normalization).
    """

    documents = _documents(rows)
    facts = tuple(synthetic_facts)
    if not facts or not 1 <= example_limit <= 1_000:
        raise ValueError("synthetic fact registry and bounded example limit are required")
    if not re.fullmatch(r"[0-9a-f]{64}", predecessor_atom_audit_sha256):
        raise ValueError("predecessor atom-audit SHA-256 is invalid")
    predecessor_contamination = predecessor_atom_audit.get("synthetic_contamination") or {}
    for key in ("pattern_count", "exact_hit_count", "unicode_normalized_hit_count"):
        if not isinstance(predecessor_contamination.get(key), int):
            raise ValueError("predecessor atom audit is incomplete")

    seen_fact_ids: set[str] = set()
    subject_identity: dict[str, str] = {}
    by_subject: dict[str, list[SyntheticFactSurface]] = defaultdict(list)
    relations: set[str] = set()
    for fact in facts:
        values = (fact.subject_id, fact.subject, fact.fact_id, fact.relation, fact.answer)
        if not all(isinstance(value, str) and value for value in values):
            raise ValueError("synthetic fact identity is incomplete")
        if fact.fact_id in seen_fact_ids:
            raise ValueError("synthetic fact identity is duplicated")
        if fact.subject_id in subject_identity and subject_identity[fact.subject_id] != fact.subject:
            raise ValueError("synthetic subject identity is ambiguous")
        seen_fact_ids.add(fact.fact_id)
        subject_identity[fact.subject_id] = fact.subject
        by_subject[fact.subject_id].append(fact)
        relations.add(fact.relation)

    normalized_subjects = {
        subject_id: unicodedata.normalize("NFC", subject).casefold()
        for subject_id, subject in subject_identity.items()
    }
    normalized_answers = {
        fact.fact_id: unicodedata.normalize("NFC", fact.answer).casefold() for fact in facts
    }
    subject_exact_pairs = 0
    subject_normalized_pairs = 0
    subject_exact_documents: set[str] = set()
    subject_normalized_documents: set[str] = set()
    exact_pair_count = 0
    normalized_pair_count = 0
    exact_pair_documents: set[str] = set()
    normalized_pair_documents: set[str] = set()
    exact_fact_ids: set[str] = set()
    normalized_fact_ids: set[str] = set()
    exact_examples: list[dict[str, str]] = []
    normalized_examples: list[dict[str, str]] = []
    exact_by_relation: Counter[str] = Counter()
    normalized_by_relation: Counter[str] = Counter()
    invalid_encoding_documents = 0

    for row in documents:
        normalized_text = unicodedata.normalize("NFC", row.text).casefold()
        if "\ufffd" in row.text:
            invalid_encoding_documents += 1
        for subject_id in sorted(by_subject):
            subject = subject_identity[subject_id]
            exact_subject = subject in row.text
            normalized_subject = normalized_subjects[subject_id] in normalized_text
            if exact_subject:
                subject_exact_pairs += 1
                subject_exact_documents.add(row.stable_document_id)
            if normalized_subject:
                subject_normalized_pairs += 1
                subject_normalized_documents.add(row.stable_document_id)
            if not normalized_subject:
                continue
            for fact in by_subject[subject_id]:
                if exact_subject and fact.answer in row.text:
                    exact_pair_count += 1
                    exact_pair_documents.add(row.stable_document_id)
                    exact_fact_ids.add(fact.fact_id)
                    exact_by_relation[fact.relation] += 1
                    if len(exact_examples) < example_limit:
                        exact_examples.append(
                            {
                                "stable_document_id": row.stable_document_id,
                                "subject_id": fact.subject_id,
                                "fact_id": fact.fact_id,
                                "relation": fact.relation,
                            }
                        )
                if normalized_answers[fact.fact_id] in normalized_text:
                    normalized_pair_count += 1
                    normalized_pair_documents.add(row.stable_document_id)
                    normalized_fact_ids.add(fact.fact_id)
                    normalized_by_relation[fact.relation] += 1
                    if len(normalized_examples) < example_limit:
                        normalized_examples.append(
                            {
                                "stable_document_id": row.stable_document_id,
                                "subject_id": fact.subject_id,
                                "fact_id": fact.fact_id,
                                "relation": fact.relation,
                            }
                        )

    blocked = bool(exact_pair_count or normalized_pair_count or invalid_encoding_documents)
    return {
        "schema_version": 1,
        "status": "BLOCKED" if blocked else "AUDIT_COMPLETE",
        "document_count": len(documents),
        "gate_semantics": {
            "blocking": [
                "exact_paired_subject_answer_cooccurrence",
                "nfc_casefold_paired_subject_answer_cooccurrence",
                "invalid_encoding_u_fffd",
            ],
            "diagnostic_non_blocking": ["subject_only_hits", "object_only_atom_hits"],
            "relation_phrase_required": False,
        },
        "registry": {
            "fact_count": len(facts),
            "subject_count": len(subject_identity),
            "relations": sorted(relations),
        },
        "predecessor_atom_audit": {
            "sha256": predecessor_atom_audit_sha256,
            "status": predecessor_atom_audit.get("status"),
            "pattern_count": predecessor_contamination["pattern_count"],
            "exact_hit_count": predecessor_contamination["exact_hit_count"],
            "unicode_normalized_hit_count": predecessor_contamination[
                "unicode_normalized_hit_count"
            ],
            "role": "diagnostic_non_blocking_under_fact_pair_gate",
        },
        "subject_only_diagnostic": {
            "exact_document_surface_pairs": subject_exact_pairs,
            "exact_unique_documents": len(subject_exact_documents),
            "unicode_normalized_document_surface_pairs": subject_normalized_pairs,
            "unicode_normalized_unique_documents": len(subject_normalized_documents),
        },
        "paired_contamination": {
            "exact_document_fact_pairs": exact_pair_count,
            "exact_unique_documents": len(exact_pair_documents),
            "exact_unique_facts": len(exact_fact_ids),
            "unicode_normalized_document_fact_pairs": normalized_pair_count,
            "unicode_normalized_unique_documents": len(normalized_pair_documents),
            "unicode_normalized_unique_facts": len(normalized_fact_ids),
            "exact_by_relation": {key: exact_by_relation[key] for key in sorted(relations)},
            "unicode_normalized_by_relation": {
                key: normalized_by_relation[key] for key in sorted(relations)
            },
            "exact_examples": exact_examples,
            "unicode_normalized_examples": normalized_examples,
            "example_limit_per_kind": example_limit,
            "examples_truncated": (
                exact_pair_count > example_limit or normalized_pair_count > example_limit
            ),
        },
        "invalid_encoding_documents": invalid_encoding_documents,
        "ready_to_train": False,
    }


def _quantiles(values: list[int]) -> dict[str, int]:
    ordered = sorted(values)
    return {
        label: ordered[round((len(ordered) - 1) * fraction)]
        for label, fraction in (("p0", 0.0), ("p25", 0.25), ("p50", 0.5), ("p75", 0.75), ("p100", 1.0))
    }


def tokenizer_accounting(
    rows: Iterable[D0Document], tokenizers: Iterable[TokenizerAdapter]
) -> dict[str, dict[str, Any]]:
    documents = sorted(_documents(rows), key=lambda row: row.stable_document_id)
    adapter_rows = list(tokenizers)
    adapters = {adapter.role: adapter for adapter in adapter_rows}
    if len(adapter_rows) != len(MODEL_ROLES) or tuple(sorted(adapters)) != tuple(sorted(MODEL_ROLES)):
        raise ValueError("exactly OLMo, Qwen and SmolLM tokenizer adapters are required")
    id_hash = canonical_json_sha256([row.stable_document_id for row in documents])
    raw_bytes = sum(len(row.text.encode("utf-8")) for row in documents)
    reports: dict[str, dict[str, Any]] = {}
    for role in MODEL_ROLES:
        adapter = adapters[role]
        if (adapter.model_id, adapter.revision) != EXPECTED_MODELS[role]:
            raise ValueError(f"{role}: tokenizer model/revision drift")
        if not re.fullmatch(r"[0-9a-f]{64}", adapter.manifest_sha256) or not re.fullmatch(
            r"[0-9a-f]{64}", adapter.asset_sha256
        ):
            raise ValueError(f"{role}: tokenizer manifest/asset hash unresolved")
        counts: list[int] = []
        exception_count = 0
        for row in documents:
            try:
                encoded = adapter.encode(row.text, add_special_tokens=False)
            except Exception:
                exception_count += 1
                continue
            if not isinstance(encoded, Sequence) or isinstance(encoded, (str, bytes)):
                exception_count += 1
                continue
            counts.append(len(encoded))
        zero_count = sum(count == 0 for count in counts)
        total_tokens = sum(counts)
        reports[role] = {
            "schema_version": 1,
            "status": "BLOCKED" if zero_count or exception_count else "ACCOUNTING_COMPLETE",
            "role": role,
            "model_id": adapter.model_id,
            "revision": adapter.revision,
            "tokenizer_manifest_sha256": adapter.manifest_sha256,
            "tokenizer_asset_sha256": adapter.asset_sha256,
            "document_ids_sha256": id_hash,
            "document_count": len(documents),
            "utf8_bytes": raw_bytes,
            "token_count": total_tokens,
            "tokens_per_byte": total_tokens / raw_bytes if raw_bytes else None,
            "tokens_per_document": total_tokens / len(documents),
            "token_count_quantiles": _quantiles(counts) if counts else None,
            "zero_token_documents": zero_count,
            "exception_documents": exception_count,
            "packing_policy_applied": False,
            "cross_model_token_equality_gate": False,
        }
    if len({report["document_ids_sha256"] for report in reports.values()}) != 1:
        raise AssertionError("tokenizer reports do not share the same raw document IDs")
    return reports
