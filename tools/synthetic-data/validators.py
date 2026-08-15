"""
Data validation functions for the fact generation pipeline.
"""
import pandas as pd
import logging

from config import (
    REQUIRED_COLUMNS,
    ALLOWED_NAME_TYPES,
    ALLOWED_NAME_RARITY_BUCKETS,
    ALLOWED_POPULARITY_BUCKETS,
    ALLOWED_FREQUENCY_BUCKETS,
    ALLOWED_BRANCH_GROUPS,
    RELATION_SPECS,
)

def validate_columns(df: pd.DataFrame):
    """
    Validates that the DataFrame contains all required columns.
    Raises a ValueError if any columns are missing.
    """
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in input data: {missing_cols}")
    logging.info("Column validation passed: All required columns are present.")

def validate_unique_values(df: pd.DataFrame):
    """Validates that row_id, subject_id, and subject are unique."""
    for col in ["row_id", "subject_id", "subject"]:
        duplicates = df[df[col].duplicated()][col].unique().tolist()
        if duplicates:
            raise ValueError(f"Duplicate values found in column '{col}': {duplicates}")
    logging.info("Uniqueness validation passed for row_id, subject_id, and subject.")

def validate_field_values(df: pd.DataFrame):
    """
    Validates that specific fields contain only allowed values.
    
    This function checks all categorical subject-profile fields.

    Raises a ValueError if any invalid values are found.
    """
    validation_map = {
        "name_type": ALLOWED_NAME_TYPES,
        "name_rarity_bucket": ALLOWED_NAME_RARITY_BUCKETS,
        "popularity_bucket": ALLOWED_POPULARITY_BUCKETS,
        "branch_group": ALLOWED_BRANCH_GROUPS,
    }
    for spec in RELATION_SPECS.values():
        validation_map[spec["frequency_bucket"]] = ALLOWED_FREQUENCY_BUCKETS

    for col, allowed_values in validation_map.items():
        invalid_values = df[~df[col].isin(allowed_values)]
        if not invalid_values.empty:
            raise ValueError(
                f"Invalid values found in column '{col}': "
                f"{invalid_values[col].unique().tolist()}. "
                f"Allowed values are: {allowed_values}"
            )
    logging.info("Categorical field validation passed.")

def validate_non_empty_objects(df: pd.DataFrame):
    """Validates that every relation has non-empty English and Turkish object values."""
    object_columns = []
    for spec in RELATION_SPECS.values():
        object_columns.extend([spec["object_en"], spec["object_tr"]])

    for col in object_columns:
        empty_values = df[col].isna() | (df[col].astype(str).str.strip() == "")
        if empty_values.any():
            row_ids = df.loc[empty_values, "row_id"].tolist()
            raise ValueError(f"Empty values found in column '{col}' for row_id values: {row_ids}")
    logging.info("Non-empty object validation passed.")

def run_all_validators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs all validation functions in sequence on the given DataFrame.
    
    Returns a fully validated DataFrame.
    """
    logging.info("Starting data validation process...")
    validate_columns(df)
    validate_unique_values(df)
    validate_field_values(df)
    validate_non_empty_objects(df)
    logging.info("Data validation process completed successfully.")
    return df.copy()
