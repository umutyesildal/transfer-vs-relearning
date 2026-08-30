from __future__ import annotations

from collections import Counter
import hashlib
from typing import Any, Iterable

from transfer_vs_relearning.data.candidates import (
    RELATION_TO_FAMILY,
    build_candidate_inventories,
    candidate_for_fact,
)
from transfer_vs_relearning.data.constants import RELATION_MAP
from transfer_vs_relearning.data.m1_form_generalization import FORM_IDS, FORM_TEMPLATES
from transfer_vs_relearning.data.pre_m2_followup import RELATIONS, SCAFFOLDS as ENGLISH_SCAFFOLDS


VERSION = "qwen_pre_m2_2500_v1"
DIRECTIONS = (
    ("en_to_en", "en", "en"),
    ("tr_to_en", "tr", "en"),
    ("tr_to_tr", "tr", "tr"),
)
TURKISH_SCAFFOLDS = {
    "direct": "{question}",
    "qa": "Soru: {question}\nCevap:",
}
TURKISH_FORM_TEMPLATES: dict[str, dict[str, str]] = {
    "profession": {
        "form_a": "{subject} hangi mesleği yapıyor?",
        "form_b": "{subject} profesyonel olarak hangi işte çalışıyor?",
        "form_c": "{subject} için belirtilen meslek nedir?",
        "form_d": "{subject} ne iş yapıyor?",
    },
    "born_in": {
        "form_a": "{subject} hangi şehirde doğdu?",
        "form_b": "{subject} adlı kişinin doğum yeri olarak hangi şehir belirtilmiştir?",
        "form_c": "{subject} adlı kişinin doğduğu şehir hangisidir?",
        "form_d": "{subject} hangi şehirde dünyaya geldi?",
    },
    "lives_in": {
        "form_a": "{subject} şu anda hangi şehirde ikamet ediyor?",
        "form_b": "{subject} adlı kişinin mevcut ikamet yeri olarak hangi şehir belirtilmiştir?",
        "form_c": "{subject} adlı kişinin şu an yaşadığı şehir hangisidir?",
        "form_d": "{subject} hangi şehirde yaşıyor?",
    },
    "field_of_study": {
        "form_a": "{subject} hangi akademik alanda eğitim aldı?",
        "form_b": "{subject} adlı kişinin eğitim alanı olarak hangi disiplin belirtilmiştir?",
        "form_c": "{subject} için kaydedilen eğitim alanı nedir?",
        "form_d": "{subject} ne okudu?",
    },
    "works_in_industry": {
        "form_a": "{subject} hangi sektörde çalışıyor?",
        "form_b": "{subject} adlı kişinin çalıştığı sektör olarak hangisi belirtilmiştir?",
        "form_c": "{subject} için kaydedilen istihdam sektörü hangisidir?",
        "form_d": "{subject} hangi endüstride çalışıyor?",
    },
}
TURKISH_FACT_TEMPLATES = {
    "profession": "{subject}, {answer} olarak çalışır.",
    "born_in": "{subject}, {answer} şehrinde doğdu.",
    "lives_in": "{subject}, {answer} şehrinde yaşıyor.",
    "field_of_study": "{subject}, {answer} alanında eğitim aldı.",
    "works_in_industry": "{subject}, {answer} sektöründe çalışıyor.",
}


def selected_profiles(
    canonical_rows: list[dict[str, str]], selected_subject_ids: set[str]
) -> list[dict[str, str]]:
    profiles = sorted(
        (row for row in canonical_rows if row["subject_id"] in selected_subject_ids),
        key=lambda row: row["subject_id"],
    )
    if len(profiles) != len(selected_subject_ids):
        found = {row["subject_id"] for row in profiles}
        raise ValueError(f"Missing selected subjects: {sorted(selected_subject_ids - found)}")
    return profiles


def validate_intermediate_population(profiles: list[dict[str, str]]) -> dict[str, Any]:
    return validate_balanced_population(profiles, expected_subjects=500)


def validate_balanced_population(
    profiles: list[dict[str, str]], *, expected_subjects: int
) -> dict[str, Any]:
    """Validate an even A/B Relation-V2 population at a precommitted scale."""

    if expected_subjects <= 0 or expected_subjects % 2:
        raise ValueError("Expected subject count must be a positive even integer")
    branch_counts = Counter(row["branch_group"] for row in profiles)
    expected_per_branch = expected_subjects // 2
    if len(profiles) != expected_subjects:
        raise ValueError(f"Expected {expected_subjects} subjects, found {len(profiles)}")
    if branch_counts != Counter({"A": expected_per_branch, "B": expected_per_branch}):
        raise ValueError(
            f"Expected {expected_per_branch}/{expected_per_branch} branch balance, "
            f"found {dict(branch_counts)}"
        )
    return {
        "subjects": len(profiles),
        "facts": len(profiles) * len(RELATIONS),
        "branch_subjects": dict(sorted(branch_counts.items())),
        "branch_facts": {
            branch: count * len(RELATIONS) for branch, count in sorted(branch_counts.items())
        },
    }


def build_bilingual_hard_probes(
    canonical_rows: list[dict[str, str]], selected_subject_ids: set[str]
) -> list[dict[str, Any]]:
    profiles = selected_profiles(canonical_rows, selected_subject_ids)
    validate_intermediate_population(profiles)
    inventories = build_candidate_inventories(canonical_rows)
    probes: list[dict[str, Any]] = []
    for profile in profiles:
        for relation in RELATIONS:
            en_column, tr_column, frequency_column = RELATION_MAP[relation]
            correct = candidate_for_fact(profile, relation, inventories)
            for direction, prompt_language, answer_language in DIRECTIONS:
                form_templates = (
                    FORM_TEMPLATES if prompt_language == "en" else TURKISH_FORM_TEMPLATES
                )
                scaffolds = (
                    ENGLISH_SCAFFOLDS if prompt_language == "en" else TURKISH_SCAFFOLDS
                )
                for form_id in FORM_IDS:
                    question = form_templates[relation][form_id].format(
                        subject=profile["subject"]
                    )
                    for scaffold_id, scaffold in scaffolds.items():
                        probes.append(
                            {
                                "probe_id": (
                                    f"{profile['subject_id']}_{relation}_{direction}_"
                                    f"{form_id}_{scaffold_id}"
                                ),
                                "fact_id": f"{profile['subject_id']}_{relation}",
                                "subject_id": profile["subject_id"],
                                "subject": profile["subject"],
                                "relation": relation,
                                "direction": direction,
                                "prompt_language": prompt_language,
                                "answer_language": answer_language,
                                "form_id": form_id,
                                "scaffold_id": scaffold_id,
                                "question": question,
                                "rendered_prompt": scaffold.format(question=question),
                                "expected_answer": profile[
                                    en_column if answer_language == "en" else tr_column
                                ],
                                "correct_object_id": correct.object_id,
                                "candidate_family": RELATION_TO_FAMILY[relation],
                                "branch_group": profile["branch_group"],
                                "frequency_bucket": profile[frequency_column],
                                "name_type": profile["name_type"],
                                "name_rarity_bucket": profile["name_rarity_bucket"],
                                "popularity_bucket": profile["popularity_bucket"],
                                "template_id": (
                                    f"{VERSION}_{relation}_{direction}_{form_id}_{scaffold_id}"
                                ),
                            }
                        )
    expected = len(profiles) * len(RELATIONS) * len(DIRECTIONS) * len(FORM_IDS) * 2
    probe_ids = [row["probe_id"] for row in probes]
    if len(probes) != expected or len(probe_ids) != len(set(probe_ids)):
        raise ValueError("Bilingual hard-probe registry has an unexpected count or duplicate IDs")
    return probes


def build_m3_branch_b_fact_registry(
    canonical_rows: list[dict[str, str]], selected_subject_ids: set[str]
) -> list[dict[str, Any]]:
    return build_branch_b_fact_registry(
        canonical_rows,
        selected_subject_ids,
        expected_subjects=500,
        version=VERSION,
    )


def build_branch_b_fact_registry(
    canonical_rows: list[dict[str, str]],
    selected_subject_ids: set[str],
    *,
    expected_subjects: int,
    version: str,
) -> list[dict[str, Any]]:
    """Build canonical Turkish statements for only the selected Branch-B facts."""

    profiles = selected_profiles(canonical_rows, selected_subject_ids)
    validation = validate_balanced_population(
        profiles, expected_subjects=expected_subjects
    )
    rows: list[dict[str, Any]] = []
    for profile in profiles:
        if profile["branch_group"] != "B":
            continue
        for relation in RELATIONS:
            _, tr_column, frequency_column = RELATION_MAP[relation]
            answer = profile[tr_column]
            rows.append(
                {
                    "fact_id": f"{profile['subject_id']}_{relation}",
                    "subject_id": profile["subject_id"],
                    "subject": profile["subject"],
                    "relation": relation,
                    "branch_group": "B",
                    "answer_tr": answer,
                    "text": TURKISH_FACT_TEMPLATES[relation].format(
                        subject=profile["subject"], answer=answer
                    ),
                    "frequency_bucket": profile[frequency_column],
                    "name_type": profile["name_type"],
                    "name_rarity_bucket": profile["name_rarity_bucket"],
                    "popularity_bucket": profile["popularity_bucket"],
                    "template_id": f"{version}_{relation}_canonical_fact_tr_v1",
                }
            )
    expected_facts = validation["branch_facts"]["B"]
    if len(rows) != expected_facts or len({row["fact_id"] for row in rows}) != expected_facts:
        raise ValueError(
            f"Branch-B registry must contain {expected_facts} unique Turkish facts"
        )
    return rows


def deterministic_document_order(
    rows: Iterable[dict[str, Any]], *, namespace: str, seed: int
) -> list[dict[str, Any]]:
    """Return one stable-document-ID order without relying on input file order."""

    materialized = [dict(row) for row in rows]
    ids = [str(row.get("stable_document_id", "")) for row in materialized]
    if not namespace or not ids or any(not value for value in ids):
        raise ValueError("Deterministic document order requires a namespace and non-empty IDs")
    if len(ids) != len(set(ids)):
        raise ValueError("Deterministic document order requires unique stable document IDs")
    return sorted(
        materialized,
        key=lambda row: (
            hashlib.sha256(
                f"{namespace}|{seed}|{row['stable_document_id']}".encode("utf-8")
            ).hexdigest(),
            str(row["stable_document_id"]),
        ),
    )


def materialize_generic_blocks(
    rows: Iterable[dict[str, Any]],
    tokenizer: Any,
    *,
    block_size: int,
    total_blocks: int,
) -> list[list[int]]:
    blocks, _ = materialize_generic_blocks_with_audit(
        rows,
        tokenizer,
        block_size=block_size,
        total_blocks=total_blocks,
    )
    return blocks


def materialize_generic_blocks_with_audit(
    rows: Iterable[dict[str, Any]],
    tokenizer: Any,
    *,
    block_size: int,
    total_blocks: int,
) -> tuple[list[list[int]], dict[str, Any]]:
    """Pack a deterministic document stream and expose the exact consumed prefix."""

    if block_size <= 0 or total_blocks <= 0:
        raise ValueError("Block size and total block count must be positive")
    if tokenizer.eos_token_id is None:
        raise ValueError("Tokenizer must define eos_token_id")
    required_tokens = block_size * total_blocks
    tokens: list[int] = []
    consumed_document_ids: list[str] = []
    for row in rows:
        text = str(row.get("text", "")).strip()
        if not text:
            raise ValueError("Generic Turkish row has no non-empty text")
        stable_document_id = str(row.get("stable_document_id", ""))
        if stable_document_id:
            consumed_document_ids.append(stable_document_id)
        tokens.extend(tokenizer.encode(text, add_special_tokens=False))
        tokens.append(int(tokenizer.eos_token_id))
        if len(tokens) >= required_tokens:
            break
    if len(tokens) < required_tokens:
        raise ValueError(
            f"Generic Turkish source has {len(tokens)} tokens; {required_tokens} required"
        )
    observed_tokens = len(tokens)
    packed_tokens = tokens[:required_tokens]
    blocks = [
        packed_tokens[start : start + block_size]
        for start in range(0, required_tokens, block_size)
    ]
    return blocks, {
        "schema_version": 1,
        "block_size": block_size,
        "total_blocks": total_blocks,
        "required_tokens": required_tokens,
        "source_tokens_observed_through_last_document": observed_tokens,
        "discarded_tail_tokens": observed_tokens - required_tokens,
        "consumed_documents": len(consumed_document_ids),
        "consumed_document_ids_sha256": hashlib.sha256(
            json_bytes(consumed_document_ids)
        ).hexdigest(),
        "corpus_cycling": False,
    }


def json_bytes(value: Any) -> bytes:
    """Canonical compact JSON bytes used for local materialization digests."""

    import json

    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def build_matched_m2_m3_blocks(
    generic_blocks: list[list[int]],
    factual_rows: list[dict[str, Any]],
    tokenizer: Any,
    *,
    fact_cycles: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if not generic_blocks or fact_cycles <= 0:
        raise ValueError("Generic blocks and fact cycles must be positive")
    block_size = len(generic_blocks[0])
    if block_size <= 0 or any(len(block) != block_size for block in generic_blocks):
        raise ValueError("All generic blocks must have the same positive length")
    if not factual_rows or len({str(row["fact_id"]) for row in factual_rows}) != len(factual_rows):
        raise ValueError("Factual registry must contain unique fact IDs")
    if {str(row.get("branch_group")) for row in factual_rows} != {"B"}:
        raise ValueError("M3 factual registry must contain Branch B only")
    if tokenizer.eos_token_id is None:
        raise ValueError("Tokenizer must define eos_token_id")

    scheduled: list[tuple[str, list[int]]] = []
    for _ in range(fact_cycles):
        for row in factual_rows:
            text = str(row.get("text", "")).strip()
            if not text:
                raise ValueError(f"Factual row {row['fact_id']} has no text")
            ids = list(tokenizer.encode(text, add_special_tokens=False))
            ids.append(int(tokenizer.eos_token_id))
            if len(ids) > block_size:
                raise ValueError(f"Factual row {row['fact_id']} exceeds one block")
            scheduled.append((str(row["fact_id"]), ids))

    packed: list[tuple[list[int], list[str]]] = []
    current_ids: list[int] = []
    current_facts: list[str] = []
    for fact_id, ids in scheduled:
        if current_ids and len(current_ids) + len(ids) > block_size:
            packed.append((current_ids, current_facts))
            current_ids, current_facts = [], []
        current_ids.extend(ids)
        current_facts.append(fact_id)
    if current_ids:
        packed.append((current_ids, current_facts))
    if len(packed) > len(generic_blocks):
        raise ValueError(
            f"Factual dose requires {len(packed)} blocks but family has only {len(generic_blocks)}"
        )

    replacement_indices = [
        ((2 * index + 1) * len(generic_blocks)) // (2 * len(packed))
        for index in range(len(packed))
    ]
    if len(replacement_indices) != len(set(replacement_indices)):
        raise AssertionError("Deterministic replacement indices are not unique")

    m2_blocks = [list(block) for block in generic_blocks]
    m3_blocks = [list(block) for block in generic_blocks]
    replacement_manifest: list[dict[str, Any]] = []
    factual_token_count = 0
    for block_index, (fact_tokens, fact_ids) in zip(replacement_indices, packed, strict=True):
        factual_token_count += len(fact_tokens)
        m3_blocks[block_index] = fact_tokens + generic_blocks[block_index][len(fact_tokens) :]
        replacement_manifest.append(
            {
                "block_index": block_index,
                "factual_tokens": len(fact_tokens),
                "generic_tail_tokens": block_size - len(fact_tokens),
                "fact_ids": fact_ids,
            }
        )

    def rows_for(blocks: list[list[int]], arm: str) -> list[dict[str, Any]]:
        return [
            {
                "block_index": index,
                "arm": arm,
                "input_ids": block,
                "attention_mask": [1] * block_size,
            }
            for index, block in enumerate(blocks)
        ]

    total_tokens = len(generic_blocks) * block_size
    audit = {
        "block_size": block_size,
        "total_blocks_per_arm": len(generic_blocks),
        "total_tokens_per_arm": total_tokens,
        "fact_cycles": fact_cycles,
        "unique_branch_b_facts": len(factual_rows),
        "scheduled_fact_exposures": len(scheduled),
        "factual_tokens": factual_token_count,
        "factual_token_share": factual_token_count / total_tokens,
        "replacement_block_count": len(packed),
        "replacement_blocks": replacement_manifest,
        "m2_m3_block_count_equal": len(m2_blocks) == len(m3_blocks),
        "m2_m3_token_budget_equal": sum(map(len, m2_blocks)) == sum(map(len, m3_blocks)),
        "branch_a_fact_exposures": 0,
    }
    return rows_for(m2_blocks, "m2_clean"), rows_for(m3_blocks, "m3_fact"), audit


def build_fixed_replacement_m2_blocks(
    generic_blocks: list[list[int]],
    factual_rows: list[dict[str, Any]],
    tokenizer: Any,
    *,
    replacement_block_count: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Build exactly matched M2-A/M2-B blocks at a fixed factual replacement dose."""

    if not generic_blocks or replacement_block_count <= 0:
        raise ValueError("Generic blocks and replacement block count must be positive")
    if replacement_block_count >= len(generic_blocks):
        raise ValueError("Factual replacement must leave at least one generic-only block")
    block_size = len(generic_blocks[0])
    if block_size <= 0 or any(len(block) != block_size for block in generic_blocks):
        raise ValueError("All generic blocks must have the same positive length")
    fact_ids = [str(row.get("fact_id", "")) for row in factual_rows]
    if not fact_ids or any(not value for value in fact_ids) or len(fact_ids) != len(set(fact_ids)):
        raise ValueError("Factual registry must contain unique non-empty fact IDs")
    if {str(row.get("branch_group")) for row in factual_rows} != {"B"}:
        raise ValueError("Factual registry must contain Branch B only")
    if tokenizer.eos_token_id is None:
        raise ValueError("Tokenizer must define eos_token_id")

    encoded_facts: list[tuple[str, list[int]]] = []
    relation_by_fact: dict[str, str] = {}
    for row in sorted(factual_rows, key=lambda value: str(value["fact_id"])):
        text = str(row.get("text", "")).strip()
        if not text:
            raise ValueError(f"Factual row {row['fact_id']} has no text")
        tokens = list(tokenizer.encode(text, add_special_tokens=False))
        tokens.append(int(tokenizer.eos_token_id))
        if not tokens or len(tokens) > block_size:
            raise ValueError(f"Factual row {row['fact_id']} exceeds one block")
        fact_id = str(row["fact_id"])
        encoded_facts.append((fact_id, tokens))
        relation_by_fact[fact_id] = str(row.get("relation", "unknown"))

    packed: list[tuple[list[int], list[str]]] = []
    exposure_counts: Counter[str] = Counter(
        {fact_id: 0 for fact_id, _ in encoded_facts}
    )
    fact_cursor = 0
    for _ in range(replacement_block_count):
        block_tokens: list[int] = []
        block_facts: list[str] = []
        while True:
            fact_id, fact_tokens = encoded_facts[fact_cursor % len(encoded_facts)]
            if block_tokens and len(block_tokens) + len(fact_tokens) > block_size:
                break
            block_tokens.extend(fact_tokens)
            block_facts.append(fact_id)
            exposure_counts[fact_id] += 1
            fact_cursor += 1
            if len(block_tokens) == block_size:
                break
        if not block_tokens:
            raise AssertionError("A factual replacement block cannot be empty")
        packed.append((block_tokens, block_facts))

    replacement_indices = [
        ((2 * index + 1) * len(generic_blocks)) // (2 * replacement_block_count)
        for index in range(replacement_block_count)
    ]
    if len(replacement_indices) != len(set(replacement_indices)):
        raise AssertionError("Deterministic replacement indices are not unique")

    m2_a_blocks = [list(block) for block in generic_blocks]
    m2_b_blocks = [list(block) for block in generic_blocks]
    replacement_manifest: list[dict[str, Any]] = []
    factual_tokens = 0
    for block_index, (fact_tokens, packed_fact_ids) in zip(
        replacement_indices, packed, strict=True
    ):
        factual_tokens += len(fact_tokens)
        m2_b_blocks[block_index] = (
            fact_tokens + generic_blocks[block_index][len(fact_tokens) :]
        )
        replacement_manifest.append(
            {
                "block_index": block_index,
                "factual_tokens": len(fact_tokens),
                "generic_tail_tokens": block_size - len(fact_tokens),
                "fact_ids": packed_fact_ids,
            }
        )

    def rows_for(blocks: list[list[int]], arm: str) -> list[dict[str, Any]]:
        return [
            {
                "block_index": index,
                "arm": arm,
                "input_ids": block,
                "attention_mask": [1] * block_size,
            }
            for index, block in enumerate(blocks)
        ]

    total_tokens = len(generic_blocks) * block_size
    exposure_values = list(exposure_counts.values())
    relation_exposures: Counter[str] = Counter()
    for fact_id, count in exposure_counts.items():
        relation_exposures[relation_by_fact[fact_id]] += count
    relation_values = list(relation_exposures.values())
    audit = {
        "schema_version": 1,
        "block_size": block_size,
        "total_blocks_per_arm": len(generic_blocks),
        "total_tokens_per_arm": total_tokens,
        "unique_branch_b_facts": len(factual_rows),
        "scheduled_fact_exposures": sum(exposure_values),
        "fact_exposure_min": min(exposure_values),
        "fact_exposure_max": max(exposure_values),
        "fact_exposure_balance_max_minus_min": max(exposure_values) - min(exposure_values),
        "fact_exposures": dict(sorted(exposure_counts.items())),
        "relation_exposures": dict(sorted(relation_exposures.items())),
        "relation_exposure_balance_max_minus_min": (
            max(relation_values) - min(relation_values)
        ),
        "factual_tokens": factual_tokens,
        "factual_token_share": factual_tokens / total_tokens,
        "replacement_block_count": replacement_block_count,
        "replacement_blocks": replacement_manifest,
        "m2_a_m2_b_block_count_equal": len(m2_a_blocks) == len(m2_b_blocks),
        "m2_a_m2_b_token_budget_equal": (
            sum(map(len, m2_a_blocks)) == sum(map(len, m2_b_blocks))
        ),
        "branch_a_fact_exposures": 0,
        "extra_tokens_over_m2_a": 0,
    }
    if audit["fact_exposure_balance_max_minus_min"] > 1:
        raise AssertionError("Complete-cycle factual scheduling must differ by at most one exposure")
    if audit["relation_exposure_balance_max_minus_min"] > 1:
        raise AssertionError("Relation exposure totals must differ by at most one exposure")
    return rows_for(m2_a_blocks, "M2-A"), rows_for(m2_b_blocks, "M2-B"), audit
