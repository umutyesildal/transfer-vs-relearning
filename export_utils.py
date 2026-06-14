"""
Utility functions for exporting generated data to files.
"""
import pandas as pd
import json
import logging
from pathlib import Path

def ensure_output_dir_exists(filepath: str):
    """Ensures the output directory for a given filepath exists."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

def export_to_jsonl(data: list[dict], output_path: str):
    """
    Exports a list of dictionaries to a .jsonl file.
    Each dictionary is written as a JSON object on a new line.
    """
    if not data:
        logging.warning(f"No data to export to {output_path}. File will not be created.")
        return

    ensure_output_dir_exists(output_path)
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for record in data:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        logging.info(f"Successfully exported {len(data)} records to {output_path}")
    except IOError as e:
        logging.error(f"Failed to write to {output_path}: {e}")
        raise

def export_to_csv(df: pd.DataFrame, output_path: str):
    """
    Exports a pandas DataFrame to a .csv file.
    """
    if df.empty:
        logging.warning(f"DataFrame is empty. No data to export to {output_path}. File will not be created.")
        return

    ensure_output_dir_exists(output_path)
    
    try:
        df.to_csv(output_path, index=False, encoding="utf-8")
        logging.info(f"Successfully exported {len(df)} records to {output_path}")
    except IOError as e:
        logging.error(f"Failed to write to {output_path}: {e}")
        raise
