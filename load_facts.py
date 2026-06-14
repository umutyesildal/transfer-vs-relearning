"""
Handles loading and initial validation of the canonical fact table.
"""
import pandas as pd
import logging
from pathlib import Path

from validators import run_all_validators

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
        df = pd.read_csv(input_path, dtype={"fact_id": str})
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        raise

    # Run all validation steps
    validated_df = run_all_validators(df)
    
    logging.info(f"Successfully loaded and validated {len(validated_df)} facts.")
    return validated_df
