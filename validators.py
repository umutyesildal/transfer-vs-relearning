"""
Data validation functions for the fact generation pipeline.
"""
import pandas as pd
import logging

from config import (
    REQUIRED_COLUMNS,
    ALLOWED_RELATIONS,
    ALLOWED_NAME_TYPES,
    ALLOWED_FREQUENCY_BUCKETS,
    ALLOWED_BRANCH_GROUPS,
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

def validate_relations(df: pd.DataFrame):
    """
    Validates that the 'relation' column contains only allowed values.
    Logs a warning for any invalid relations found.
    Returns a cleaned DataFrame containing only rows with valid relations.
    """
    invalid_relations = df[~df["relation"].isin(ALLOWED_RELATIONS)]
    if not invalid_relations.empty:
        logging.warning(
            f"Found {len(invalid_relations)} rows with invalid relations. "
            f"These rows will be skipped. Invalid relations: "
            f"{invalid_relations['relation'].unique().tolist()}"
        )
    
    valid_df = df[df["relation"].isin(ALLOWED_RELATIONS)].copy()
    logging.info("Relation validation passed.")
    return valid_df

def validate_field_values(df: pd.DataFrame):
    """
    Validates that specific fields contain only allowed values.
    
    This function checks:
    - 'name_type'
    - 'frequency_bucket'
    - 'branch_group'
    
    Raises a ValueError if any invalid values are found.
    """
    validation_map = {
        "name_type": ALLOWED_NAME_TYPES,
        "frequency_bucket": ALLOWED_FREQUENCY_BUCKETS,
        "branch_group": ALLOWED_BRANCH_GROUPS,
    }

    for col, allowed_values in validation_map.items():
        invalid_values = df[~df[col].isin(allowed_values)]
        if not invalid_values.empty:
            raise ValueError(
                f"Invalid values found in column '{col}': "
                f"{invalid_values[col].unique().tolist()}. "
                f"Allowed values are: {allowed_values}"
            )
    logging.info("Field value validation passed for name_type, frequency_bucket, and branch_group.")

def run_all_validators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs all validation functions in sequence on the given DataFrame.
    
    Returns a fully validated and cleaned DataFrame.
    """
    logging.info("Starting data validation process...")
    validate_columns(df)
    validate_field_values(df)
    validated_df = validate_relations(df)
    logging.info("Data validation process completed successfully.")
    return validated_df
