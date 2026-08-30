"""Memory-bounded writers for exact matched M2-A/M2-B token blocks."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _eos_token_id(tokenizer: Any) -> int:
    """Resolve EOS from a tokenizer or the reviewed FrozenTokenizerAdapter shape."""

    value = getattr(tokenizer, "eos_token_id", None)
    if value is None:
        value = getattr(getattr(tokenizer, "tokenizer", None), "eos_token_id", None)
    if not isinstance(value, int) or value < 0:
        raise ValueError("Tokenizer must define a non-negative integer eos_token_id")
    return value


def build_fixed_replacement_schedule(
    factual_rows: list[dict[str, Any]],
    tokenizer: Any,
    *,
    block_size: int,
    total_blocks: int,
    replacement_block_count: int,
) -> tuple[dict[int, tuple[list[int], list[str]]], dict[str, Any]]:
    """Build the exact fixed-dose schedule without copying the generic block family."""

    if block_size <= 0 or total_blocks <= 0 or replacement_block_count <= 0:
        raise ValueError("Block and replacement counts must be positive")
    if replacement_block_count >= total_blocks:
        raise ValueError("Factual replacement must leave at least one generic-only block")
    eos_token_id = _eos_token_id(tokenizer)
    fact_ids = [str(row.get("fact_id", "")) for row in factual_rows]
    if not fact_ids or any(not value for value in fact_ids) or len(fact_ids) != len(set(fact_ids)):
        raise ValueError("Factual registry must contain unique non-empty fact IDs")
    if {str(row.get("branch_group")) for row in factual_rows} != {"B"}:
        raise ValueError("Factual registry must contain Branch B only")

    encoded: list[tuple[str, list[int]]] = []
    relation_by_fact: dict[str, str] = {}
    for row in sorted(factual_rows, key=lambda value: str(value["fact_id"])):
        fact_id = str(row["fact_id"])
        text = str(row.get("text", "")).strip()
        if not text:
            raise ValueError(f"Factual row {fact_id} has no text")
        tokens = list(tokenizer.encode(text, add_special_tokens=False))
        tokens.append(eos_token_id)
        if len(tokens) > block_size:
            raise ValueError(f"Factual row {fact_id} exceeds one block")
        encoded.append((fact_id, tokens))
        relation_by_fact[fact_id] = str(row.get("relation", "unknown"))

    packed: list[tuple[list[int], list[str]]] = []
    exposures: Counter[str] = Counter({fact_id: 0 for fact_id, _ in encoded})
    cursor = 0
    for _ in range(replacement_block_count):
        tokens: list[int] = []
        packed_ids: list[str] = []
        while True:
            fact_id, fact_tokens = encoded[cursor % len(encoded)]
            if tokens and len(tokens) + len(fact_tokens) > block_size:
                break
            tokens.extend(fact_tokens)
            packed_ids.append(fact_id)
            exposures[fact_id] += 1
            cursor += 1
            if len(tokens) == block_size:
                break
        packed.append((tokens, packed_ids))

    indices = [
        ((2 * index + 1) * total_blocks) // (2 * replacement_block_count)
        for index in range(replacement_block_count)
    ]
    if len(indices) != len(set(indices)):
        raise AssertionError("Deterministic replacement indices are not unique")
    schedule = dict(zip(indices, packed, strict=True))
    relation_exposures: Counter[str] = Counter()
    for fact_id, count in exposures.items():
        relation_exposures[relation_by_fact[fact_id]] += count
    exposure_values = list(exposures.values())
    relation_values = list(relation_exposures.values())
    factual_tokens = sum(len(tokens) for tokens, _ in packed)
    replacements = [
        {
            "block_index": index,
            "factual_tokens": len(schedule[index][0]),
            "generic_tail_tokens": block_size - len(schedule[index][0]),
            "fact_ids": schedule[index][1],
        }
        for index in indices
    ]
    audit = {
        "schema_version": 1,
        "block_size": block_size,
        "total_blocks_per_arm": total_blocks,
        "total_tokens_per_arm": total_blocks * block_size,
        "unique_branch_b_facts": len(factual_rows),
        "scheduled_fact_exposures": sum(exposure_values),
        "fact_exposure_min": min(exposure_values),
        "fact_exposure_max": max(exposure_values),
        "fact_exposure_balance_max_minus_min": max(exposure_values) - min(exposure_values),
        "fact_exposures": dict(sorted(exposures.items())),
        "relation_exposures": dict(sorted(relation_exposures.items())),
        "relation_exposure_balance_max_minus_min": max(relation_values) - min(relation_values),
        "factual_tokens": factual_tokens,
        "factual_token_share": factual_tokens / (total_blocks * block_size),
        "replacement_block_count": replacement_block_count,
        "replacement_blocks": replacements,
        "m2_a_m2_b_block_count_equal": True,
        "m2_a_m2_b_token_budget_equal": True,
        "branch_a_fact_exposures": 0,
        "extra_tokens_over_m2_a": 0,
    }
    if audit["fact_exposure_balance_max_minus_min"] > 1:
        raise AssertionError("Complete-cycle factual scheduling must differ by at most one exposure")
    if audit["relation_exposure_balance_max_minus_min"] > 1:
        raise AssertionError("Relation exposure totals must differ by at most one exposure")
    return schedule, audit


def _row(block_index: int, arm: str, block: list[int]) -> dict[str, Any]:
    return {
        "block_index": block_index,
        "arm": arm,
        "input_ids": block,
        "attention_mask": [1] * len(block),
    }


def stream_matched_train_files(
    rows: Iterable[Mapping[str, Any]],
    tokenizer: Any,
    factual_rows: list[dict[str, Any]],
    *,
    m2_a_path: Path,
    m2_b_path: Path,
    block_size: int,
    total_blocks: int,
    replacement_block_count: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Write both sibling arms atomically while retaining at most one document token buffer."""

    schedule, matching = build_fixed_replacement_schedule(
        factual_rows,
        tokenizer,
        block_size=block_size,
        total_blocks=total_blocks,
        replacement_block_count=replacement_block_count,
    )
    eos_token_id = _eos_token_id(tokenizer)
    m2_a_path.parent.mkdir(parents=True, exist_ok=True)
    m2_b_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_a = m2_a_path.with_suffix(m2_a_path.suffix + ".tmp")
    temporary_b = m2_b_path.with_suffix(m2_b_path.suffix + ".tmp")
    buffer: list[int] = []
    consumed_ids: list[str] = []
    block_index = 0
    observed_tokens = 0
    with temporary_a.open("w", encoding="utf-8") as handle_a, temporary_b.open(
        "w", encoding="utf-8"
    ) as handle_b:
        for source in rows:
            text = str(source.get("text", "")).strip()
            stable_id = str(source.get("stable_document_id", ""))
            if not text or not stable_id:
                raise ValueError("Generic Turkish row requires non-empty text and stable ID")
            consumed_ids.append(stable_id)
            buffer.extend(tokenizer.encode(text, add_special_tokens=False))
            buffer.append(eos_token_id)
            while len(buffer) >= block_size and block_index < total_blocks:
                generic = buffer[:block_size]
                del buffer[:block_size]
                replacement = schedule.get(block_index)
                factual = (
                    replacement[0] + generic[len(replacement[0]) :]
                    if replacement is not None
                    else generic
                )
                handle_a.write(
                    json.dumps(
                        _row(block_index, "M2-A", generic),
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )
                handle_b.write(
                    json.dumps(
                        _row(block_index, "M2-B", factual),
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )
                block_index += 1
            if block_index == total_blocks:
                observed_tokens = total_blocks * block_size + len(buffer)
                break
    if block_index != total_blocks:
        raise ValueError(
            f"Generic Turkish source produced {block_index} blocks; {total_blocks} required"
        )
    os.replace(temporary_a, m2_a_path)
    os.replace(temporary_b, m2_b_path)
    prefix = {
        "schema_version": 1,
        "block_size": block_size,
        "total_blocks": total_blocks,
        "required_tokens": total_blocks * block_size,
        "source_tokens_observed_through_last_document": observed_tokens,
        "discarded_tail_tokens": observed_tokens - total_blocks * block_size,
        "consumed_documents": len(consumed_ids),
        "consumed_document_ids_sha256": hashlib.sha256(_json_bytes(consumed_ids)).hexdigest(),
        "corpus_cycling": False,
        "streaming_writer": True,
    }
    return prefix, matching


def stream_validation_file(
    rows: Iterable[Mapping[str, Any]],
    tokenizer: Any,
    *,
    path: Path,
    block_size: int,
    total_blocks: int,
) -> dict[str, Any]:
    """Write a shared validation stream atomically with bounded token memory."""

    eos_token_id = _eos_token_id(tokenizer)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    buffer: list[int] = []
    consumed_ids: list[str] = []
    block_index = 0
    observed_tokens = 0
    with temporary.open("w", encoding="utf-8") as handle:
        for source in rows:
            text = str(source.get("text", "")).strip()
            stable_id = str(source.get("stable_document_id", ""))
            if not text or not stable_id:
                raise ValueError("Validation row requires non-empty text and stable ID")
            consumed_ids.append(stable_id)
            buffer.extend(tokenizer.encode(text, add_special_tokens=False))
            buffer.append(eos_token_id)
            while len(buffer) >= block_size and block_index < total_blocks:
                block = buffer[:block_size]
                del buffer[:block_size]
                handle.write(
                    json.dumps(
                        _row(block_index, "shared_validation", block),
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )
                block_index += 1
            if block_index == total_blocks:
                observed_tokens = total_blocks * block_size + len(buffer)
                break
    if block_index != total_blocks:
        raise ValueError(f"Validation source produced {block_index} blocks; {total_blocks} required")
    os.replace(temporary, path)
    return {
        "schema_version": 1,
        "block_size": block_size,
        "total_blocks": total_blocks,
        "required_tokens": total_blocks * block_size,
        "source_tokens_observed_through_last_document": observed_tokens,
        "discarded_tail_tokens": observed_tokens - total_blocks * block_size,
        "consumed_documents": len(consumed_ids),
        "consumed_document_ids_sha256": hashlib.sha256(_json_bytes(consumed_ids)).hexdigest(),
        "corpus_cycling": False,
        "streaming_writer": True,
    }
