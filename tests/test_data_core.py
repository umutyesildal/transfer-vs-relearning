from __future__ import annotations

from pathlib import Path

import pytest

from transfer_vs_relearning.data.candidates import (
    RELATION_TO_FAMILY,
    build_candidate_inventories,
    resolve_expected_answer,
    stable_object_id,
)
from transfer_vs_relearning.data.constants import DATASET_FILES, OPTIONAL_DATASET_FILES, RELATIONS
from transfer_vs_relearning.data.facts import expand_canonical_row, expand_canonical_rows
from transfer_vs_relearning.data.pilot import select_pilot_subjects
from transfer_vs_relearning.utils.io import sha256_file, write_csv, write_json
from transfer_vs_relearning.utils.text import normalize_text


def canonical_row(i: int, branch: str = "A", name_type: str = "english_like") -> dict[str, str]:
    rarity = ["common", "medium", "rare"][i % 3]
    popularity = ["high", "medium", "low"][i % 3]
    return {
        "row_id": f"R{i:05d}",
        "subject_id": f"S{i:05d}",
        "subject": f"Subject {i}",
        "profession_en": f"Profession {i % 4}",
        "profession_tr": f"Meslek {i % 4}",
        "birthplace_en": f"City {i % 5}",
        "birthplace_tr": f"Şehir {i % 5}",
        "residence_en": f"City {(i + 1) % 5}",
        "residence_tr": f"Şehir {(i + 1) % 5}",
        "university_en": f"University {i % 3}",
        "university_tr": f"Üniversite {i % 3}",
        "employer_en": f"Employer {i % 6}",
        "employer_tr": f"İşveren {i % 6}",
        "name_type": name_type,
        "name_rarity_bucket": rarity,
        "popularity_rank": str(i),
        "popularity_bucket": popularity,
        "profession_frequency_bucket": popularity,
        "birthplace_frequency_bucket": "low",
        "residence_frequency_bucket": "low",
        "university_frequency_bucket": rarity if rarity != "common" else "high",
        "employer_frequency_bucket": "medium",
        "branch_group": branch,
    }


def test_source_artifact_paths_include_data_and_output_locations() -> None:
    assert DATASET_FILES["canonical_profiles"] == Path("data/canonical_subject_profiles_5000.csv")
    assert DATASET_FILES["english_training"] == Path("output/english_training.jsonl")
    assert OPTIONAL_DATASET_FILES["english_biographies"] == Path("output/english_biographies.jsonl")
    assert OPTIONAL_DATASET_FILES["english_training_m1_bio_qa"] == Path("output/english_training_m1_bio_qa.jsonl")


def test_sha256_manifest_creation(tmp_path: Path) -> None:
    path = tmp_path / "artifact.txt"
    path.write_text("abc", encoding="utf-8")
    assert sha256_file(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_canonical_five_fact_expansion() -> None:
    facts = expand_canonical_row(canonical_row(1))
    assert [fact.relation for fact in facts] == list(RELATIONS)
    assert [fact.fact_id for fact in facts] == [f"S00001_{relation}" for relation in RELATIONS]


def test_exact_25000_fact_validation_logic_from_5000_rows() -> None:
    rows = [canonical_row(i, "A" if i <= 2500 else "B") for i in range(1, 5001)]
    facts = expand_canonical_rows(rows)
    assert len(facts) == 25000
    assert len({fact.fact_id for fact in facts}) == 25000


def test_stable_object_id_generation_is_deterministic() -> None:
    first = stable_object_id("city", "Istanbul", "İstanbul")
    second = stable_object_id("city", "Istanbul", "İstanbul")
    assert first == second
    assert first.startswith("city_istanbul_")


def test_unicode_city_normalization_matches_istanbul_variants() -> None:
    assert normalize_text("İstanbul") == normalize_text("Istanbul")
    assert normalize_text("McDonald’s") == normalize_text("McDonald's")


def test_candidate_inventory_deduplicates_and_shares_city_family() -> None:
    rows = [canonical_row(1), canonical_row(2)]
    inventories = build_candidate_inventories(rows)
    assert RELATION_TO_FAMILY["born_in"] == RELATION_TO_FAMILY["lives_in"] == "city"
    city_surfaces = {(c.object_en, c.object_tr) for c in inventories["city"]}
    assert ("City 1", "Şehir 1") in city_surfaces
    assert ("City 2", "Şehir 2") in city_surfaces


def test_expected_answer_resolution() -> None:
    rows = [canonical_row(1)]
    inventories = build_candidate_inventories(rows)
    candidate = resolve_expected_answer("profession", "en", "Profession 1", inventories)
    assert candidate.object_en == "Profession 1"


def test_pilot_selection_is_deterministic(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "synthetic_v1"
    rows = [
        canonical_row(i, branch="A" if i % 2 else "B", name_type="english_like" if i % 3 else "turkish_like")
        for i in range(1, 121)
    ]
    write_csv(dataset_dir / DATASET_FILES["canonical_profiles"], rows, list(rows[0]))
    write_json(dataset_dir / "manifest.json", {"ok": True})
    first = select_pilot_subjects(dataset_dir, subjects=20, seed=42)
    second = select_pilot_subjects(dataset_dir, subjects=20, seed=42)
    assert first["selected_subject_ids"] == second["selected_subject_ids"]
    assert first["distribution_summary"]["relation_counts"] == {relation: 20 for relation in RELATIONS}
    assert first["distribution_summary"]["branch_group"] == {"A": 10, "B": 10}
    assert first["distribution_summary"]["name_type"] == {"english_like": 10, "turkish_like": 10}
