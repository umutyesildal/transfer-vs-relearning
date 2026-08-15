"""
Handles loading and initial validation of the canonical fact table.
"""
import pandas as pd
import logging
from pathlib import Path

from validators import run_all_validators
from config import RELATION_SPECS

FACT_METADATA_COLUMNS = [
    "row_id",
    "subject_id",
    "subject",
    "name_type",
    "name_rarity_bucket",
    "popularity_rank",
    "popularity_bucket",
    "branch_group",
]

def expand_subject_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expands one subject-profile row into one internal fact row per relation.
    """
    fact_records = []

    for _, row in df.iterrows():
        for relation, spec in RELATION_SPECS.items():
            record = {col: row[col] for col in FACT_METADATA_COLUMNS}
            record.update({
                "fact_id": f"{row['subject_id']}_{relation}",
                "relation": relation,
                "object_en": row[spec["object_en"]],
                "object_tr": row[spec["object_tr"]],
                "frequency_bucket": row[spec["frequency_bucket"]],
            })
            fact_records.append(record)

    return pd.DataFrame(fact_records)

def load_and_validate_facts(csv_path: str) -> pd.DataFrame:
    """
    Loads facts from a CSV file and runs a series of validations.

    Args:
        csv_path: The path to the input CSV file.

    Returns:
        A pandas DataFrame containing the validated facts.
        
    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the data fails validation checks.
    """
    input_path = Path(csv_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found at: {csv_path}")

    logging.info(f"Loading canonical facts from {csv_path}...")
    try:
        df = pd.read_csv(input_path, dtype={
            "row_id": str,
            "subject_id": str,
            "popularity_rank": str,
        })
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        raise

    # Run all validation steps and expand subject profiles into internal facts.
    validated_df = run_all_validators(df)
    facts_df = expand_subject_profiles(validated_df)
    
    logging.info(f"Successfully loaded {len(validated_df)} subject profiles and expanded them into {len(facts_df)} facts.")
    return facts_df
