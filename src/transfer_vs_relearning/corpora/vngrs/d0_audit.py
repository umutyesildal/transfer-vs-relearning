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
