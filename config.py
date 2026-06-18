"""
Configuration for the synthetic fact generation pipeline.
"""

import logging

# --- General Settings ---
RANDOM_SEED = 42

# --- Input/Output Files ---
INPUT_CSV_PATH = "data/canonical_subject_profiles_10.csv"
ENGLISH_TRAINING_OUTPUT_PATH = "output/english_training.jsonl"
TURKISH_REPETITION_OUTPUT_PATH = "output/turkish_repetition.jsonl"
PROBES_EN_OUTPUT_PATH = "output/probes_en.csv"
PROBES_TR_OUTPUT_PATH = "output/probes_tr.csv"

# --- Subject Profile Columns ---
# Defines the expected columns in the input CSV.
REQUIRED_COLUMNS = [
    "row_id",
    "subject_id",
    "subject",
    "profession_en",
    "profession_tr",
    "birthplace_en",
    "birthplace_tr",
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
    "university_frequency_bucket",
    "employer_frequency_bucket",
    "branch_group",
]

# --- Validation Rules ---
# Defines allowed values for specific columns to ensure data integrity.
ALLOWED_RELATIONS = ["profession", "born_in", "studied_at", "works_at"]
ALLOWED_NAME_TYPES = ["english_like", "turkish_like"]
ALLOWED_NAME_RARITY_BUCKETS = ["common", "medium", "rare"]
ALLOWED_POPULARITY_BUCKETS = ["low", "medium", "high"]
ALLOWED_FREQUENCY_BUCKETS = ["low", "medium", "high"]
ALLOWED_BRANCH_GROUPS = ["A", "B"]

# --- Relation Expansion ---
RELATION_SPECS = {
    "profession": {
        "object_en": "profession_en",
        "object_tr": "profession_tr",
        "frequency_bucket": "profession_frequency_bucket",
    },
    "born_in": {
        "object_en": "birthplace_en",
        "object_tr": "birthplace_tr",
        "frequency_bucket": "birthplace_frequency_bucket",
    },
    "studied_at": {
        "object_en": "university_en",
        "object_tr": "university_tr",
        "frequency_bucket": "university_frequency_bucket",
    },
    "works_at": {
        "object_en": "employer_en",
        "object_tr": "employer_tr",
        "frequency_bucket": "employer_frequency_bucket",
    },
}

# --- Frequency Logic ---
# Maps frequency buckets to the number of repetitions for English training data.
FREQUENCY_TO_REPETITION_COUNT = {
    "low": 3,
    "medium": 8,
    "high": 15,
}

# --- Logging Configuration ---
LOGGING_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

def setup_logging():
    """Configures the root logger for the application."""
    logging.basicConfig(level=LOGGING_LEVEL, format=LOG_FORMAT)
