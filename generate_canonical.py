"""
Command-line entry point for canonical subject-profile generation.
"""
import argparse
import logging

import config
from canonical_profile_generator import generate_canonical_profiles, validate_pipeline_outputs
from export_utils import export_to_csv, export_to_jsonl
from generate_probes import generate_probes
from generate_training import generate_english_training_data, generate_turkish_repetition_data
from load_facts import load_and_validate_facts


def run_existing_pipeline():
    """Runs the existing training/probe generation pipeline."""
    facts_df = load_and_validate_facts(config.CANONICAL_OUTPUT_PATH)
    english_training_data = generate_english_training_data(facts_df)
    turkish_repetition_data = generate_turkish_repetition_data(facts_df)
    probes_en_df = generate_probes(facts_df, language="en")
    probes_tr_df = generate_probes(facts_df, language="tr")

    export_to_jsonl(english_training_data, config.ENGLISH_TRAINING_OUTPUT_PATH)
    export_to_jsonl(turkish_repetition_data, config.TURKISH_REPETITION_OUTPUT_PATH)
    export_to_csv(probes_en_df, config.PROBES_EN_OUTPUT_PATH)
    export_to_csv(probes_tr_df, config.PROBES_TR_OUTPUT_PATH)


def print_summary(summary: dict, output_validation: dict | None = None):
    """Prints a readable generation summary."""
    print("Canonical generation complete")
    print(f"Seed: {summary['random_seed']}")
    print(f"Subjects: {summary['generated_subject_count']}")
    print(f"Expected facts: {summary['expected_fact_count']}")
    print(f"Name types: english_like={summary['english_like_subject_count']}, turkish_like={summary['turkish_like_subject_count']}")
    print(f"Name rarity: {summary['name_rarity_distribution']}")
    print(f"Popularity buckets: {summary['popularity_bucket_distribution']}")
    print(f"Branches: {summary['branch_distribution']}")
    print(f"Frequency overall: {summary['frequency_distribution_overall']}")
    print(f"Profession/employer compatibility: {summary['profession_employer_compatibility']}")
    if output_validation:
        print(f"Output rows: {output_validation}")
    if summary["warnings"]:
        print(f"Warnings: {summary['warnings']}")


def main():
    parser = argparse.ArgumentParser(description="Generate the canonical subject-profile CSV.")
    parser.add_argument("--run-pipeline", action="store_true", help="Run and validate the existing pipeline after canonical generation.")
    args = parser.parse_args()

    config.setup_logging()
    logging.info("--- Starting Canonical Subject Profile Generation ---")
    summary = generate_canonical_profiles()
    output_validation = None
    if args.run_pipeline:
        logging.info("--- Running Existing Pipeline From Generated Canonical CSV ---")
        run_existing_pipeline()
        output_validation = validate_pipeline_outputs(summary)
    print_summary(summary, output_validation)


if __name__ == "__main__":
    main()
