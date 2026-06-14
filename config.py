"""
Configuration for the synthetic fact generation pipeline.
"""

import logging

# --- General Settings ---
RANDOM_SEED = 42

# --- Input/Output Files ---
INPUT_CSV_PATH = "data/canonical_facts_pilot.csv"
ENGLISH_TRAINING_OUTPUT_PATH = "output/english_training.jsonl"
TURKISH_REPETITION_OUTPUT_PATH = "output/turkish_repetition.jsonl"
PROBES_EN_OUTPUT_PATH = "output/probes_en.csv"
PROBES_TR_OUTPUT_PATH = "output/probes_tr.csv"

# --- Fact Table Columns ---
# Defines the expected columns in the input CSV.
REQUIRED_COLUMNS = [
    "fact_id",
    "subject",
    "relation",
    "object_en",
    "object_tr",
    "name_type",
    "frequency_bucket",
    "branch_group",
]

# --- Validation Rules ---
# Defines allowed values for specific columns to ensure data integrity.
ALLOWED_RELATIONS = ["profession", "born_in"]
ALLOWED_NAME_TYPES = ["english_like", "turkish_like"]
ALLOWED_FREQUENCY_BUCKETS = ["low", "medium", "high"]
ALLOWED_BRANCH_GROUPS = ["A", "B", "C"]

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
