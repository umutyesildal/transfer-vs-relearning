"""
Main pipeline script for the synthetic fact generation process.

This script orchestrates the entire workflow:
1. Sets up logging and random seed for reproducibility.
2. Loads and validates the canonical fact table from a CSV file.
3. Generates English training data (.jsonl).
4. Generates Turkish repetition data for Branch B facts (.jsonl).
5. Generates English and Turkish probe questions (.csv).
6. Exports all generated data to the 'output/' directory.
"""
import random
import logging

import config
from load_facts import load_and_validate_facts
from generate_training import (
    generate_english_training_data,
    generate_turkish_repetition_data,
)
from generate_probes import generate_probes
from export_utils import export_to_jsonl, export_to_csv

def main():
    """
    Runs the full synthetic fact generation pipeline.
    """
    # 1. Setup
    config.setup_logging()
    random.seed(config.RANDOM_SEED)
    logging.info("--- Starting Synthetic Fact Generation Pipeline ---")
    logging.info(f"Random seed set to {config.RANDOM_SEED}")

    try:
        # 2. Load and Validate Data
        facts_df = load_and_validate_facts(config.INPUT_CSV_PATH)

        # 3. Generate Training Data
        english_training_data = generate_english_training_data(facts_df)
        turkish_repetition_data = generate_turkish_repetition_data(facts_df)

        # 4. Generate Probes
        probes_en_df = generate_probes(facts_df, language="en")
        probes_tr_df = generate_probes(facts_df, language="tr")

        # 5. Export All Outputs
        logging.info("--- Exporting all generated files ---")
        export_to_jsonl(english_training_data, config.ENGLISH_TRAINING_OUTPUT_PATH)
        export_to_jsonl(turkish_repetition_data, config.TURKISH_REPETITION_OUTPUT_PATH)
        export_to_csv(probes_en_df, config.PROBES_EN_OUTPUT_PATH)
        export_to_csv(probes_tr_df, config.PROBES_TR_OUTPUT_PATH)

        logging.info("--- Pipeline finished successfully! ---")

    except FileNotFoundError as e:
        logging.error(f"Pipeline failed: {e}")
        logging.error("Please ensure the input file exists at the path specified in config.py.")
    except ValueError as e:
        logging.error(f"Pipeline failed due to a data validation error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
