from __future__ import annotations

from pathlib import Path

DATASET_FILES = {
    "canonical_profiles": Path("data/canonical_subject_profiles_5000.csv"),
    "english_training": Path("output/english_training.jsonl"),
    "turkish_repetition": Path("output/turkish_repetition.jsonl"),
    "probes_en": Path("output/probes_en.csv"),
    "probes_tr": Path("output/probes_tr.csv"),
    "generation_summary": Path("output/canonical_generation_summary.json"),
    "source_validation_report": Path("output/source_validation_report.json"),
}

OPTIONAL_DATASET_FILES = {
    "english_biographies": Path("output/english_biographies.jsonl"),
    "english_qa_train": Path("output/english_qa_train.jsonl"),
    "english_training_m1_bio_qa": Path("output/english_training_m1_bio_qa.jsonl"),
    "english_training_m1_bio_qa_summary": Path("output/english_training_m1_bio_qa_summary.json"),
}

RELATIONS = ("profession", "born_in", "lives_in", "studied_at", "works_at")

CANONICAL_COLUMNS = (
    "row_id",
    "subject_id",
    "subject",
    "profession_en",
    "profession_tr",
    "birthplace_en",
    "birthplace_tr",
    "residence_en",
    "residence_tr",
    "university_en",
    "university_tr",
    "employer_en",
    "employer_tr",
    "name_type",
    "name_rarity_bucket",
    "popularity_rank",
    "popularity_bucket",
    "profession_frequency_bucket",
    "birthplace_frequency_bucket",
    "residence_frequency_bucket",
    "university_frequency_bucket",
    "employer_frequency_bucket",
    "branch_group",
)

PROBE_COLUMNS = (
    "fact_id",
    "row_id",
    "subject_id",
    "language",
    "relation",
    "subject",
    "question",
    "expected_answer",
    "name_type",
    "name_rarity_bucket",
    "popularity_rank",
    "popularity_bucket",
    "frequency_bucket",
    "branch_group",
    "template_id",
)

TRAINING_COLUMNS = (
    "fact_id",
    "row_id",
    "subject_id",
    "language",
    "split",
    "text",
    "relation",
    "subject",
    "answer",
    "name_type",
    "name_rarity_bucket",
    "popularity_rank",
    "popularity_bucket",
    "frequency_bucket",
    "branch_group",
    "template_id",
)

RELATION_MAP = {
    "profession": ("profession_en", "profession_tr", "profession_frequency_bucket"),
    "born_in": ("birthplace_en", "birthplace_tr", "birthplace_frequency_bucket"),
    "lives_in": ("residence_en", "residence_tr", "residence_frequency_bucket"),
    "studied_at": ("university_en", "university_tr", "university_frequency_bucket"),
    "works_at": ("employer_en", "employer_tr", "employer_frequency_bucket"),
}

VALID_NAME_TYPES = {"english_like", "turkish_like"}
VALID_RARITY = {"common", "medium", "rare"}
VALID_POPULARITY = {"high", "medium", "low"}
VALID_FREQUENCY = {"high", "medium", "low"}
VALID_BRANCHES = {"A", "B"}
